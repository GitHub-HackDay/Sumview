from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
from pathlib import Path
import json

app = FastAPI(title="Meeting & Lecture Summarizer API", version="1.0.0")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Meeting & Lecture Summarizer API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Handle audio/video file upload and processing (simplified version)"""
    
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
    temp_content = await file.read()
    file_size = len(temp_content)
    
    if file_size > 100 * 1024 * 1024:  # 100MB
        raise HTTPException(status_code=400, detail="File size exceeds 100MB limit")
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(temp_content)
            temp_file_path = temp_file.name
        
        print(f"Successfully uploaded file: {file.filename} (Type: {file.content_type}, Size: {file_size} bytes)")
        
        # For now, return a mock result
        result = {
            "recording_id": "test-123",
            "filename": file.filename,
            "status": "completed",
            "summary": "This is a test summary for your uploaded MPEG4 file. The file was successfully processed.",
            "article": "This is a test article generated from your recording. Your MPEG4 file upload and processing workflow is working correctly.",
            "test_questions": [
                {
                    "question": "What type of file was uploaded?",
                    "type": "multiple_choice",
                    "options": ["MP3", "MPEG4", "WAV", "AVI"],
                    "correct_answer": "MPEG4"
                }
            ]
        }
        
        # Clean up temp file
        os.unlink(temp_file_path)
        
        return JSONResponse(content=result)
        
    except Exception as e:
        # Clean up temp file if it exists
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        
        print(f"Processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.get("/recordings/{recording_id}")
async def get_recording(recording_id: str):
    """Get recording details by ID"""
    # Mock response for testing
    return {
        "id": recording_id,
        "status": "completed",
        "summary": "Test summary",
        "article": "Test article",
        "test_questions": []
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
