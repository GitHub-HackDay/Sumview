import weaviate
import json
from typing import List, Dict, Any, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv

load_dotenv()

class WeaviateService:
    """
    Service for managing vector embeddings and semantic search using Weaviate
    """
    
    def __init__(self):
        self.client = self._initialize_client()
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self._ensure_schema()
    
    def _initialize_client(self):
        """Initialize Weaviate client"""
        weaviate_url = os.getenv("WEAVIATE_URL", "http://localhost:8080")
        
        try:
            client = weaviate.Client(
                url=weaviate_url,
                auth_client_secret=weaviate.AuthApiKey(
                    api_key=os.getenv("WEAVIATE_API_KEY", "")
                ) if os.getenv("WEAVIATE_API_KEY") else None,
                additional_headers={
                    "X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY", "")
                }
            )
            return client
        except Exception as e:
            print(f"Warning: Could not connect to Weaviate: {e}")
            return None
    
    def _ensure_schema(self):
        """Create schema for recording segments if it doesn't exist"""
        if not self.client:
            return
            
        schema = {
            "class": "RecordingSegment",
            "description": "A segment of a recording with its transcript and metadata",
            "properties": [
                {
                    "name": "content",
                    "dataType": ["text"],
                    "description": "The transcript content of this segment"
                },
                {
                    "name": "recording_id",
                    "dataType": ["int"],
                    "description": "ID of the parent recording"
                },
                {
                    "name": "start_time",
                    "dataType": ["number"],
                    "description": "Start time of the segment in seconds"
                },
                {
                    "name": "end_time",
                    "dataType": ["number"],
                    "description": "End time of the segment in seconds"
                },
                {
                    "name": "speaker",
                    "dataType": ["text"],
                    "description": "Speaker identification if available"
                },
                {
                    "name": "topics",
                    "dataType": ["text[]"],
                    "description": "Topics discussed in this segment"
                },
                {
                    "name": "sentiment",
                    "dataType": ["text"],
                    "description": "Sentiment of the segment (positive/negative/neutral)"
                }
            ],
            "vectorizer": "text2vec-openai",
            "moduleConfig": {
                "text2vec-openai": {
                    "model": "ada",
                    "modelVersion": "002",
                    "type": "text"
                }
            }
        }
        
        try:
            if not self.client.schema.exists("RecordingSegment"):
                self.client.schema.create_class(schema)
        except Exception as e:
            print(f"Schema creation warning: {e}")
    
    async def store_recording_segments(self, recording_id: int, transcript: str, 
                                     segments: List[Dict] = None) -> bool:
        """
        Store recording segments in Weaviate for semantic search
        """
        if not self.client:
            return False
            
        try:
            # If no segments provided, create them from transcript
            if not segments:
                segments = self._create_segments_from_transcript(transcript)
            
            # Store each segment
            for segment in segments:
                data_object = {
                    "content": segment.get("text", ""),
                    "recording_id": recording_id,
                    "start_time": segment.get("start_time", 0),
                    "end_time": segment.get("end_time", 0),
                    "speaker": segment.get("speaker", "unknown"),
                    "topics": segment.get("topics", []),
                    "sentiment": segment.get("sentiment", "neutral")
                }
                
                self.client.data_object.create(
                    data_object=data_object,
                    class_name="RecordingSegment"
                )
            
            return True
            
        except Exception as e:
            print(f"Error storing segments: {e}")
            return False
    
    def _create_segments_from_transcript(self, transcript: str) -> List[Dict]:
        """Create segments from timestamped transcript"""
        segments = []
        lines = transcript.split('\n')
        
        for line in lines:
            if '[' in line and ']' in line:
                # Extract timestamp and text
                timestamp_match = line.split(']', 1)
                if len(timestamp_match) == 2:
                    timestamp_part = timestamp_match[0].replace('[', '')
                    text_part = timestamp_match[1].strip()
                    
                    # Parse time range
                    if ' - ' in timestamp_part:
                        start_str, end_str = timestamp_part.split(' - ')
                        start_time = self._time_to_seconds(start_str)
                        end_time = self._time_to_seconds(end_str)
                    else:
                        start_time = self._time_to_seconds(timestamp_part)
                        end_time = start_time + 30  # Default 30 second segments
                    
                    segments.append({
                        "text": text_part,
                        "start_time": start_time,
                        "end_time": end_time,
                        "speaker": "unknown",
                        "topics": [],
                        "sentiment": "neutral"
                    })
        
        return segments
    
    def _time_to_seconds(self, time_str: str) -> float:
        """Convert MM:SS format to seconds"""
        try:
            parts = time_str.split(':')
            if len(parts) == 2:
                return int(parts[0]) * 60 + int(parts[1])
            return 0
        except:
            return 0
    
    async def semantic_search(self, query: str, recording_id: Optional[int] = None, 
                            limit: int = 10) -> List[Dict]:
        """
        Perform semantic search across recording segments
        """
        if not self.client:
            return []
        
        try:
            where_filter = None
            if recording_id:
                where_filter = {
                    "path": ["recording_id"],
                    "operator": "Equal",
                    "valueInt": recording_id
                }
            
            result = (
                self.client.query
                .get("RecordingSegment", [
                    "content", "recording_id", "start_time", "end_time", 
                    "speaker", "topics", "sentiment"
                ])
                .with_near_text({"concepts": [query]})
                .with_where(where_filter) if where_filter else 
                self.client.query.get("RecordingSegment", [
                    "content", "recording_id", "start_time", "end_time", 
                    "speaker", "topics", "sentiment"
                ]).with_near_text({"concepts": [query]})
                .with_limit(limit)
                .with_additional(["certainty", "distance"])
                .do()
            )
            
            return result.get("data", {}).get("Get", {}).get("RecordingSegment", [])
            
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    async def get_related_segments(self, segment_content: str, 
                                 exclude_recording_id: Optional[int] = None) -> List[Dict]:
        """
        Find segments related to the given content across all recordings
        """
        if not self.client:
            return []
        
        try:
            where_filter = None
            if exclude_recording_id:
                where_filter = {
                    "path": ["recording_id"],
                    "operator": "NotEqual",
                    "valueInt": exclude_recording_id
                }
            
            result = (
                self.client.query
                .get("RecordingSegment", [
                    "content", "recording_id", "start_time", "end_time", "topics"
                ])
                .with_near_text({"concepts": [segment_content]})
                .with_where(where_filter) if where_filter else
                self.client.query.get("RecordingSegment", [
                    "content", "recording_id", "start_time", "end_time", "topics"
                ]).with_near_text({"concepts": [segment_content]})
                .with_limit(5)
                .with_additional(["certainty"])
                .do()
            )
            
            return result.get("data", {}).get("Get", {}).get("RecordingSegment", [])
            
        except Exception as e:
            print(f"Related segments error: {e}")
            return []
    
    async def get_recording_topics(self, recording_id: int) -> List[str]:
        """
        Extract all topics discussed in a recording
        """
        if not self.client:
            return []
        
        try:
            result = (
                self.client.query
                .get("RecordingSegment", ["topics"])
                .with_where({
                    "path": ["recording_id"],
                    "operator": "Equal",
                    "valueInt": recording_id
                })
                .do()
            )
            
            segments = result.get("data", {}).get("Get", {}).get("RecordingSegment", [])
            topics = set()
            
            for segment in segments:
                segment_topics = segment.get("topics", [])
                if segment_topics:
                    topics.update(segment_topics)
            
            return list(topics)
            
        except Exception as e:
            print(f"Topics extraction error: {e}")
            return []
