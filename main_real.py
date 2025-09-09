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
import librosa
import soundfile as sf
import numpy as np
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

def extract_audio_with_librosa(file_path: str) -> str:
    """Extract audio using librosa (works for many formats)"""
    try:
        print("Extracting audio using librosa...")
        
        # Create temporary audio file
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_audio_path = temp_audio.name
        temp_audio.close()
        
        # Load audio using librosa (supports many formats)
        audio_data, sample_rate = librosa.load(file_path, sr=16000)  # Whisper prefers 16kHz
        
        # Save as WAV file
        sf.write(temp_audio_path, audio_data, sample_rate)
        
        print(f"Audio extracted successfully. Duration: {len(audio_data)/sample_rate:.2f} seconds")
        return temp_audio_path
        
    except Exception as e:
        print(f"Librosa audio extraction failed: {e}")
        raise Exception(f"Could not extract audio: {str(e)}")

def generate_content_from_transcript(transcript: str) -> Dict:
    """Generate summary, article, and quiz from actual transcript content"""
    
    if not transcript or len(transcript.strip()) < 20:
        raise Exception("Transcript too short to generate meaningful content")
    
    words = transcript.split()
    word_count = len(words)
    
    # Analyze the content to identify topics and create relevant questions
    transcript_lower = transcript.lower()
    
    # Create intelligent summary based on actual content
    sentences = transcript.split('.')
    important_sentences = []
    
    # Take first few and last few sentences for summary
    if len(sentences) > 5:
        important_sentences.extend(sentences[:2])  # First 2 sentences
        important_sentences.extend(sentences[-2:])  # Last 2 sentences
    else:
        important_sentences = sentences[:3]  # Just take first 3 if short
    
    summary = '. '.join([s.strip() for s in important_sentences if s.strip()]) + '.'
    
    # Create article from the full transcript
    paragraphs = []
    words_per_paragraph = 100
    
    for i in range(0, len(words), words_per_paragraph):
        paragraph_words = words[i:i + words_per_paragraph]
        paragraph = ' '.join(paragraph_words)
        if paragraph.strip():
            paragraphs.append(paragraph.strip())
    
    article = f"""# Transcript Analysis

## Overview
This recording contains {word_count} words of spoken content covering the following topics.

## Content Summary
{summary}

## Full Content Analysis
""" + '\n\n'.join([f"### Section {i+1}\n{para}" for i, para in enumerate(paragraphs[:3])])

    # Generate intelligent quiz questions based on actual content
    quiz_questions = []
    
    # Question 1: About content length/type
    if word_count > 500:
        duration_type = "Medium length"
    elif word_count > 200:
        duration_type = "Short"
    else:
        duration_type = "Very short"
        
    quiz_questions.append({
        "question": f"Based on the transcript length ({word_count} words), how would you classify this recording?",
        "type": "multiple_choice",
        "options": ["Very short", "Short", "Medium length", "Long"],
        "correct_answer": duration_type
    })
    
    # Question 2: Content-specific questions
    if any(word in transcript_lower for word in ['math', 'equation', 'solve', 'calculate', 'derivative', 'integral', 'antiderivative']):
        quiz_questions.append({
            "question": "Does this recording discuss mathematical concepts?",
            "type": "true_false",
            "correct_answer": "true"
        })
        
        if 'antiderivative' in transcript_lower or 'integral' in transcript_lower:
            quiz_questions.append({
                "question": "What mathematical concept is primarily discussed?",
                "type": "multiple_choice",
                "options": ["Algebra", "Geometry", "Calculus", "Statistics"],
                "correct_answer": "Calculus"
            })
    
    elif any(word in transcript_lower for word in ['science', 'experiment', 'research', 'hypothesis', 'data']):
        quiz_questions.append({
            "question": "Is this recording related to scientific topics?",
            "type": "true_false",
            "correct_answer": "true"
        })
    
    # Question 3: Extract a key term or concept
    # Find frequently mentioned important words
    common_words = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an', 'is', 'was', 'are', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them']
    content_words = [word.lower().strip('.,!?;:') for word in words if word.lower() not in common_words and len(word) > 3]
    
    if content_words:
        # Find most frequent content words
        word_freq = {}
        for word in content_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        most_common = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:3]
        
        if most_common and most_common[0][1] > 1:  # If word appears more than once
            key_term = most_common[0][0]
            quiz_questions.append({
                "question": f"Which term is mentioned frequently in this recording?",
                "type": "multiple_choice",
                "options": [key_term.title(), "General discussion", "Introduction", "Conclusion"],
                "correct_answer": key_term.title()
            })
    
    # Always add a basic comprehension question
    quiz_questions.append({
        "question": "Does this recording contain spoken human speech?",
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
        
        # Step 1: Extract and transcribe audio
        model = get_whisper_model()
        transcript = None
        audio_path_to_clean = None
        
        try:
            print("Starting transcription...")
            
            # For video files or unsupported audio, use librosa
            if is_video_file(temp_file_path) or file_extension in ['.m4a', '.flac']:
                audio_path = extract_audio_with_librosa(temp_file_path)
                audio_path_to_clean = audio_path
            else:
                audio_path = temp_file_path
            
            # Transcribe with Whisper
            result = model.transcribe(audio_path, fp16=False, language='en')
            transcript = result["text"].strip()
            
            print(f"Transcription completed. Length: {len(transcript)} characters")
            print(f"Transcript preview: {transcript[:200]}...")
            
        except Exception as e:
            print(f"Transcription failed: {e}")
            raise HTTPException(
                status_code=422,
                detail=f"Could not transcribe audio from this file. Error: {str(e)}. Please try a clear audio file (MP3, WAV) or ensure the video has clear speech."
            )
        finally:
            # Clean up extracted audio file
            if audio_path_to_clean and os.path.exists(audio_path_to_clean):
                os.unlink(audio_path_to_clean)
        
        if not transcript or len(transcript.strip()) < 10:
            raise HTTPException(
                status_code=422,
                detail="No meaningful speech was detected in this file. Please ensure the file contains clear spoken audio."
            )
        
        # Step 2: Generate content based on actual transcript
        try:
            content = generate_content_from_transcript(transcript)
        except Exception as e:
            print(f"Content generation failed: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate content from transcript: {str(e)}"
            )
        
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
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Clean up temp files if they exist
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        
        print(f"Unexpected error: {str(e)}")
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
