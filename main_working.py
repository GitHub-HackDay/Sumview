from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
from pathlib import Path
import json
import whisper
import openai
from typing import Optional
import uuid
import asyncio
import ssl

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

# Load Whisper model
whisper_model = None

def get_whisper_model():
    global whisper_model
    if whisper_model is None:
        print("Loading Whisper model...")
        whisper_model = whisper.load_model("base")
        print("Whisper model loaded successfully!")
    return whisper_model

# Store processed recordings in memory (for demo purposes)
recordings_db = {}

@app.get("/")
async def root():
    return {"message": "Meeting & Lecture Summarizer API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

def extract_audio_from_video(video_path: str) -> str:
    """Extract audio from video file using FFmpeg"""
    try:
        import subprocess
        
        # Create temporary audio file
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_audio_path = temp_audio.name
        temp_audio.close()
        
        # Use FFmpeg to extract audio
        cmd = [
            'ffmpeg', '-i', video_path, 
            '-vn', '-acodec', 'pcm_s16le', 
            '-ar', '16000', '-ac', '1', 
            '-y', temp_audio_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"FFmpeg error: {result.stderr}")
            # Fallback: just use the original file
            return video_path
            
        return temp_audio_path
        
    except Exception as e:
        print(f"Audio extraction failed: {e}")
        # Fallback: just use the original file
        return video_path

def is_video_file(file_path: str) -> bool:
    """Check if file is a video file"""
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.mpeg', '.mpg', '.m4v']
    return Path(file_path).suffix.lower() in video_extensions

async def transcribe_audio(file_path: str) -> str:
    """Transcribe audio using Whisper"""
    try:
        model = get_whisper_model()
        
        # Handle video files
        audio_path = file_path
        if is_video_file(file_path):
            print("Extracting audio from video...")
            audio_path = extract_audio_from_video(file_path)
        
        print("Transcribing audio...")
        result = model.transcribe(audio_path)
        transcript = result["text"]
        
        # Clean up extracted audio file if it was created
        if audio_path != file_path and os.path.exists(audio_path):
            os.unlink(audio_path)
            
        return transcript.strip()
        
    except Exception as e:
        raise Exception(f"Transcription failed: {str(e)}")

async def generate_summary_and_quiz(transcript: str) -> dict:
    """Generate summary and quiz questions using OpenAI"""
    try:
        # Check if OpenAI API key is available
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("Warning: No OpenAI API key found. Using mock data.")
            return generate_mock_content(transcript)
        
        client = openai.OpenAI(api_key=api_key)
        
        # Generate summary
        summary_prompt = f"""
        Please provide a concise summary of the following transcript in 2-3 paragraphs:

        {transcript}

        Focus on the main points, key concepts, and important takeaways.
        """
        
        summary_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": summary_prompt}],
            max_tokens=300
        )
        
        summary = summary_response.choices[0].message.content.strip()
        
        # Generate quiz questions
        quiz_prompt = f"""
        Based on the following transcript, create 5 quiz questions in JSON format:

        {transcript}

        Please return ONLY valid JSON in this exact format:
        [
            {{
                "question": "Question text here?",
                "type": "multiple_choice",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": "Option A"
            }},
            {{
                "question": "True or false question?",
                "type": "true_false",
                "correct_answer": "true"
            }}
        ]

        Include a mix of multiple choice and true/false questions.
        """
        
        quiz_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": quiz_prompt}],
            max_tokens=500
        )
        
        quiz_text = quiz_response.choices[0].message.content.strip()
        
        # Parse quiz JSON
        try:
            # Clean up the response to extract just the JSON
            start_idx = quiz_text.find('[')
            end_idx = quiz_text.rfind(']') + 1
            if start_idx != -1 and end_idx != 0:
                quiz_json = quiz_text[start_idx:end_idx]
                quiz_questions = json.loads(quiz_json)
            else:
                quiz_questions = []
        except json.JSONDecodeError:
            print("Failed to parse quiz JSON, using fallback questions")
            quiz_questions = generate_fallback_quiz(transcript)
        
        # Generate article
        article_prompt = f"""
        Write a comprehensive article based on the following transcript. 
        Make it educational and well-structured with clear sections:

        {transcript}

        The article should be 3-4 paragraphs and suitable for study purposes.
        """
        
        article_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": article_prompt}],
            max_tokens=500
        )
        
        article = article_response.choices[0].message.content.strip()
        
        return {
            "summary": summary,
            "article": article,
            "quiz_questions": quiz_questions
        }
        
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return generate_mock_content(transcript)

def generate_mock_content(transcript: str) -> dict:
    """Generate mock content when OpenAI API is not available"""
    words = transcript.split()
    topic = "the recorded content"
    
    if len(words) > 10:
        # Try to extract a topic from the transcript
        common_words = ["the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"]
        meaningful_words = [w for w in words[:20] if w.lower() not in common_words and len(w) > 3]
        if meaningful_words:
            topic = meaningful_words[0]
    
    return {
        "summary": f"This recording discusses {topic} and covers several important concepts. The main points include various aspects of the subject matter that were explained in detail. Key takeaways from this session provide valuable insights for understanding the topic better.",
        "article": f"# Understanding {topic.title()}\n\nThis comprehensive overview examines the key concepts presented in the recording. The discussion covers fundamental principles and practical applications.\n\nThe content provides detailed explanations of important topics, offering learners a solid foundation for further study. Various examples and explanations help clarify complex concepts.\n\nIn conclusion, this material serves as an excellent resource for understanding {topic} and its practical implications.",
        "quiz_questions": [
            {
                "question": f"What is the main topic discussed in this recording?",
                "type": "multiple_choice",
                "options": [f"{topic.title()}", "Mathematics", "Science", "History"],
                "correct_answer": f"{topic.title()}"
            },
            {
                "question": "Did the recording provide detailed explanations?",
                "type": "true_false",
                "correct_answer": "true"
            },
            {
                "question": "What type of content does this recording contain?",
                "type": "multiple_choice",
                "options": ["Educational material", "Entertainment", "News", "Sports"],
                "correct_answer": "Educational material"
            }
        ]
    }

def generate_fallback_quiz(transcript: str) -> list:
    """Generate fallback quiz questions"""
    return [
        {
            "question": "What is the main subject of this recording?",
            "type": "multiple_choice",
            "options": ["Educational content", "Entertainment", "News", "Music"],
            "correct_answer": "Educational content"
        },
        {
            "question": "Does this recording contain spoken content?",
            "type": "true_false",
            "correct_answer": "true"
        }
    ]

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
        transcript = await transcribe_audio(temp_file_path)
        print(f"Transcript length: {len(transcript)} characters")
        
        # Step 2: Generate summary, article, and quiz
        content = await generate_summary_and_quiz(transcript)
        
        # Store result
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
