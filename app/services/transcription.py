import whisper
import os
from pathlib import Path
import tempfile

# Try to import video processing libraries
try:
    from moviepy.editor import VideoFileClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False

class TranscriptionService:
    def __init__(self):
        # Load Whisper model (you can change to different sizes: tiny, base, small, medium, large)
        self.model = whisper.load_model("base")
    
    async def transcribe(self, file_path: str) -> str:
        """
        Transcribe audio or video file to text using OpenAI Whisper
        """
        try:
            # For now, let's directly use Whisper on the file
            # Whisper can handle many video formats directly
            result = self.model.transcribe(file_path)
            
            # Extract text with timestamps for better context
            transcript_with_timestamps = self._format_transcript_with_timestamps(result)
            
            return transcript_with_timestamps
            
        except Exception as e:
            # If direct transcription fails, try with video processing if available
            if self._is_video_file(file_path) and MOVIEPY_AVAILABLE:
                try:
                    audio_path = await self._extract_audio_from_video(file_path)
                    result = self.model.transcribe(audio_path)
                    # Clean up temporary audio file
                    os.unlink(audio_path)
                    return self._format_transcript_with_timestamps(result)
                except Exception as video_error:
                    raise Exception(f"Transcription failed for video file: {str(video_error)}")
            
            raise Exception(f"Transcription failed: {str(e)}")
    
    def _is_video_file(self, file_path: str) -> bool:
        """Check if file is a video file"""
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.mpeg', '.mpg', '.m4v', '.3gp']
        return Path(file_path).suffix.lower() in video_extensions
    
    async def _extract_audio_from_video(self, video_path: str) -> str:
        """Extract audio from video file"""
        if not MOVIEPY_AVAILABLE:
            raise Exception("MoviePy is not available. Cannot extract audio from video files.")
        
        try:
            # Create temporary audio file
            temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            temp_audio_path = temp_audio.name
            temp_audio.close()
            
            # Extract audio using moviepy
            from moviepy.editor import VideoFileClip
            video = VideoFileClip(video_path)
            audio = video.audio
            audio.write_audiofile(temp_audio_path, verbose=False, logger=None)
            
            # Clean up
            audio.close()
            video.close()
            
            return temp_audio_path
            
        except Exception as e:
            raise Exception(f"Audio extraction failed: {str(e)}")
    
    def _format_transcript_with_timestamps(self, result) -> str:
        """Format transcript with timestamps for better readability"""
        formatted_transcript = ""
        
        for segment in result['segments']:
            start_time = self._format_time(segment['start'])
            end_time = self._format_time(segment['end'])
            text = segment['text'].strip()
            
            formatted_transcript += f"[{start_time} - {end_time}] {text}\n"
        
        return formatted_transcript
    
    def _format_time(self, seconds: float) -> str:
        """Convert seconds to MM:SS format"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
