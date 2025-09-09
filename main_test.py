from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
from pathlib import Path
import json
import whisper
import uuid
import ssl
from typing import List, Dict

# Fix SSL certificate issue on macOS
ssl._create_default_https_context = ssl._create_unverified_context

app = FastAPI(title="Meeting & Lecture Summarizer API", version="1.0.0")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
whisper_model = None
recordings_db = {}

def get_whisper_model():
    global whisper_model
    if whisper_model is None:
        print("Loading Whisper model...")
        whisper_model = whisper.load_model("base")
        print("Whisper model loaded successfully!")
    return whisper_model

def is_video_file(file_path: str) -> bool:
    """Check if file is a video file"""
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.mpeg', '.mpg', '.m4v']
    return Path(file_path).suffix.lower() in video_extensions

def generate_content_from_transcript(transcript: str) -> Dict:
    """Generate summary, article, and quiz from transcript"""
    
    # Extract key information from transcript
    words = transcript.split()
    word_count = len(words)
    
    # Create a basic summary
    if word_count > 100:
        # Take first and last portions for summary
        first_portion = ' '.join(words[:50])
        last_portion = ' '.join(words[-30:])
        summary = f"This recording covers important topics including the main concepts discussed at the beginning: {first_portion}... The session concludes with: {last_portion}"
    else:
        summary = f"This is a brief recording covering: {transcript[:200]}..."
    
    # Create an article
    article = f"""# Analysis of the Recording

## Overview
This recording contains {word_count} words of spoken content covering various important topics.

## Main Content
{transcript[:500]}...

## Key Points
The discussion covers several important aspects that provide valuable insights for understanding the subject matter.

## Conclusion
This content serves as a useful resource for learning and reference purposes."""

    # Generate quiz questions based on content
    quiz_questions = [
        {
            "question": "What is the approximate length of this recording?",
            "type": "multiple_choice",
            "options": ["Very short (under 1 minute)", "Short (1-5 minutes)", "Medium (5-15 minutes)", "Long (over 15 minutes)"],
            "correct_answer": "Medium (5-15 minutes)" if word_count > 500 else "Short (1-5 minutes)"
        },
        {
            "question": "Does this recording contain spoken content?",
            "type": "true_false",
            "correct_answer": "true"
        }
    ]
    
    # Add content-specific questions if we can extract topics
    if any(word in transcript.lower() for word in ['math', 'mathematics', 'equation', 'solve', 'problem']):
        quiz_questions.append({
            "question": "Does this recording discuss mathematical concepts?",
            "type": "true_false",
            "correct_answer": "true"
        })
    
    if any(word in transcript.lower() for word in ['science', 'experiment', 'hypothesis', 'research']):
        quiz_questions.append({
            "question": "Is this recording related to scientific topics?",
            "type": "true_false",
            "correct_answer": "true"
        })
    
    return {
        "summary": summary,
        "article": article,
        "quiz_questions": quiz_questions
    }

@app.get("/")
async def root():
    return {"message": "Meeting & Lecture Summarizer API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Handle audio/video file upload and processing"""
    
    # Validate file type
    allowed_extensions = ['.mp3', '.wav', '.mp4', '.avi', '.mov', '.mpeg', '.mpg', '.m4a', '.flac']
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file extension: {file_extension}. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Check file size (100MB limit)
    temp_content = await file.read()
    file_size = len(temp_content)
    
    if file_size > 100 * 1024 * 1024:  # 100MB
        raise HTTPException(status_code=400, detail="File size exceeds 100MB limit")
    
    # Generate unique recording ID
    recording_id = str(uuid.uuid4())
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(temp_content)
            temp_file_path = temp_file.name
        
        print(f"Processing file: {file.filename} (Size: {file_size} bytes)")
        
        # Step 1: Transcribe audio
        try:
            model = get_whisper_model()
            print("Starting transcription...")
            
            # Try direct transcription first (works for most audio and some video formats)
            try:
                result = model.transcribe(temp_file_path, fp16=False)
                transcript = result["text"].strip()
                print(f"Direct transcription successful. Length: {len(transcript)} characters")
                
                if len(transcript) < 10:
                    raise Exception("Transcription too short")
                    
            except Exception as direct_error:
                print(f"Direct transcription failed: {direct_error}")
                
                # For video files, try with different Whisper options
                if is_video_file(temp_file_path):
                    print("Trying video transcription with different settings...")
                    try:
                        result = model.transcribe(
                            temp_file_path, 
                            fp16=False,
                            task="transcribe",
                            language="en"  # Assume English for now
                        )
                        transcript = result["text"].strip()
                        print(f"Video transcription successful. Length: {len(transcript)} characters")
                    except Exception as video_error:
                        print(f"Video transcription also failed: {video_error}")
                        raise Exception("Could not transcribe audio from video")
                else:
                    raise direct_error
                
            if not transcript or len(transcript) < 10:
                raise Exception("Transcription produced empty or very short result")
                
        except Exception as e:
            print(f"All transcription attempts failed: {e}")
            # Return an error instead of fake content
            raise HTTPException(
                status_code=422, 
                detail=f"Could not transcribe audio from this file. This may be due to: 1) Audio quality issues, 2) Unsupported codec, or 3) Missing FFmpeg for video processing. Please try uploading a clear audio file (MP3, WAV) or a standard video format. Error: {str(e)}"
            )
        
        if not transcript:
            raise HTTPException(
                status_code=422,
                detail="No audio content could be extracted from this file. Please ensure the file contains clear spoken audio."
            )
        
        # Step 2: Generate content
        content = generate_content_from_transcript(transcript)
        
        # Create result
        result = {
            "id": recording_id,
            "recording_id": recording_id,
            "filename": file.filename,
            "status": "completed",
            "transcript": transcript,
            "summary": content["summary"],
            "article": content["article"],
            "test_questions": content["quiz_questions"]
        }
        
        # Store result
        recordings_db[recording_id] = result
        
        # Clean up temp file
        os.unlink(temp_file_path)
        
        print("Processing completed successfully!")
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
    if recording_id in recordings_db:
        return recordings_db[recording_id]
    else:
        raise HTTPException(status_code=404, detail="Recording not found")

@app.get("/api/recordings")
async def list_recordings():
    """List all recordings"""
    return list(recordings_db.values())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
