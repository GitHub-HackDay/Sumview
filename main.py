from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, JSONResponse
import os
import tempfile
import aiofiles
import json
from pathlib import Path

from app.services.transcription import TranscriptionService
from app.services.summarization import SummarizationService
from app.services.test_generation import TestGenerationService
from app.services.weaviate_service import WeaviateService
from app.services.graphrag_service import GraphRAGService
from app.services.nlweb_service import NLWebService
from app.models.database import SessionLocal, engine
from app.models import models

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Meeting & Lecture Summarizer", version="1.0.0")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize services
transcription_service = TranscriptionService()
summarization_service = SummarizationService()
test_service = TestGenerationService()
weaviate_service = WeaviateService()
graphrag_service = GraphRAGService()
nlweb_service = NLWebService()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main page for file upload"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), db = Depends(get_db)):
    """Handle audio/video file upload and processing"""
    
    # Validate file type - be more flexible with MIME types
    allowed_extensions = ['.mp3', '.wav', '.mp4', '.avi', '.mov', '.mpeg', '.mpg', '.m4a', '.flac']
    allowed_mime_types = [
        'audio/mpeg', 'audio/wav', 'audio/mp4', 'audio/x-wav', 'audio/wave',
        'video/mp4', 'video/avi', 'video/mov', 'video/quicktime', 'video/x-msvideo',
        'video/mpeg', 'video/x-mpeg', 'application/octet-stream'
    ]
    
    # Check file extension
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file extension: {file_extension}. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Check MIME type (but be flexible since some browsers report different types)
    if file.content_type and file.content_type not in allowed_mime_types:
        # Only warn, don't reject - some valid files have unexpected MIME types
        print(f"Warning: Unexpected MIME type {file.content_type} for file {file.filename}")
    
    # Check file size (100MB limit)
    file_size = 0
    temp_content = await file.read()
    file_size = len(temp_content)
    
    if file_size > 100 * 1024 * 1024:  # 100MB
        raise HTTPException(status_code=400, detail="File size exceeds 100MB limit")
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(temp_content)
            temp_file_path = temp_file.name
        
        print(f"Processing file: {file.filename} (Type: {file.content_type}, Size: {file_size} bytes)")
        
        # Process the file
        result = await process_recording(temp_file_path, file.filename, db)
        
        # Clean up temp file
        os.unlink(temp_file_path)
        
        return JSONResponse(content=result)
        
    except Exception as e:
        # Clean up temp file if it exists
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        
        print(f"Processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

async def process_recording(file_path: str, filename: str, db):
    """Process audio/video recording through the complete pipeline with enhanced features"""
    
    # Step 1: Transcribe audio
    transcript = await transcription_service.transcribe(file_path)
    
    # Step 2: Generate summary and article
    summary_result = await summarization_service.generate_content(transcript)
    
    # Step 3: Generate comprehension test
    test_questions = await test_service.generate_test(transcript, summary_result['key_points'])
    
    # Step 4: Build knowledge graph (GraphRAG)
    key_points_list = json.loads(summary_result['key_points'])
    graph_result = await graphrag_service.build_knowledge_graph(
        recording_id=0,  # Temporary ID, will be updated after DB save
        transcript=transcript,
        summary=summary_result['summary'],
        key_points=key_points_list
    )
    
    # Step 5: Enhance with web research (nlweb)
    async with nlweb_service as nlweb:
        web_enhancement = await nlweb.enhance_content_with_web_research(
            transcript, key_points_list
        )
    
    # Step 6: Store to database
    from app.models.models import Recording
    recording = Recording(
        filename=filename,
        transcript=transcript,
        summary=summary_result['summary'],
        article=summary_result['article'],
        key_points=summary_result['key_points'],
        test_questions=test_questions
    )
    db.add(recording)
    db.commit()
    
    # Step 7: Store in Weaviate for semantic search
    await weaviate_service.store_recording_segments(recording.id, transcript)
    
    # Update graph with correct recording ID
    await graphrag_service.build_knowledge_graph(
        recording_id=recording.id,
        transcript=transcript,
        summary=summary_result['summary'],
        key_points=key_points_list
    )
    
    return {
        "id": recording.id,
        "filename": filename,
        "transcript": transcript,
        "summary": summary_result['summary'],
        "article": summary_result['article'],
        "key_points": summary_result['key_points'],
        "test_questions": test_questions,
        "enhanced_content": web_enhancement,
        "knowledge_graph": graph_result,
        "message": "Recording processed successfully with enhanced features"
    }

@app.get("/recording/{recording_id}")
async def get_recording(recording_id: int, db = Depends(get_db)):
    """Retrieve a processed recording by ID"""
    from .models.models import Recording
    recording = db.query(Recording).filter(Recording.id == recording_id).first()
    
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")
    
    return {
        "id": recording.id,
        "filename": recording.filename,
        "transcript": recording.transcript,
        "summary": recording.summary,
        "article": recording.article,
        "key_points": recording.key_points,
        "test_questions": recording.test_questions,
        "created_at": recording.created_at
    }

@app.get("/recordings")
async def list_recordings(db = Depends(get_db)):
    """List all processed recordings"""
    from .models.models import Recording
    recordings = db.query(Recording).all()
    
    return [
        {
            "id": r.id,
            "filename": r.filename,
            "created_at": r.created_at,
            "summary": r.summary[:200] + "..." if len(r.summary) > 200 else r.summary
        }
        for r in recordings
    ]

# New enhanced endpoints

@app.get("/search")
async def semantic_search(q: str, recording_id: int = None, limit: int = 10):
    """Semantic search across recordings using Weaviate"""
    try:
        results = await weaviate_service.semantic_search(q, recording_id, limit)
        return JSONResponse(content={"results": results, "query": q})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/knowledge-graph/{recording_id}")
async def get_knowledge_graph(recording_id: int):
    """Get knowledge graph data for a recording"""
    try:
        graph_data = await graphrag_service.query_knowledge_graph("", recording_id)
        graph_summary = graphrag_service.get_graph_summary(recording_id)
        
        return JSONResponse(content={
            "graph_data": graph_data,
            "summary": graph_summary
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph query failed: {str(e)}")

@app.post("/query-graph")
async def query_knowledge_graph(query_data: dict, db = Depends(get_db)):
    """Query the knowledge graph with natural language"""
    try:
        query = query_data.get("query", "")
        recording_id = query_data.get("recording_id")
        
        results = await graphrag_service.query_knowledge_graph(query, recording_id)
        
        return JSONResponse(content=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph query failed: {str(e)}")

@app.get("/enhance/{recording_id}")
async def enhance_recording_with_web_research(recording_id: int, db = Depends(get_db)):
    """Enhance a recording with additional web research"""
    try:
        from app.models.models import Recording
        recording = db.query(Recording).filter(Recording.id == recording_id).first()
        
        if not recording:
            raise HTTPException(status_code=404, detail="Recording not found")
        
        key_points = json.loads(recording.key_points)
        
        async with nlweb_service as nlweb:
            enhancement = await nlweb.enhance_content_with_web_research(
                recording.transcript, key_points
            )
            
            follow_up_questions = await nlweb.generate_follow_up_questions(
                recording.transcript, enhancement
            )
        
        return JSONResponse(content={
            "enhancement": enhancement,
            "follow_up_questions": follow_up_questions
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enhancement failed: {str(e)}")

@app.get("/related/{recording_id}")
async def get_related_content(recording_id: int, limit: int = 5):
    """Get content related to a specific recording"""
    try:
        # Get recording topics from knowledge graph
        topics = await weaviate_service.get_recording_topics(recording_id)
        
        # Find related segments from other recordings
        related_segments = []
        if topics:
            for topic in topics[:3]:  # Limit to top 3 topics
                segments = await weaviate_service.semantic_search(
                    topic, exclude_recording_id=recording_id, limit=3
                )
                related_segments.extend(segments)
        
        # Get graph-based relationships
        graph_relations = await graphrag_service.query_knowledge_graph(
            " ".join(topics[:2]) if topics else "", None
        )
        
        return JSONResponse(content={
            "related_segments": related_segments,
            "graph_relations": graph_relations,
            "topics": topics
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Related content query failed: {str(e)}")

@app.get("/analytics")
async def get_analytics(db = Depends(get_db)):
    """Get analytics and insights across all recordings"""
    try:
        from app.models.models import Recording
        recordings = db.query(Recording).all()
        
        # Basic statistics
        total_recordings = len(recordings)
        total_duration = sum([
            len(r.transcript.split()) / 150 * 60  # Rough estimate: 150 words per minute
            for r in recordings
        ])
        
        # Knowledge graph statistics
        graph_summary = graphrag_service.get_graph_summary()
        
        # Topic analysis across recordings
        all_topics = []
        for recording in recordings:
            topics = await weaviate_service.get_recording_topics(recording.id)
            all_topics.extend(topics)
        
        from collections import Counter
        top_topics = Counter(all_topics).most_common(10)
        
        return JSONResponse(content={
            "total_recordings": total_recordings,
            "estimated_total_duration_minutes": total_duration,
            "knowledge_graph": graph_summary,
            "top_topics": [{"topic": topic, "count": count} for topic, count in top_topics],
            "average_key_points_per_recording": sum([
                len(json.loads(r.key_points)) for r in recordings
            ]) / total_recordings if total_recordings > 0 else 0
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
