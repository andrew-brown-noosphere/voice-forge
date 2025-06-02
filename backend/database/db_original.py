"""
Database interface implementation.
"""
import json
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from sqlalchemy import desc, func, cast, Float, or_, and_
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.exc import SQLAlchemyError
import uuid

from database.models import Crawl, Content, ContentChunk, MarketingTemplate
from api.models import CrawlStatus, CrawlState, CrawlProgress, ContentType, ContentMetadata

logger = logging.getLogger(__name__)

class Database:
    """Database interface for VoiceForge."""
    
    def __init__(self, session):
        """Initialize the database interface."""
        self.session = session
    
    def _ensure_session_health(self):
        """
        Ensure the session is in a healthy state for queries.
        This method attempts to recover from failed transactions.
        """
        try:
            # Test if the session is in a failed state
            from sqlalchemy.sql.expression import text
            self.session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.warning(f"Session unhealthy, attempting rollback: {str(e)}")
            try:
                # Rollback the failed transaction
                self.session.rollback()
                # Test again after rollback
                self.session.execute(text("SELECT 1"))
                logger.info("Session recovered after rollback")
                return True
            except Exception as rollback_error:
                logger.error(f"Failed to recover session: {str(rollback_error)}")
                # Session is completely unusable at this point
                return False
    
    def _safe_execute(self, operation_name: str, operation_func, *args, **kwargs):
        """
        Safely execute a database operation with proper error handling.
        
        Args:
            operation_name: Name of the operation for logging
            operation_func: The function to execute
            *args, **kwargs: Arguments to pass to the function
            
        Returns:
            Result of the operation, or None if failed
        """
        try:
            # Ensure session is healthy before operation
            if not self._ensure_session_health():
                logger.error(f"Cannot execute {operation_name}: session is unhealthy")
                return None
            
            # Execute the operation
            result = operation_func(*args, **kwargs)
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemy error in {operation_name}: {str(e)}")
            try:
                self.session.rollback()
            except Exception as rollback_error:
                logger.error(f"Failed to rollback after {operation_name}: {str(rollback_error)}")
            return None
            
        except Exception as e:
            logger.error(f"Unexpected error in {operation_name}: {str(e)}")
            try:
                self.session.rollback()
            except Exception as rollback_error:
                logger.error(f"Failed to rollback after {operation_name}: {str(rollback_error)}")
            return None
    
    def save_crawl_status(self, status: CrawlStatus, org_id: str):
        """Save a new crawl status to the database."""
        crawl = Crawl(
            id=status.crawl_id,
            org_id=org_id,
            domain=status.domain,
            state=status.state,
            start_time=status.start_time,
            end_time=status.end_time,
            error=status.error,
            config=json.loads(status.config.json()),
            pages_crawled=status.progress.pages_crawled,
            pages_discovered=status.progress.pages_discovered,
            pages_failed=status.progress.pages_failed,
            current_depth=status.progress.current_depth,
            content_extracted=status.progress.content_extracted
        )
        
        self.session.add(crawl)
        self.session.commit()
    
    def update_crawl_status(self, status: CrawlStatus, org_id: str = None):
        """Update an existing crawl status in the database."""
        crawl = self.session.query(Crawl).filter(Crawl.id == status.crawl_id)
        
        # If org_id is provided, filter by it for security
        if org_id:
            crawl = crawl.filter(Crawl.org_id == org_id)
            
        crawl = crawl.first()
        
        if not crawl:
            # If crawl doesn't exist, create it
            if org_id:
                return self.save_crawl_status(status, org_id)
            else:
                # Fallback: try to save without org_id (this shouldn't happen in multi-tenant mode)
                logger.warning(f"Creating crawl status without org_id for {status.crawl_id}")
                return
        
        crawl.state = status.state
        crawl.start_time = status.start_time
        crawl.end_time = status.end_time
        crawl.error = status.error
        crawl.config = json.loads(status.config.json())
        crawl.pages_crawled = status.progress.pages_crawled
        crawl.pages_discovered = status.progress.pages_discovered
        crawl.pages_failed = status.progress.pages_failed
        crawl.current_depth = status.progress.current_depth
        crawl.content_extracted = status.progress.content_extracted
        
        self.session.commit()
    
    def get_crawl_status(self, crawl_id: str, org_id: str) -> Optional[CrawlStatus]:
        """Get a crawl status from the database."""
        crawl = self.session.query(Crawl).filter(
            Crawl.id == crawl_id,
            Crawl.org_id == org_id
        ).first()
        
        if not crawl:
            return None
        
        return CrawlStatus(
            crawl_id=crawl.id,
            domain=crawl.domain,
            state=CrawlState(crawl.state),
            progress=CrawlProgress(
                pages_crawled=crawl.pages_crawled,
                pages_discovered=crawl.pages_discovered,
                pages_failed=crawl.pages_failed,
                current_depth=crawl.current_depth,
                content_extracted=crawl.content_extracted
            ),
            start_time=crawl.start_time,
            end_time=crawl.end_time,
            error=crawl.error,
            config=json.loads(json.dumps(crawl.config))
        )
    
    def list_crawl_statuses(self, limit: int, offset: int, org_id: str) -> List[CrawlStatus]:
        """List all crawl statuses with pagination."""
        crawls = self.session.query(Crawl) \
            .filter(Crawl.org_id == org_id) \
            .order_by(desc(Crawl.start_time)) \
            .limit(limit) \
            .offset(offset) \
            .all()
        
        return [
            CrawlStatus(
                crawl_id=crawl.id,
                domain=crawl.domain,
                state=CrawlState(crawl.state),
                progress=CrawlProgress(
                    pages_crawled=crawl.pages_crawled,
                    pages_discovered=crawl.pages_discovered,
                    pages_failed=crawl.pages_failed,
                    current_depth=crawl.current_depth,
                    content_extracted=crawl.content_extracted
                ),
                start_time=crawl.start_time,
                end_time=crawl.end_time,
                error=crawl.error,
                config=json.loads(json.dumps(crawl.config))
            )
            for crawl in crawls
        ]
    
    def save_content(self, content_data: Dict[str, Any], org_id: str):
        """Save content to the database."""
        metadata = content_data["metadata"]
        
        content = Content(
            id=content_data["content_id"],
            org_id=org_id,
            url=content_data["url"],
            domain=content_data["domain"],
            text=content_data["text"],
            html=content_data.get("html"),
            crawl_id=content_data["crawl_id"],
            extracted_at=content_data["extracted_at"],
            title=metadata.title,
            author=metadata.author,
            publication_date=metadata.publication_date,
            last_modified=metadata.last_modified,
            categories=metadata.categories,
            tags=metadata.tags,
            language=metadata.language,
            content_type=metadata.content_type
        )
        
        self.session.add(content)
        self.session.commit()
    
    def get_content(self, content_id: str, org_id: str) -> Optional[Dict[str, Any]]:
        """Get content by ID."""
        content = self.session.query(Content).filter(
            Content.id == content_id,
            Content.org_id == org_id
        ).first()
        
        if not content:
            return None
        
        return {
            "content_id": content.id,
            "url": content.url,
            "domain": content.domain,
            "text": content.text,
            "html": content.html,
            "metadata": ContentMetadata(
                title=content.title,
                author=content.author,
                publication_date=content.publication_date,
                last_modified=content.last_modified,
                categories=content.categories,
                tags=content.tags,
                language=content.language,
                content_type=ContentType(content.content_type)
            ),
            "relevance_score": None,
            "crawl_id": content.crawl_id,
            "extracted_at": content.extracted_at
        }
    
    def update_content_processing(self, content_id: str, entities: List[Dict], embedding: List[float]):
        """Update content with processing results."""
        content = self.session.query(Content).filter(Content.id == content_id).first()
        
        if not content:
            return
        
        content.is_processed = True
        content.entities = entities
        content.embedding = embedding
        
        self.session.commit()
    
    def search_content_by_vector(
        self,
        query_embedding: List[float],
        domain: Optional[str] = None,
        content_type: Optional[ContentType] = None,
        limit: int = 10,
        offset: int = 0,
        org_id: str = None
    ) -> List[Dict[str, Any]]:
        """
        Search for content using vector similarity.
        
        Args:
            query_embedding: The query embedding vector
            domain: Filter by domain
            content_type: Filter by content type
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of content dictionaries with relevance scores
        """
        def _search_operation():
            query = self.session.query(Content)
            
            # Apply organization filter first
            if org_id:
                query = query.filter(Content.org_id == org_id)
            
            # Apply filters
            if domain:
                query = query.filter(Content.domain == domain)
            
            if content_type:
                query = query.filter(Content.content_type == content_type.value)
            
            # Add pagination
            query = query.limit(limit).offset(offset)
            
            # Execute query
            results = query.all()
            
            # Calculate similarities in Python
            content_results = []
            for content in results:
                try:
                    # Calculate similarity if both embeddings exist
                    if content.embedding and query_embedding:
                        from sklearn.metrics.pairwise import cosine_similarity
                        import numpy as np
                        
                        similarity_score = cosine_similarity(
                            [np.array(query_embedding)],
                            [np.array(content.embedding)]
                        )[0][0]
                    else:
                        similarity_score = 0.0  # Default score for content without embeddings
                except Exception as e:
                    logger.debug(f"Error calculating similarity: {str(e)}")
                    similarity_score = 0.0  # Default score on error
                
                # Always include the content
                content_results.append({
                    "content_id": content.id,
                    "url": content.url,
                    "domain": content.domain,
                    "text": content.text,
                    "html": content.html,
                    "metadata": ContentMetadata(
                        title=content.title,
                        author=content.author,
                        publication_date=content.publication_date,
                        last_modified=content.last_modified,
                        categories=content.categories,
                        tags=content.tags,
                        language=content.language,
                        content_type=ContentType(content.content_type)
                    ),
                    "relevance_score": float(similarity_score),
                    "crawl_id": content.crawl_id,
                    "extracted_at": content.extracted_at
                })
            
            return content_results
        
        result = self._safe_execute("search_content_by_vector", _search_operation)
        return result if result is not None else []
    
    def get_all_domains(self, org_id: str) -> List[str]:
        """Get all domains that have been crawled."""
        def _get_domains_operation():
            domains = self.session.query(Content.domain).filter(
                Content.org_id == org_id
            ).distinct().all()
            domain_list = [domain[0] for domain in domains]
            if domain_list:
                logger.debug(f"Found {len(domain_list)} domains for org {org_id}")
            else:
                logger.debug(f"No domains found for org {org_id}")
            return domain_list
        
        result = self._safe_execute("get_all_domains", _get_domains_operation)
        return result if result is not None else []
    
    # New RAG-specific methods
    
    def store_content_chunks(self, chunks: List[Dict[str, Any]], org_id: str):
        """
        Store content chunks in the database.
        
        Args:
            chunks: List of chunk dictionaries
        """
        chunk_objects = []
        for chunk in chunks:
            chunk_object = ContentChunk(
                id=chunk["id"],
                org_id=org_id,
                content_id=chunk["content_id"],
                chunk_index=chunk["chunk_index"],
                text=chunk["text"],
                start_char=chunk["start_char"],
                end_char=chunk["end_char"],
                embedding=chunk.get("embedding"),
                chunk_metadata=chunk.get("chunk_metadata", {})
            )
            chunk_objects.append(chunk_object)
        
        self.session.add_all(chunk_objects)
        self.session.commit()
    
    def search_chunks_by_vector(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        domain: Optional[str] = None,
        content_type: Optional[str] = None,
        org_id: str = None
    ) -> List[Dict[str, Any]]:
        """
        Search for content chunks using vector similarity.
        
        Args:
            query_embedding: The query embedding vector
            top_k: Maximum number of results
            domain: Filter by domain
            content_type: Filter by content type
            
        Returns:
            List of chunk dictionaries with similarity scores
        """
        def _search_chunks_operation():
            query = self.session.query(ContentChunk)
            
            # Apply organization filter first
            if org_id:
                query = query.filter(ContentChunk.org_id == org_id)
            
            # Apply filters through joins
            if domain or content_type:
                query = query.join(Content, ContentChunk.content_id == Content.id)
                
                if domain:
                    query = query.filter(Content.domain == domain)
                
                if content_type:
                    query = query.filter(Content.content_type == content_type)
            
            # Limit results
            query = query.limit(top_k)
            
            # Execute query
            results = query.all()
            
            # Convert to dictionaries with similarity scores
            chunk_results = []
            for chunk in results:
                try:
                    from sklearn.metrics.pairwise import cosine_similarity
                    import numpy as np
                    
                    if chunk.embedding and query_embedding:
                        similarity_score = cosine_similarity(
                            [np.array(query_embedding)],
                            [np.array(chunk.embedding)]
                        )[0][0]
                    else:
                        similarity_score = 0.0  # Default score if embeddings are missing
                    
                    chunk_results.append({
                        "id": chunk.id,
                        "content_id": chunk.content_id,
                        "chunk_index": chunk.chunk_index,
                        "text": chunk.text,
                        "start_char": chunk.start_char,
                        "end_char": chunk.end_char,
                        "metadata": chunk.chunk_metadata,
                        "similarity": float(similarity_score)
                    })
                except Exception as e:
                    logger.error(f"Error processing chunk {chunk.id}: {str(e)}")
                    # Still include the chunk, just without a similarity score
                    chunk_results.append({
                        "id": chunk.id,
                        "content_id": chunk.content_id,
                        "chunk_index": chunk.chunk_index,
                        "text": chunk.text,
                        "start_char": chunk.start_char,
                        "end_char": chunk.end_char,
                        "metadata": chunk.chunk_metadata,
                        "similarity": 0.0
                    })
            
            return chunk_results
        
        result = self._safe_execute("search_chunks_by_vector", _search_chunks_operation)
        return result if result is not None else []
    
    def search_chunks_by_text(
        self,
        query: str,
        top_k: int = 5,
        domain: Optional[str] = None,
        content_type: Optional[str] = None,
        org_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for content chunks using text search with multi-tenant support.
        This is a fallback for when vector search doesn't work.
        
        Args:
            query: The search query text
            top_k: Maximum number of results
            domain: Filter by domain
            content_type: Filter by content type
            org_id: Organization ID for multi-tenant isolation
            
        Returns:
            List of chunk dictionaries with similarity scores
        """
        def _text_search_operation():
            # Prepare the search query
            search_terms = [term.strip().lower() for term in query.split() if term.strip()]
            
            if not search_terms:
                return []
            
            # Build base query
            query_obj = self.session.query(ContentChunk)
            
            # Apply organization filter first
            if org_id:
                query_obj = query_obj.filter(ContentChunk.org_id == org_id)
            
            # Apply filters through joins if needed
            if domain or content_type:
                query_obj = query_obj.join(Content, ContentChunk.content_id == Content.id)
                
                if domain:
                    query_obj = query_obj.filter(Content.domain == domain)
                
                if content_type:
                    query_obj = query_obj.filter(Content.content_type == content_type)
            
            # Add text search conditions
            if search_terms:
                from sqlalchemy import or_
                conditions = []
                for term in search_terms:
                    # Add condition for text column with ILIKE (case-insensitive)
                    conditions.append(ContentChunk.text.ilike(f'%{term}%'))
                
                if conditions:
                    query_obj = query_obj.filter(or_(*conditions))
            
            # Limit results to prevent excessive loading
            results = query_obj.limit(top_k * 2).all()  # Get more than needed to score and filter
            
            # Convert to dictionaries with calculated similarity scores
            chunk_results = []
            
            for chunk in results:
                # Calculate a score based on number of terms found in text
                score = 0.0
                if search_terms:
                    chunk_text = chunk.text.lower()
                    term_count = 0
                    
                    for term in search_terms:
                        if term in chunk_text:
                            term_count += 1
                    
                    # Score based on percentage of terms found
                    score = min(1.0, term_count / len(search_terms))  # Normalize to [0, 1]
                
                # Only add if score is positive (some term was found)
                if score > 0:
                    chunk_results.append({
                        "id": chunk.id,
                        "content_id": chunk.content_id,
                        "chunk_index": chunk.chunk_index,
                        "text": chunk.text,
                        "start_char": chunk.start_char,
                        "end_char": chunk.end_char,
                        "metadata": chunk.chunk_metadata,
                        "similarity": score
                    })
            
            # Sort by score and limit to top_k
            chunk_results.sort(key=lambda x: x["similarity"], reverse=True)
            return chunk_results[:top_k]
        
        result = self._safe_execute("search_chunks_by_text", _text_search_operation)
        return result if result is not None else []
    
    def check_content_exists(
        self,
        domain: Optional[str] = None,
        content_type: Optional[str] = None,
    ) -> bool:
        """
        Check if any content exists with the given filters.
        
        Args:
            domain: Filter by domain
            content_type: Filter by content type
            
        Returns:
            True if content exists, False otherwise
        """
        try:
            query = self.session.query(Content)
            
            if domain:
                query = query.filter(Content.domain == domain)
            
            if content_type:
                query = query.filter(Content.content_type == content_type)
            
            # Just check if any content exists
            return self.session.query(query.exists()).scalar()
        except Exception as e:
            print(f"Error checking if content exists: {str(e)}")
            return False
    
    def get_content_chunks(self, content_id: str, org_id: str) -> List[Dict[str, Any]]:
        """
        Get all chunks for a specific content.
        
        Args:
            content_id: Content ID
            
        Returns:
            List of chunk dictionaries
        """
        chunks = self.session.query(ContentChunk) \
            .filter(
                ContentChunk.content_id == content_id,
                ContentChunk.org_id == org_id
            ) \
            .order_by(ContentChunk.chunk_index) \
            .all()
        
        return [
            {
                "id": chunk.id,
                "content_id": chunk.content_id,
                "chunk_index": chunk.chunk_index,
                "text": chunk.text,
                "start_char": chunk.start_char,
                "end_char": chunk.end_char,
                "metadata": chunk.chunk_metadata
            }
            for chunk in chunks
        ]
    

    def store_template(self, template_data: Dict[str, Any], org_id: str) -> str:
        """
        Store a marketing template in the database.
        
        Args:
            template_data: Template data
            
        Returns:
            Template ID
        """
        template_id = template_data.get("id", str(uuid.uuid4()))
        
        template = MarketingTemplate(
            id=template_id,
            org_id=org_id,
            name=template_data["name"],
            description=template_data.get("description"),
            template_text=template_data["template_text"],
            platform=template_data["platform"],
            tone=template_data["tone"],
            purpose=template_data["purpose"],
            parameters=template_data.get("parameters", []),
            created_at=datetime.utcnow(),
            created_by=template_data.get("created_by")
        )
        
        self.session.add(template)
        self.session.commit()
        
        return template_id
    
    def get_template(
        self,
        template_id: Optional[str] = None,
        platform: Optional[str] = None,
        tone: Optional[str] = None,
        purpose: Optional[str] = None,
        org_id: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get a marketing template.
        
        Args:
            template_id: Optional template ID
            platform: Optional platform filter
            tone: Optional tone filter
            purpose: Optional purpose filter
            
        Returns:
            Template dictionary or None if not found
        """
        query = self.session.query(MarketingTemplate)
        
        # Apply organization filter first
        if org_id:
            query = query.filter(MarketingTemplate.org_id == org_id)
        
        if template_id:
            query = query.filter(MarketingTemplate.id == template_id)
        else:
            # Apply filters
            if platform:
                query = query.filter(MarketingTemplate.platform == platform)
            
            if tone:
                query = query.filter(MarketingTemplate.tone == tone)
            
            if purpose:
                query = query.filter(MarketingTemplate.purpose == purpose)
        
        template = query.first()
        
        if not template:
            return None
        
        return {
            "id": template.id,
            "name": template.name,
            "description": template.description,
            "template_text": template.template_text,
            "platform": template.platform,
            "tone": template.tone,
            "purpose": template.purpose,
            "parameters": template.parameters,
            "created_at": template.created_at,
            "updated_at": template.updated_at,
            "created_by": template.created_by
        }
    
    def list_templates(
        self,
        platform: Optional[str] = None,
        tone: Optional[str] = None,
        purpose: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
        org_id: str = None
    ) -> List[Dict[str, Any]]:
        """
        List marketing templates with filters.
        
        Args:
            platform: Optional platform filter
            tone: Optional tone filter
            purpose: Optional purpose filter
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of template dictionaries
        """
        query = self.session.query(MarketingTemplate)
        
        # Apply organization filter first
        if org_id:
            query = query.filter(MarketingTemplate.org_id == org_id)
        
        # Apply filters
        if platform:
            query = query.filter(MarketingTemplate.platform == platform)
        
        if tone:
            query = query.filter(MarketingTemplate.tone == tone)
        
        if purpose:
            query = query.filter(MarketingTemplate.purpose == purpose)
        
        templates = query.order_by(desc(MarketingTemplate.created_at)).limit(limit).offset(offset).all()
        
        return [
            {
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "template_text": template.template_text,
                "platform": template.platform,
                "tone": template.tone,
                "purpose": template.purpose,
                "parameters": template.parameters,
                "created_at": template.created_at,
                "updated_at": template.updated_at,
                "created_by": template.created_by
            }
            for template in templates
        ]
