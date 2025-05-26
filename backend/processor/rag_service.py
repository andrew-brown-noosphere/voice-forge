"""
RAG Service for VoiceForge API integration
Bridges the RAGSystem with the FastAPI endpoints
"""
import logging
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

from processor.rag import RAGSystem
from api.models import ChunkResponse, GeneratedContent, MarketingTemplateResponse

logger = logging.getLogger(__name__)

class RAGService:
    """Service layer for RAG operations"""
    
    def __init__(self, db, processor_service=None):
        self.db = db
        self.processor_service = processor_service
        self.rag_system = RAGSystem(db)
    
    def search_chunks(
        self, 
        query: str, 
        domain: Optional[str] = None,
        content_type: Optional[str] = None,
        top_k: int = 5
    ) -> List[ChunkResponse]:
        """Search for relevant chunks"""
        try:
            chunks = self.rag_system.retrieve_relevant_chunks(
                query=query,
                top_k=top_k,
                domain=domain,
                content_type=content_type
            )
            
            # Convert to ChunkResponse models
            response_chunks = []
            for chunk in chunks:
                response_chunks.append(ChunkResponse(
                    chunk_id=chunk["id"],
                    content_id=chunk["content_id"],
                    text=chunk["text"],
                    similarity=chunk.get("similarity", 0.0),
                    chunk_index=chunk.get("chunk_index", 0),
                    metadata=chunk.get("metadata", {})
                ))
            
            return response_chunks
            
        except Exception as e:
            logger.error(f"Failed to search chunks: {e}")
            return []
    
    def get_content_chunks(self, content_id: str) -> List[ChunkResponse]:
        """Get all chunks for a specific content"""
        try:
            chunks = self.db.get_content_chunks(content_id)
            
            response_chunks = []
            for chunk in chunks:
                response_chunks.append(ChunkResponse(
                    chunk_id=chunk["id"],
                    content_id=chunk["content_id"],
                    text=chunk["text"],
                    similarity=1.0,  # Not applicable for direct retrieval
                    chunk_index=chunk.get("chunk_index", 0),
                    metadata=chunk.get("metadata", {})
                ))
            
            return response_chunks
            
        except Exception as e:
            logger.error(f"Failed to get content chunks: {e}")
            return []
    
    def process_content_for_rag(self, content_id: str) -> bool:
        """Process content into chunks for RAG"""
        return self.rag_system.process_content_for_rag(content_id)
    
    def generate_content(
        self,
        query: str,
        platform: str,
        tone: str,
        domain: Optional[str] = None,
        content_type: Optional[str] = None,
        top_k: int = 5
    ) -> GeneratedContent:
        """Generate content using RAG"""
        try:
            response = self.rag_system.process_and_generate(
                query=query,
                platform=platform,
                tone=tone,
                domain=domain,
                content_type=content_type,
                top_k=top_k
            )
            
            # Convert source chunks to the expected format
            source_chunks = []
            for chunk in response.get("source_chunks", []):
                source_chunks.append({
                    "chunk_id": chunk["chunk_id"],
                    "text": chunk["text"],
                    "similarity": chunk["similarity"],
                    "content_id": chunk.get("content_id")
                })
            
            return GeneratedContent(
                text=response["text"],
                source_chunks=source_chunks,
                metadata=response.get("metadata", {})
            )
            
        except Exception as e:
            logger.error(f"Failed to generate content: {e}")
            return GeneratedContent(
                text=f"Error generating content: {str(e)}",
                source_chunks=[],
                metadata={"error": str(e)}
            )
    
    # Template management methods
    def create_template(self, template_data: Dict[str, Any]) -> str:
        """Create a new template"""
        template_id = str(uuid.uuid4())
        template_data["id"] = template_id
        template_data["created_at"] = datetime.utcnow().isoformat()
        
        # Store in database (implement based on your database schema)
        # For now, we'll use a simple in-memory store
        if not hasattr(self, '_templates'):
            self._templates = {}
        
        self._templates[template_id] = template_data
        return template_id
    
    def get_template(self, template_id: str) -> Optional[MarketingTemplateResponse]:
        """Get a template by ID"""
        if hasattr(self, '_templates') and template_id in self._templates:
            template = self._templates[template_id]
            return MarketingTemplateResponse(**template)
        return None
    
    def list_templates(
        self,
        platform: Optional[str] = None,
        tone: Optional[str] = None,
        purpose: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[MarketingTemplateResponse]:
        """List templates with filters"""
        if not hasattr(self, '_templates'):
            self._templates = {}
        
        templates = list(self._templates.values())
        
        # Apply filters
        if platform:
            templates = [t for t in templates if t.get("platform") == platform]
        if tone:
            templates = [t for t in templates if t.get("tone") == tone]
        if purpose:
            templates = [t for t in templates if t.get("purpose") == purpose]
        
        # Apply pagination
        templates = templates[offset:offset + limit]
        
        return [MarketingTemplateResponse(**t) for t in templates]
