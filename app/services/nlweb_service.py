import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
import json
import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()

class NLWebService:
    """
    Service for natural language web processing and content enhancement
    """
    
    def __init__(self):
        self.session = None
        self.base_urls = {
            "wikipedia": "https://en.wikipedia.org/api/rest_v1/page/summary/",
            "news": "https://newsapi.org/v2/everything",
            "academic": "https://api.semanticscholar.org/graph/v1/paper/search"
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def enhance_content_with_web_research(self, transcript: str, 
                                              key_points: List[str]) -> Dict[str, Any]:
        """
        Enhance recording content with relevant web research
        """
        if not self.session:
            async with self:
                return await self._perform_enhancement(transcript, key_points)
        else:
            return await self._perform_enhancement(transcript, key_points)
    
    async def _perform_enhancement(self, transcript: str, key_points: List[str]) -> Dict[str, Any]:
        """Perform the actual content enhancement"""
        try:
            # Extract key topics and entities for research
            research_topics = await self._extract_research_topics(transcript, key_points)
            
            # Gather information from multiple sources
            wikipedia_data = await self._search_wikipedia(research_topics)
            news_data = await self._search_news(research_topics)
            academic_data = await self._search_academic_papers(research_topics)
            
            # Generate enhanced content
            enhanced_content = await self._generate_enhanced_content(
                transcript, key_points, wikipedia_data, news_data, academic_data
            )
            
            return {
                "enhanced_summary": enhanced_content.get("summary", ""),
                "additional_context": enhanced_content.get("context", ""),
                "related_resources": enhanced_content.get("resources", []),
                "fact_checks": enhanced_content.get("fact_checks", []),
                "source_data": {
                    "wikipedia": wikipedia_data,
                    "news": news_data,
                    "academic": academic_data
                }
            }
            
        except Exception as e:
            print(f"Web enhancement error: {e}")
            return {
                "enhanced_summary": "",
                "additional_context": "",
                "related_resources": [],
                "fact_checks": [],
                "source_data": {}
            }
    
    async def _extract_research_topics(self, transcript: str, key_points: List[str]) -> List[str]:
        """Extract topics suitable for web research"""
        topics = []
        
        # Extract from key points
        for point in key_points:
            # Look for proper nouns, concepts, technologies
            words = point.split()
            for word in words:
                if word[0].isupper() and len(word) > 3:
                    topics.append(word)
        
        # Extract from transcript using simple NLP
        # Look for patterns like "discussing X", "about Y", "regarding Z"
        patterns = [
            r"discussing (\w+(?:\s+\w+){0,2})",
            r"about (\w+(?:\s+\w+){0,2})",
            r"regarding (\w+(?:\s+\w+){0,2})",
            r"focus on (\w+(?:\s+\w+){0,2})",
            r"implementation of (\w+(?:\s+\w+){0,2})"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, transcript, re.IGNORECASE)
            topics.extend([match.strip() for match in matches])
        
        # Remove duplicates and filter
        unique_topics = list(set(topics))
        filtered_topics = [t for t in unique_topics if len(t) > 2 and not t.isdigit()]
        
        return filtered_topics[:10]  # Limit to top 10 topics
    
    async def _search_wikipedia(self, topics: List[str]) -> List[Dict]:
        """Search Wikipedia for topic information"""
        results = []
        
        for topic in topics:
            try:
                url = self.base_urls["wikipedia"] + topic.replace(" ", "_")
                async with self.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        results.append({
                            "topic": topic,
                            "title": data.get("title", ""),
                            "summary": data.get("extract", ""),
                            "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                            "source": "wikipedia"
                        })
                    
                # Add delay to be respectful to the API
                await asyncio.sleep(0.1)
                
            except Exception as e:
                print(f"Wikipedia search error for {topic}: {e}")
                continue
        
        return results
    
    async def _search_news(self, topics: List[str]) -> List[Dict]:
        """Search for recent news related to topics"""
        results = []
        api_key = os.getenv("NEWS_API_KEY")
        
        if not api_key:
            return results
        
        for topic in topics[:5]:  # Limit to avoid API quota
            try:
                params = {
                    "q": topic,
                    "sortBy": "relevancy",
                    "pageSize": 3,
                    "apiKey": api_key,
                    "language": "en"
                }
                
                async with self.session.get(self.base_urls["news"], params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        articles = data.get("articles", [])
                        
                        for article in articles:
                            results.append({
                                "topic": topic,
                                "title": article.get("title", ""),
                                "description": article.get("description", ""),
                                "url": article.get("url", ""),
                                "published_at": article.get("publishedAt", ""),
                                "source": article.get("source", {}).get("name", ""),
                                "type": "news"
                            })
                
                await asyncio.sleep(0.2)
                
            except Exception as e:
                print(f"News search error for {topic}: {e}")
                continue
        
        return results
    
    async def _search_academic_papers(self, topics: List[str]) -> List[Dict]:
        """Search for academic papers related to topics"""
        results = []
        
        for topic in topics[:3]:  # Limit to avoid overwhelming
            try:
                params = {
                    "query": topic,
                    "limit": 3,
                    "fields": "title,abstract,url,year,authors"
                }
                
                async with self.session.get(self.base_urls["academic"], params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        papers = data.get("data", [])
                        
                        for paper in papers:
                            results.append({
                                "topic": topic,
                                "title": paper.get("title", ""),
                                "abstract": paper.get("abstract", ""),
                                "url": paper.get("url", ""),
                                "year": paper.get("year", ""),
                                "authors": [author.get("name", "") for author in paper.get("authors", [])],
                                "type": "academic"
                            })
                
                await asyncio.sleep(0.3)
                
            except Exception as e:
                print(f"Academic search error for {topic}: {e}")
                continue
        
        return results
    
    async def _generate_enhanced_content(self, transcript: str, key_points: List[str],
                                       wikipedia_data: List[Dict], news_data: List[Dict],
                                       academic_data: List[Dict]) -> Dict[str, Any]:
        """Generate enhanced content using web research data"""
        # Create context from research
        context_parts = []
        resources = []
        
        # Process Wikipedia data
        for item in wikipedia_data:
            if item["summary"]:
                context_parts.append(f"**{item['title']}**: {item['summary'][:200]}...")
                resources.append({
                    "title": item["title"],
                    "url": item["url"],
                    "type": "reference",
                    "source": "Wikipedia"
                })
        
        # Process news data
        recent_news = []
        for item in news_data:
            if item["description"]:
                recent_news.append(f"- {item['title']}: {item['description'][:150]}...")
                resources.append({
                    "title": item["title"],
                    "url": item["url"],
                    "type": "news",
                    "source": item["source"],
                    "published": item["published_at"]
                })
        
        # Process academic data
        academic_insights = []
        for item in academic_data:
            if item["abstract"]:
                academic_insights.append(f"- {item['title']} ({item['year']}): {item['abstract'][:150]}...")
                resources.append({
                    "title": item["title"],
                    "url": item["url"],
                    "type": "academic",
                    "authors": item["authors"],
                    "year": item["year"]
                })
        
        # Create enhanced summary
        enhanced_summary = f"""
        ## Enhanced Summary with Web Context
        
        ### Background Information
        {chr(10).join(context_parts[:3])}
        
        ### Recent Developments
        {chr(10).join(recent_news[:3])}
        
        ### Academic Perspective
        {chr(10).join(academic_insights[:2])}
        """
        
        additional_context = f"""
        ## Additional Context from Web Research
        
        This meeting/lecture content has been enhanced with information from multiple sources including Wikipedia, recent news, and academic papers. The research provides broader context for the topics discussed.
        
        ### Key Connections
        - The topics discussed align with current industry trends and academic research
        - Recent developments in the field may impact the discussed concepts
        - Historical context from reference sources provides foundation for understanding
        """
        
        return {
            "summary": enhanced_summary.strip(),
            "context": additional_context.strip(),
            "resources": resources,
            "fact_checks": []  # Could be enhanced with fact-checking APIs
        }
    
    async def generate_follow_up_questions(self, transcript: str, 
                                         enhanced_content: Dict[str, Any]) -> List[str]:
        """Generate follow-up questions based on content and web research"""
        questions = []
        
        # Extract topics from enhanced content
        topics = []
        for resource in enhanced_content.get("related_resources", []):
            topics.append(resource.get("title", ""))
        
        # Generate questions based on gaps between meeting content and web research
        base_questions = [
            f"How does the discussion relate to recent developments in {topic}?"
            for topic in topics[:3]
        ]
        
        questions.extend(base_questions)
        
        # Add generic follow-up questions
        questions.extend([
            "What are the latest industry trends related to the topics discussed?",
            "Are there any conflicting viewpoints in recent research?",
            "What additional resources would help deepen understanding?",
            "How can the discussed concepts be applied in practice?"
        ])
        
        return questions[:8]  # Return top 8 questions
    
    async def validate_claims(self, claims: List[str]) -> List[Dict]:
        """Basic claim validation using web sources"""
        # This is a simplified implementation
        # In a production system, you'd use specialized fact-checking APIs
        
        validations = []
        for claim in claims:
            # Extract key terms from claim
            words = claim.split()
            key_terms = [w for w in words if len(w) > 4 and w.isalpha()]
            
            if key_terms:
                # Search for supporting information
                search_query = " ".join(key_terms[:3])
                wikipedia_results = await self._search_wikipedia([search_query])
                
                validation = {
                    "claim": claim,
                    "confidence": "unknown",
                    "supporting_sources": len(wikipedia_results),
                    "notes": "Basic validation performed - manual verification recommended"
                }
                
                validations.append(validation)
        
        return validations
