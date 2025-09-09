import openai
import json
from typing import Dict, List
import random
import os
from dotenv import load_dotenv

load_dotenv()

class TestGenerationService:
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
    
    async def generate_test(self, transcript: str, key_points_json: str) -> str:
        """
        Generate comprehension test questions based on the transcript and key points
        """
        try:
            key_points = json.loads(key_points_json)
            
            # Generate different types of questions
            multiple_choice = await self._generate_multiple_choice(transcript, key_points)
            short_answer = await self._generate_short_answer(transcript, key_points)
            true_false = await self._generate_true_false(transcript, key_points)
            
            # Combine all questions into a comprehensive test
            test_data = {
                "multiple_choice": multiple_choice,
                "short_answer": short_answer,
                "true_false": true_false,
                "instructions": "This comprehension test covers the main concepts discussed in the meeting/lecture. Take your time and refer back to the materials if needed."
            }
            
            return json.dumps(test_data, indent=2)
            
        except Exception as e:
            raise Exception(f"Test generation failed: {str(e)}")
    
    async def _generate_multiple_choice(self, transcript: str, key_points: List[str]) -> List[Dict]:
        """Generate multiple choice questions"""
        prompt = f"""
        Based on this transcript and key points, create 3-5 multiple choice questions that test understanding of the main concepts.
        
        Key Points:
        {', '.join(key_points)}
        
        Transcript:
        {transcript[:2000]}...
        
        Format as JSON array with this structure:
        [
            {{
                "question": "Question text here?",
                "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
                "correct_answer": "A",
                "explanation": "Brief explanation of why this is correct"
            }}
        ]
        """
        
        response = await self._call_openai(prompt, max_tokens=800)
        
        try:
            return json.loads(response.strip())
        except:
            # Fallback to empty list if parsing fails
            return []
    
    async def _generate_short_answer(self, transcript: str, key_points: List[str]) -> List[Dict]:
        """Generate short answer questions"""
        prompt = f"""
        Create 2-3 short answer questions that require deeper thinking about the concepts discussed.
        
        Key Points:
        {', '.join(key_points)}
        
        Format as JSON array:
        [
            {{
                "question": "Question text here?",
                "sample_answer": "Example of a good answer",
                "points": 5
            }}
        ]
        """
        
        response = await self._call_openai(prompt, max_tokens=500)
        
        try:
            return json.loads(response.strip())
        except:
            return []
    
    async def _generate_true_false(self, transcript: str, key_points: List[str]) -> List[Dict]:
        """Generate true/false questions"""
        prompt = f"""
        Create 3-4 true/false questions based on the content. Include some subtle misconceptions to test careful listening.
        
        Key Points:
        {', '.join(key_points)}
        
        Format as JSON array:
        [
            {{
                "statement": "Statement to evaluate",
                "correct_answer": true,
                "explanation": "Why this is true/false"
            }}
        ]
        """
        
        response = await self._call_openai(prompt, max_tokens=600)
        
        try:
            return json.loads(response.strip())
        except:
            return []
    
    async def _call_openai(self, prompt: str, max_tokens: int = 500) -> str:
        """Make API call to OpenAI"""
        try:
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert educator who creates comprehensive tests to evaluate understanding of meeting and lecture content. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"OpenAI API call failed: {str(e)}")
