import openai
import json
from typing import Dict, List
import os
from dotenv import load_dotenv

load_dotenv()

class SummarizationService:
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
    
    async def generate_content(self, transcript: str) -> Dict[str, str]:
        """
        Generate summary, article, and key points from transcript
        """
        try:
            # Generate summary
            summary = await self._generate_summary(transcript)
            
            # Generate detailed article
            article = await self._generate_article(transcript, summary)
            
            # Extract key points
            key_points = await self._extract_key_points(transcript)
            
            return {
                "summary": summary,
                "article": article,
                "key_points": json.dumps(key_points)
            }
            
        except Exception as e:
            raise Exception(f"Content generation failed: {str(e)}")
    
    async def _generate_summary(self, transcript: str) -> str:
        """Generate a concise summary of the main message"""
        prompt = f"""
        Please provide a concise summary of the main message and key points from this meeting/lecture transcript.
        Focus on the core concepts, decisions made, and action items.
        
        Transcript:
        {transcript}
        
        Summary:
        """
        
        response = await self._call_openai(prompt, max_tokens=300)
        return response.strip()
    
    async def _generate_article(self, transcript: str, summary: str) -> str:
        """Generate a comprehensive follow-up article"""
        prompt = f"""
        Based on this meeting/lecture transcript, create a comprehensive follow-up article for people who missed the session.
        Include:
        - Introduction with context
        - Main topics covered
        - Key insights and takeaways
        - Action items or next steps
        - Conclusion
        
        Summary: {summary}
        
        Full Transcript:
        {transcript}
        
        Article:
        """
        
        response = await self._call_openai(prompt, max_tokens=1000)
        return response.strip()
    
    async def _extract_key_points(self, transcript: str) -> List[str]:
        """Extract key points as a list"""
        prompt = f"""
        Extract the most important key points from this transcript as a numbered list.
        Focus on actionable items, key decisions, important concepts, and main takeaways.
        Provide 5-10 key points maximum.
        
        Transcript:
        {transcript}
        
        Key Points (as a JSON array of strings):
        """
        
        response = await self._call_openai(prompt, max_tokens=400)
        
        try:
            # Try to parse as JSON array
            key_points = json.loads(response.strip())
            if isinstance(key_points, list):
                return key_points
        except:
            # Fallback: split by lines and clean up
            lines = response.strip().split('\n')
            key_points = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('[') and not line.startswith(']'):
                    # Remove numbering if present
                    if line[0].isdigit():
                        line = line.split('.', 1)[-1].strip()
                    key_points.append(line)
            return key_points[:10]  # Limit to 10 points
    
    async def _call_openai(self, prompt: str, max_tokens: int = 500) -> str:
        """Make API call to OpenAI"""
        try:
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing meeting and lecture content and creating comprehensive summaries and articles."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"OpenAI API call failed: {str(e)}")
