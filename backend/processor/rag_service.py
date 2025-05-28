"""
RAG Service for VoiceForge API integration
Enhanced with automated RAG optimization integration
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
        top_k: int = 5,
        org_id: str = None
    ) -> List[ChunkResponse]:
        """
        Search for relevant chunks.
        Enhanced with lazy RAG optimization.
        """
        try:
            # 🆕 ADD: Ensure org is optimized before querying (lazy optimization)
            try:
                from automated_rag_integration import RAGIntegrationHooks
                
                optimization_result = RAGIntegrationHooks.on_rag_query_requested(org_id, query)
                
                if optimization_result['status'] == 'processing':
                    logger.info(f"🔄 RAG optimization triggered for org {org_id} during query")
                    # Note: In a production system, you might want to queue the query
                    # or return a "processing" response to the user
                    
            except Exception as e:
                logger.warning(f"⚠️ RAG optimization check failed for org {org_id}: {e}")
                # Continue with query even if optimization check fails
            
            chunks = self.rag_system.retrieve_relevant_chunks(
                query=query,
                top_k=top_k,
                domain=domain,
                content_type=content_type,
                org_id=org_id
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
    
    def get_content_chunks(self, content_id: str, org_id: str) -> List[ChunkResponse]:
        """Get all chunks for a specific content"""
        try:
            chunks = self.db.get_content_chunks(content_id, org_id)
            
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
    
    def process_content_for_rag(self, content_id: str, org_id: str) -> bool:
        """Process content into chunks for RAG"""
        try:
            # 🆕 ADD: Track content addition for RAG optimization
            try:
                from automated_rag_integration import RAGIntegrationHooks
                
                # Notify RAG system of content processing
                rag_result = RAGIntegrationHooks.on_content_added(org_id, 1)  # 1 new processed item
                
                if rag_result['status'] == 'processing':
                    logger.info(f"🚀 RAG optimization triggered during content processing for org {org_id}")
                    
            except Exception as e:
                logger.warning(f"⚠️ RAG content tracking failed for org {org_id}: {e}")
                # Don't fail content processing if RAG tracking fails
            
            return self.rag_system.process_content_for_rag(content_id, org_id)
            
        except Exception as e:
            logger.error(f"Failed to process content for RAG: {e}")
            return False
    
    def generate_content(
        self,
        query: str,
        platform: str,
        tone: str,
        domain: Optional[str] = None,
        content_type: Optional[str] = None,
        top_k: int = 5,
        org_id: str = None
    ) -> GeneratedContent:
        """
        Generate content using RAG.
        Enhanced with lazy RAG optimization.
        """
        try:
            # 🆕 ADD: Ensure org is optimized before generating content
            try:
                from automated_rag_integration import RAGIntegrationHooks
                
                optimization_result = RAGIntegrationHooks.on_rag_query_requested(org_id, query)
                
                if optimization_result['status'] == 'processing':
                    logger.info(f"🔄 RAG optimization triggered for org {org_id} during content generation")
                    
            except Exception as e:
                logger.warning(f"⚠️ RAG optimization check failed for org {org_id}: {e}")
                # Continue with generation even if optimization check fails
            
            response = self.rag_system.process_and_generate(
                query=query,
                platform=platform,
                tone=tone,
                domain=domain,
                content_type=content_type,
                top_k=top_k,
                org_id=org_id
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
    def create_template(self, template_data: Dict[str, Any], org_id: str) -> str:
        """Create a new template"""
        template_id = str(uuid.uuid4())
        template_data["id"] = template_id
        template_data["org_id"] = org_id
        template_data["created_at"] = datetime.utcnow().isoformat()
        
        # Store in database (implement based on your database schema)
        # For now, we'll use a simple in-memory store
        if not hasattr(self, '_templates'):
            self._templates = {}
        
        self._templates[template_id] = template_data
        return template_id
    
    def get_template(self, template_id: str, org_id: str) -> Optional[MarketingTemplateResponse]:
        """Get a template by ID"""
        if hasattr(self, '_templates') and template_id in self._templates:
            template = self._templates[template_id]
            # Check if template belongs to the organization
            if template.get('org_id') == org_id:
                return MarketingTemplateResponse(**template)
        return None
    
    def list_templates(
        self,
        platform: Optional[str] = None,
        tone: Optional[str] = None,
        purpose: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
        org_id: str = None
    ) -> List[MarketingTemplateResponse]:
        """List templates with filters"""
        if not hasattr(self, '_templates'):
            self._templates = {}
        
        templates = list(self._templates.values())
        
        # Filter by organization first
        if org_id:
            templates = [t for t in templates if t.get("org_id") == org_id]
        
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
