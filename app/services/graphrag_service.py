import networkx as nx
import json
from typing import List, Dict, Any, Optional, Tuple
import spacy
from collections import defaultdict, Counter
import openai
import os
from dotenv import load_dotenv

load_dotenv()

class GraphRAGService:
    """
    Service for building and querying knowledge graphs from meeting/lecture content
    """
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.entity_embeddings = {}
        self.nlp = self._load_spacy_model()
        openai.api_key = os.getenv("OPENAI_API_KEY")
    
    def _load_spacy_model(self):
        """Load spaCy model for NER and relationship extraction"""
        try:
            return spacy.load("en_core_web_sm")
        except OSError:
            print("Warning: spaCy model not found. Run: python -m spacy download en_core_web_sm")
            return None
    
    async def build_knowledge_graph(self, recording_id: int, transcript: str, 
                                  summary: str, key_points: List[str]) -> Dict[str, Any]:
        """
        Build a knowledge graph from recording content
        """
        try:
            # Extract entities and relationships
            entities = await self._extract_entities(transcript + " " + summary)
            relationships = await self._extract_relationships(transcript, entities)
            
            # Add to graph
            graph_data = self._build_graph_structure(recording_id, entities, relationships, key_points)
            
            # Store in NetworkX graph
            self._add_to_networkx_graph(recording_id, graph_data)
            
            return {
                "entities": len(entities),
                "relationships": len(relationships),
                "graph_data": graph_data
            }
            
        except Exception as e:
            print(f"Knowledge graph building error: {e}")
            return {"entities": 0, "relationships": 0, "graph_data": {}}
    
    async def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities using spaCy and OpenAI"""
        entities = []
        
        # spaCy entity extraction
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                entities.append({
                    "text": ent.text,
                    "label": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "confidence": 1.0,
                    "source": "spacy"
                })
        
        # Enhanced entity extraction with OpenAI
        enhanced_entities = await self._extract_entities_with_openai(text)
        entities.extend(enhanced_entities)
        
        # Deduplicate and merge entities
        return self._deduplicate_entities(entities)
    
    async def _extract_entities_with_openai(self, text: str) -> List[Dict[str, Any]]:
        """Use OpenAI to extract domain-specific entities"""
        prompt = f"""
        Extract important entities from this meeting/lecture transcript. Focus on:
        - Key concepts and topics
        - People and organizations
        - Products, projects, or initiatives
        - Dates and deadlines
        - Action items and decisions
        
        Text: {text[:2000]}...
        
        Return as JSON array with format:
        [
            {{"text": "entity name", "type": "CONCEPT|PERSON|ORG|DATE|ACTION", "importance": 0.0-1.0}}
        ]
        """
        
        try:
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert at entity extraction for meeting and lecture content. Return valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.3
            )
            
            entities_data = json.loads(response.choices[0].message.content)
            return [
                {
                    "text": entity["text"],
                    "label": entity["type"],
                    "confidence": entity.get("importance", 0.5),
                    "source": "openai"
                }
                for entity in entities_data
            ]
            
        except Exception as e:
            print(f"OpenAI entity extraction error: {e}")
            return []
    
    def _deduplicate_entities(self, entities: List[Dict]) -> List[Dict]:
        """Remove duplicate entities and merge information"""
        entity_map = {}
        
        for entity in entities:
            key = entity["text"].lower().strip()
            if key in entity_map:
                # Merge confidence scores
                existing = entity_map[key]
                existing["confidence"] = max(existing["confidence"], entity["confidence"])
                if entity["source"] == "openai":
                    existing["label"] = entity["label"]  # Prefer OpenAI labels
            else:
                entity_map[key] = entity
        
        return list(entity_map.values())
    
    async def _extract_relationships(self, text: str, entities: List[Dict]) -> List[Dict]:
        """Extract relationships between entities"""
        relationships = []
        
        # Simple co-occurrence based relationships
        entity_texts = [e["text"] for e in entities]
        sentences = text.split('.')
        
        for sentence in sentences:
            sentence_entities = [e for e in entity_texts if e.lower() in sentence.lower()]
            
            # Create relationships for entities that appear together
            for i, entity1 in enumerate(sentence_entities):
                for entity2 in sentence_entities[i+1:]:
                    relationships.append({
                        "source": entity1,
                        "target": entity2,
                        "relationship": "mentioned_together",
                        "confidence": 0.7,
                        "context": sentence.strip()
                    })
        
        # Enhanced relationship extraction with OpenAI
        enhanced_rels = await self._extract_relationships_with_openai(text, entity_texts)
        relationships.extend(enhanced_rels)
        
        return self._deduplicate_relationships(relationships)
    
    async def _extract_relationships_with_openai(self, text: str, entities: List[str]) -> List[Dict]:
        """Use OpenAI to extract semantic relationships"""
        if len(entities) < 2:
            return []
        
        prompt = f"""
        Given these entities from a meeting/lecture: {', '.join(entities[:20])}
        
        Extract meaningful relationships from this text: {text[:1500]}...
        
        Return as JSON array:
        [
            {{"source": "entity1", "target": "entity2", "relationship": "relationship_type", "confidence": 0.0-1.0}}
        ]
        
        Relationship types: discusses, leads, depends_on, part_of, causes, results_in, collaborates_with
        """
        
        try:
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Extract semantic relationships between entities. Return valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.3
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            print(f"OpenAI relationship extraction error: {e}")
            return []
    
    def _deduplicate_relationships(self, relationships: List[Dict]) -> List[Dict]:
        """Remove duplicate relationships"""
        seen = set()
        unique_rels = []
        
        for rel in relationships:
            key = (rel["source"].lower(), rel["target"].lower(), rel["relationship"])
            if key not in seen:
                seen.add(key)
                unique_rels.append(rel)
        
        return unique_rels
    
    def _build_graph_structure(self, recording_id: int, entities: List[Dict], 
                             relationships: List[Dict], key_points: List[str]) -> Dict:
        """Build graph data structure"""
        # Create nodes for entities
        nodes = []
        for entity in entities:
            nodes.append({
                "id": entity["text"],
                "label": entity["text"],
                "type": entity["label"],
                "confidence": entity["confidence"],
                "recording_id": recording_id
            })
        
        # Add nodes for key points
        for i, point in enumerate(key_points):
            nodes.append({
                "id": f"keypoint_{recording_id}_{i}",
                "label": point[:50] + "..." if len(point) > 50 else point,
                "type": "KEY_POINT",
                "confidence": 1.0,
                "recording_id": recording_id,
                "full_text": point
            })
        
        # Create edges from relationships
        edges = []
        for rel in relationships:
            edges.append({
                "source": rel["source"],
                "target": rel["target"],
                "relationship": rel["relationship"],
                "confidence": rel["confidence"],
                "recording_id": recording_id
            })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "recording_id": recording_id
        }
    
    def _add_to_networkx_graph(self, recording_id: int, graph_data: Dict):
        """Add graph data to NetworkX graph for analysis"""
        # Add nodes
        for node in graph_data["nodes"]:
            self.graph.add_node(
                node["id"],
                label=node["label"],
                type=node["type"],
                confidence=node["confidence"],
                recording_id=recording_id
            )
        
        # Add edges
        for edge in graph_data["edges"]:
            if self.graph.has_node(edge["source"]) and self.graph.has_node(edge["target"]):
                self.graph.add_edge(
                    edge["source"],
                    edge["target"],
                    relationship=edge["relationship"],
                    confidence=edge["confidence"],
                    recording_id=recording_id
                )
    
    async def query_knowledge_graph(self, query: str, recording_id: Optional[int] = None) -> Dict:
        """
        Query the knowledge graph using natural language
        """
        try:
            # Extract entities from query
            query_entities = await self._extract_entities(query)
            query_terms = [e["text"].lower() for e in query_entities]
            
            # Find relevant nodes
            relevant_nodes = []
            for node_id, node_data in self.graph.nodes(data=True):
                if recording_id and node_data.get("recording_id") != recording_id:
                    continue
                
                node_label = node_data["label"].lower()
                if any(term in node_label for term in query_terms) or \
                   any(node_label in term for term in query_terms):
                    relevant_nodes.append({
                        "id": node_id,
                        "label": node_data["label"],
                        "type": node_data["type"],
                        "confidence": node_data["confidence"]
                    })
            
            # Find paths between relevant nodes
            paths = []
            if len(relevant_nodes) > 1:
                for i in range(len(relevant_nodes)):
                    for j in range(i+1, len(relevant_nodes)):
                        try:
                            path = nx.shortest_path(
                                self.graph, 
                                relevant_nodes[i]["id"], 
                                relevant_nodes[j]["id"]
                            )
                            paths.append(path)
                        except nx.NetworkXNoPath:
                            continue
            
            # Get related concepts
            related_concepts = self._get_related_concepts(query_terms)
            
            return {
                "relevant_nodes": relevant_nodes[:10],
                "paths": paths[:5],
                "related_concepts": related_concepts[:10],
                "graph_stats": {
                    "total_nodes": self.graph.number_of_nodes(),
                    "total_edges": self.graph.number_of_edges()
                }
            }
            
        except Exception as e:
            print(f"Graph query error: {e}")
            return {"relevant_nodes": [], "paths": [], "related_concepts": []}
    
    def _get_related_concepts(self, query_terms: List[str]) -> List[Dict]:
        """Find concepts related to query terms"""
        related = []
        
        for node_id, node_data in self.graph.nodes(data=True):
            node_label = node_data["label"].lower()
            
            # Check if connected to any query terms
            for term in query_terms:
                if self.graph.has_node(term) and \
                   (self.graph.has_edge(term, node_id) or self.graph.has_edge(node_id, term)):
                    related.append({
                        "concept": node_data["label"],
                        "type": node_data["type"],
                        "connection": "direct"
                    })
                    break
        
        return related
    
    def get_graph_summary(self, recording_id: Optional[int] = None) -> Dict:
        """Get summary statistics of the knowledge graph"""
        if recording_id:
            nodes = [(n, d) for n, d in self.graph.nodes(data=True) 
                    if d.get("recording_id") == recording_id]
            edges = [(u, v, d) for u, v, d in self.graph.edges(data=True) 
                    if d.get("recording_id") == recording_id]
        else:
            nodes = list(self.graph.nodes(data=True))
            edges = list(self.graph.edges(data=True))
        
        # Count entity types
        entity_types = Counter([d["type"] for n, d in nodes])
        
        # Count relationship types
        relationship_types = Counter([d["relationship"] for u, v, d in edges])
        
        return {
            "total_entities": len(nodes),
            "total_relationships": len(edges),
            "entity_types": dict(entity_types),
            "relationship_types": dict(relationship_types),
            "recordings_covered": len(set(d.get("recording_id") for n, d in nodes if d.get("recording_id")))
        }
