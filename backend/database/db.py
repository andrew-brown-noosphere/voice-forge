"""
Database interface implementation with improved transaction error handling.
"""
import json
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from sqlalchemy import desc, func, cast, Float, or_, and_
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.exc import SQLAlchemyError
import uuid

from database.models import Crawl, Content, ContentChunk, MarketingTemplate, RedditSignal, SignalResponse
from api.models import CrawlStatus, CrawlState, CrawlProgress, ContentType, ContentMetadata

logger = logging.getLogger(__name__)

class Database:
    """Database interface for VoiceForge with improved error handling."""
    
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
        def _save_operation():
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
            return True
        
        return self._safe_execute("save_crawl_status", _save_operation)
    
    def update_crawl_status(self, status: CrawlStatus, org_id: str = None):
        """Update an existing crawl status in the database."""
        def _update_operation():
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
                    logger.warning(f"Creating crawl status without org_id for {status.crawl_id}")
                    return None
            
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
            return True
        
        return self._safe_execute("update_crawl_status", _update_operation)
    
    def get_crawl_status(self, crawl_id: str, org_id: str) -> Optional[CrawlStatus]:
        """Get a crawl status from the database."""
        def _get_operation():
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
        
        return self._safe_execute("get_crawl_status", _get_operation)
    
    def list_crawl_statuses(self, limit: int, offset: int, org_id: str) -> List[CrawlStatus]:
        """List all crawl statuses with pagination."""
        def _list_operation():
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
        
        result = self._safe_execute("list_crawl_statuses", _list_operation)
        return result if result is not None else []
    
    def save_content(self, content_data: Dict[str, Any], org_id: str):
        """Save content to the database."""
        def _save_content_operation():
            metadata = content_data["metadata"]
            
            # Handle metadata as either dict or object with proper fallbacks
            def get_metadata_value(key, default=None):
                if isinstance(metadata, dict):
                    return metadata.get(key, default)
                else:
                    return getattr(metadata, key, default)
            
            content = Content(
                id=content_data["content_id"],
                org_id=org_id,
                url=content_data["url"],
                domain=content_data["domain"],
                text=content_data["text"],
                html=content_data.get("html"),
                crawl_id=content_data["crawl_id"],
                extracted_at=content_data["extracted_at"],
                title=get_metadata_value("title", ""),
                author=get_metadata_value("author"),
                publication_date=get_metadata_value("publication_date"),
                last_modified=get_metadata_value("last_modified"),
                categories=get_metadata_value("categories", []),
                tags=get_metadata_value("tags", []),
                language=get_metadata_value("language", "en"),
                content_type=get_metadata_value("content_type", "webpage")
            )
            
            self.session.add(content)
            self.session.commit()
            return True
        
        return self._safe_execute("save_content", _save_content_operation)
    
    def get_content(self, content_id: str, org_id: str) -> Optional[Dict[str, Any]]:
        """Get content by ID."""
        def _get_content_operation():
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
        
        return self._safe_execute("get_content", _get_content_operation)
    
    def update_content_processing(self, content_id: str, entities: List[Dict], embedding: List[float]):
        """Update content with processing results."""
        def _update_processing_operation():
            content = self.session.query(Content).filter(Content.id == content_id).first()
            
            if not content:
                return False
            
            content.is_processed = True
            content.entities = entities
            content.embedding = embedding
            
            self.session.commit()
            return True
        
        return self._safe_execute("update_content_processing", _update_processing_operation)
    
    def search_content_by_vector(
        self,
        query_embedding: List[float],
        domain: Optional[str] = None,
        content_type: Optional[ContentType] = None,
        limit: int = 10,
        offset: int = 0,
        org_id: str = None
    ) -> List[Dict[str, Any]]:
        """Search for content using vector similarity with improved error handling."""
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
                        similarity_score = 0.0
                except Exception as e:
                    logger.debug(f"Error calculating similarity: {str(e)}")
                    similarity_score = 0.0
                
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
    
    def store_content_chunks(self, chunks: List[Dict[str, Any]], org_id: str):
        """Store content chunks in the database."""
        def _store_chunks_operation():
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
            return True
        
        return self._safe_execute("store_content_chunks", _store_chunks_operation)
    
    def search_chunks_by_vector(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        domain: Optional[str] = None,
        content_type: Optional[str] = None,
        org_id: str = None
    ) -> List[Dict[str, Any]]:
        """Search for content chunks using vector similarity with improved error handling."""
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
            
            # Limit results to prevent excessive loading
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
        """Search for content chunks using text search with multi-tenant support."""
        def _search_text_operation():
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
        
        result = self._safe_execute("search_chunks_by_text", _search_text_operation)
        return result if result is not None else []    
    
    def check_content_exists(
        self,
        domain: Optional[str] = None,
        content_type: Optional[str] = None,
    ) -> bool:
        """Check if any content exists with the given filters."""
        def _check_exists_operation():
            query = self.session.query(Content)
            
            if domain:
                query = query.filter(Content.domain == domain)
            
            if content_type:
                query = query.filter(Content.content_type == content_type)
            
            # Just check if any content exists
            return self.session.query(query.exists()).scalar()
        
        result = self._safe_execute("check_content_exists", _check_exists_operation)
        return result if result is not None else False
    
    def get_content_chunks(self, content_id: str, org_id: str) -> List[Dict[str, Any]]:
        """Get all chunks for a specific content."""
        def _get_chunks_operation():
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
        
        result = self._safe_execute("get_content_chunks", _get_chunks_operation)
        return result if result is not None else []

    def store_template(self, template_data: Dict[str, Any], org_id: str) -> str:
        """Store a marketing template in the database."""
        def _store_template_operation():
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
        
        result = self._safe_execute("store_template", _store_template_operation)
        return result if result is not None else str(uuid.uuid4())
    
    def get_template(
        self,
        template_id: Optional[str] = None,
        platform: Optional[str] = None,
        tone: Optional[str] = None,
        purpose: Optional[str] = None,
        org_id: str = None
    ) -> Optional[Dict[str, Any]]:
        """Get a marketing template."""
        def _get_template_operation():
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
        
        return self._safe_execute("get_template", _get_template_operation)
    
    def list_templates(
        self,
        platform: Optional[str] = None,
        tone: Optional[str] = None,
        purpose: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
        org_id: str = None
    ) -> List[Dict[str, Any]]:
        """List marketing templates with filters."""
        def _list_templates_operation():
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
        
        result = self._safe_execute("list_templates", _list_templates_operation)
        return result if result is not None else []
    
    def store_reddit_signal(self, signal_data: Dict[str, Any]) -> bool:
        """Store a Reddit signal in the database."""
        def _store_signal_operation():
            signal = RedditSignal(
                signal_id=signal_data["signal_id"],
                org_id=signal_data["org_id"],
                platform=signal_data.get("platform", "reddit"),
                thread_id=signal_data["thread_id"],
                subreddit=signal_data["subreddit"],
                title=signal_data["title"],
                content=signal_data.get("content"),
                url=signal_data["url"],
                author=signal_data.get("author"),
                score=signal_data.get("score", 0),
                num_comments=signal_data.get("num_comments", 0),
                created_at=signal_data["created_at"],
                relevance_score=signal_data["relevance_score"],
                signal_type=signal_data["signal_type"],
                engagement_potential=signal_data["engagement_potential"],
                top_comments=signal_data.get("top_comments", []),
                discovered_at=signal_data.get("discovered_at", datetime.utcnow()),
                status=signal_data.get("status", "active"),
                signal_metadata=signal_data.get("metadata", {})
            )
            
            self.session.add(signal)
            self.session.commit()
            return True
        
        result = self._safe_execute("store_reddit_signal", _store_signal_operation)
        return result if result is not None else False
    
    def get_reddit_signal(self, signal_id: str, org_id: str) -> Optional[Dict[str, Any]]:
        """Get a Reddit signal by ID."""
        def _get_signal_operation():
            signal = self.session.query(RedditSignal).filter(
                RedditSignal.signal_id == signal_id,
                RedditSignal.org_id == org_id
            ).first()
            
            if not signal:
                return None
            
            return {
                "signal_id": signal.signal_id,
                "thread_id": signal.thread_id,
                "subreddit": signal.subreddit,
                "title": signal.title,
                "content": signal.content,
                "url": signal.url,
                "author": signal.author,
                "score": signal.score,
                "num_comments": signal.num_comments,
                "created_at": signal.created_at,
                "relevance_score": signal.relevance_score,
                "signal_type": signal.signal_type,
                "engagement_potential": signal.engagement_potential,
                "top_comments": signal.top_comments or [],
                "discovered_at": signal.discovered_at,
                "status": signal.status,
                "metadata": signal.signal_metadata or {}
            }
        
        return self._safe_execute("get_reddit_signal", _get_signal_operation)
    
    def list_reddit_signals(
        self,
        org_id: str,
        limit: int = 20,
        offset: int = 0,
        signal_type: Optional[str] = None,
        subreddit: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List Reddit signals with filtering."""
        def _list_signals_operation():
            query = self.session.query(RedditSignal).filter(
                RedditSignal.org_id == org_id
            )
            
            # Apply filters
            if signal_type:
                query = query.filter(RedditSignal.signal_type == signal_type)
            
            if subreddit:
                query = query.filter(RedditSignal.subreddit == subreddit)
            
            signals = query.order_by(desc(RedditSignal.discovered_at)).limit(limit).offset(offset).all()
            
            return [
                {
                    "signal_id": signal.signal_id,
                    "thread_id": signal.thread_id,
                    "subreddit": signal.subreddit,
                    "title": signal.title,
                    "content": signal.content,
                    "url": signal.url,
                    "author": signal.author,
                    "score": signal.score,
                    "num_comments": signal.num_comments,
                    "created_at": signal.created_at,
                    "relevance_score": signal.relevance_score,
                    "signal_type": signal.signal_type,
                    "engagement_potential": signal.engagement_potential,
                    "top_comments": signal.top_comments or [],
                    "discovered_at": signal.discovered_at,
                    "status": signal.status,
                    "metadata": signal.signal_metadata or {}
                }
                for signal in signals
            ]
        
        result = self._safe_execute("list_reddit_signals", _list_signals_operation)
        return result if result is not None else []
    
    def store_signal_response(self, response_data: Dict[str, Any]) -> bool:
        """Store a generated signal response."""
        def _store_response_operation():
            response_id = response_data.get("response_id", str(uuid.uuid4()))
            
            response = SignalResponse(
                response_id=response_id,
                signal_id=response_data["signal_id"],
                org_id=response_data["org_id"],
                generated_content=response_data["generated_content"],
                response_type=response_data["response_type"],
                platform=response_data["platform"],
                tone=response_data["tone"],
                confidence_score=response_data["confidence_score"],
                response_metadata=response_data.get("metadata", {}),
                generated_at=response_data.get("generated_at", datetime.utcnow()),
                status=response_data.get("status", "generated"),
                published_at=response_data.get("published_at"),
                engagement_metrics=response_data.get("engagement_metrics", {})
            )
            
            self.session.add(response)
            self.session.commit()
            return True
        
        result = self._safe_execute("store_signal_response", _store_response_operation)
        return result if result is not None else False
    
    # ============================================================================
    # ABSTRACTED SIGNALS SYSTEM METHODS
    # ============================================================================
    
    def store_signal(self, signal_data: Dict[str, Any]) -> bool:
        """Store a signal from any platform in the database."""
        def _store_signal_operation():
            # Import here to avoid circular imports
            from database.models import Signal
            
            signal = Signal(
                signal_id=signal_data["signal_id"],
                org_id=signal_data["org_id"],
                platform=signal_data["platform"],
                platform_id=signal_data["platform_id"],
                title=signal_data["title"],
                content=signal_data.get("content"),
                url=signal_data["url"],
                author=signal_data.get("author"),
                author_url=signal_data.get("author_url"),
                created_at=signal_data["created_at"],
                discovered_at=signal_data.get("discovered_at", datetime.utcnow()),
                signal_type=signal_data["signal_type"],
                relevance_score=signal_data["relevance_score"],
                engagement_potential=signal_data["engagement_potential"],
                sentiment_score=signal_data.get("sentiment_score"),
                status=signal_data.get("status", "active"),
                platform_metadata=signal_data.get("platform_metadata", {}),
                keywords_matched=signal_data.get("keywords_matched", []),
                engagement_metrics=signal_data.get("engagement_metrics", {})
            )
            
            self.session.add(signal)
            self.session.commit()
            return True
        
        result = self._safe_execute("store_signal", _store_signal_operation)
        return result if result is not None else False
    
    def get_signal(self, signal_id: str, org_id: str) -> Optional[Dict[str, Any]]:
        """Get a signal by ID."""
        def _get_signal_operation():
            from database.models import Signal
            
            signal = self.session.query(Signal).filter(
                Signal.signal_id == signal_id,
                Signal.org_id == org_id
            ).first()
            
            if not signal:
                return None
            
            return {
                "signal_id": signal.signal_id,
                "org_id": signal.org_id,
                "platform": signal.platform,
                "platform_id": signal.platform_id,
                "title": signal.title,
                "content": signal.content,
                "url": signal.url,
                "author": signal.author,
                "author_url": signal.author_url,
                "created_at": signal.created_at,
                "discovered_at": signal.discovered_at,
                "signal_type": signal.signal_type,
                "relevance_score": signal.relevance_score,
                "engagement_potential": signal.engagement_potential,
                "sentiment_score": signal.sentiment_score,
                "status": signal.status,
                "platform_metadata": signal.platform_metadata or {},
                "keywords_matched": signal.keywords_matched or [],
                "engagement_metrics": signal.engagement_metrics or {}
            }
        
        return self._safe_execute("get_signal", _get_signal_operation)
    
    def list_signals(
        self,
        org_id: str,
        limit: int = 20,
        offset: int = 0,
        platform: Optional[str] = None,
        signal_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List signals with filtering."""
        def _list_signals_operation():
            from database.models import Signal
            
            query = self.session.query(Signal).filter(
                Signal.org_id == org_id
            )
            
            # Apply filters
            if platform:
                query = query.filter(Signal.platform == platform)
            
            if signal_type:
                query = query.filter(Signal.signal_type == signal_type)
            
            if status:
                query = query.filter(Signal.status == status)
            
            signals = query.order_by(desc(Signal.discovered_at)).limit(limit).offset(offset).all()
            
            return [
                {
                    "signal_id": signal.signal_id,
                    "org_id": signal.org_id,
                    "platform": signal.platform,
                    "platform_id": signal.platform_id,
                    "title": signal.title,
                    "content": signal.content,
                    "url": signal.url,
                    "author": signal.author,
                    "author_url": signal.author_url,
                    "created_at": signal.created_at,
                    "discovered_at": signal.discovered_at,
                    "signal_type": signal.signal_type,
                    "relevance_score": signal.relevance_score,
                    "engagement_potential": signal.engagement_potential,
                    "sentiment_score": signal.sentiment_score,
                    "status": signal.status,
                    "platform_metadata": signal.platform_metadata or {},
                    "keywords_matched": signal.keywords_matched or [],
                    "engagement_metrics": signal.engagement_metrics or {}
                }
                for signal in signals
            ]
        
        result = self._safe_execute("list_signals", _list_signals_operation)
        return result if result is not None else []
    
    def store_signal_source(self, source_data: Dict[str, Any]) -> bool:
        """Store a signal monitoring source configuration."""
        def _store_source_operation():
            from database.models import SignalSource
            
            source = SignalSource(
                source_id=source_data.get("source_id", str(uuid.uuid4())),
                org_id=source_data["org_id"],
                platform=source_data["platform"],
                source_name=source_data["source_name"],
                source_type=source_data["source_type"],
                keywords=source_data["keywords"],
                is_active=source_data.get("is_active", True),
                last_crawled_at=source_data.get("last_crawled_at"),
                crawl_frequency=source_data.get("crawl_frequency", "daily"),
                relevance_threshold=source_data.get("relevance_threshold", 0.6),
                config=source_data.get("config", {}),
                created_at=source_data.get("created_at", datetime.utcnow()),
                updated_at=source_data.get("updated_at", datetime.utcnow())
            )
            
            self.session.add(source)
            self.session.commit()
            return True
        
        result = self._safe_execute("store_signal_source", _store_source_operation)
        return result if result is not None else False
    
    def list_signal_sources(
        self,
        org_id: str,
        platform: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """List signal monitoring sources."""
        def _list_sources_operation():
            from database.models import SignalSource
            
            query = self.session.query(SignalSource).filter(
                SignalSource.org_id == org_id
            )
            
            if platform:
                query = query.filter(SignalSource.platform == platform)
            
            if is_active is not None:
                query = query.filter(SignalSource.is_active == is_active)
            
            sources = query.order_by(desc(SignalSource.created_at)).all()
            
            return [
                {
                    "source_id": source.source_id,
                    "org_id": source.org_id,
                    "platform": source.platform,
                    "source_name": source.source_name,
                    "source_type": source.source_type,
                    "keywords": source.keywords or [],
                    "is_active": source.is_active,
                    "last_crawled_at": source.last_crawled_at,
                    "crawl_frequency": source.crawl_frequency,
                    "relevance_threshold": source.relevance_threshold,
                    "config": source.config or {},
                    "created_at": source.created_at,
                    "updated_at": source.updated_at
                }
                for source in sources
            ]
        
        result = self._safe_execute("list_signal_sources", _list_sources_operation)
        return result if result is not None else []
    
    def store_abstracted_signal_response(self, response_data: Dict[str, Any]) -> bool:
        """Store a generated signal response for the abstracted system."""
        def _store_response_operation():
            from database.models import SignalResponse
            
            response_id = response_data.get("response_id", str(uuid.uuid4()))
            
            response = SignalResponse(
                response_id=response_id,
                signal_id=response_data["signal_id"],
                org_id=response_data["org_id"],
                generated_content=response_data["generated_content"],
                response_type=response_data["response_type"],
                platform=response_data["platform"],
                tone=response_data["tone"],
                confidence_score=response_data["confidence_score"],
                response_metadata=response_data.get("response_metadata", {}),
                generated_at=response_data.get("generated_at", datetime.utcnow()),
                status=response_data.get("status", "generated"),
                published_at=response_data.get("published_at"),
                platform_response_id=response_data.get("platform_response_id"),
                engagement_metrics=response_data.get("engagement_metrics", {})
            )
            
            self.session.add(response)
            self.session.commit()
            return True
        
        result = self._safe_execute("store_abstracted_signal_response", _store_response_operation)
        return result if result is not None else False

    def get_signal_source(self, source_id: str, org_id: str) -> Optional[Dict[str, Any]]:
        """Get a signal source by ID"""
        def _get_source_operation():
            from database.models import SignalSource
            
            source = self.session.query(SignalSource).filter(
                SignalSource.source_id == source_id,
                SignalSource.org_id == org_id
            ).first()
            
            if not source:
                return None
            
            return {
                "source_id": source.source_id,
                "org_id": source.org_id,
                "platform": source.platform,
                "source_name": source.source_name,
                "keywords": source.keywords or [],
                "ai_suggested_keywords": source.ai_suggested_keywords or [],
                "business_context": source.business_context,
                "performance_metrics": source.performance_metrics or {}
            }
        
        return self._safe_execute("get_signal_source", _get_source_operation)

    def update_signal_source(self, source_id: str, org_id: str, updates: Dict[str, Any]) -> bool:
        """Update a signal source"""
        def _update_source_operation():
            from database.models import SignalSource
            
            source = self.session.query(SignalSource).filter(
                SignalSource.source_id == source_id,
                SignalSource.org_id == org_id
            ).first()
            
            if not source:
                return False
            
            for key, value in updates.items():
                if hasattr(source, key):
                    setattr(source, key, value)
            
            source.updated_at = datetime.utcnow()
            self.session.commit()
            return True
        
        return self._safe_execute("update_signal_source", _update_source_operation)
    
    # ============================================================================
    # PLATFORM CONFIGURATION METHODS
    # ============================================================================
    
    def store_platform_config(self, config_data: Dict[str, Any]) -> bool:
        """Store or update platform configuration"""
        def _store_config_operation():
            from database.models import PlatformConfiguration
            
            # Check if configuration already exists
            existing_config = self.session.query(PlatformConfiguration).filter(
                PlatformConfiguration.org_id == config_data["org_id"],
                PlatformConfiguration.platform == config_data["platform"]
            ).first()
            
            if existing_config:
                # Update existing configuration
                existing_config.configuration = config_data["config"]
                existing_config.updated_at = config_data.get("configured_at", datetime.utcnow())
                existing_config.configured_by = config_data.get("configured_by")
            else:
                # Create new configuration
                config_id = str(uuid.uuid4())
                new_config = PlatformConfiguration(
                    config_id=config_id,
                    org_id=config_data["org_id"],
                    platform=config_data["platform"],
                    configuration=config_data["config"],
                    configured_at=config_data.get("configured_at", datetime.utcnow()),
                    configured_by=config_data.get("configured_by"),
                    is_active=True
                )
                self.session.add(new_config)
            
            self.session.commit()
            return True
        
        result = self._safe_execute("store_platform_config", _store_config_operation)
        return result if result is not None else False
    
    def get_platform_config(self, org_id: str, platform: str) -> Optional[Dict[str, Any]]:
        """Get platform configuration for an organization"""
        def _get_config_operation():
            from database.models import PlatformConfiguration
            
            config = self.session.query(PlatformConfiguration).filter(
                PlatformConfiguration.org_id == org_id,
                PlatformConfiguration.platform == platform,
                PlatformConfiguration.is_active == True
            ).first()
            
            if not config:
                return None
            
            return config.configuration
        
        return self._safe_execute("get_platform_config", _get_config_operation)
    
    def list_platform_configs(self, org_id: str) -> List[Dict[str, Any]]:
        """List all platform configurations for an organization"""
        def _list_configs_operation():
            from database.models import PlatformConfiguration
            
            configs = self.session.query(PlatformConfiguration).filter(
                PlatformConfiguration.org_id == org_id,
                PlatformConfiguration.is_active == True
            ).all()
            
            return [
                {
                    "config_id": config.config_id,
                    "platform": config.platform,
                    "configured_at": config.configured_at,
                    "configured_by": config.configured_by,
                    "last_tested_at": config.last_tested_at,
                    "last_test_status": config.last_test_status,
                    "last_test_error": config.last_test_error,
                    "rate_limit_info": config.rate_limit_info or {},
                    "quota_usage": config.quota_usage or {}
                }
                for config in configs
            ]
        
        result = self._safe_execute("list_platform_configs", _list_configs_operation)
        return result if result is not None else []
    
    def update_platform_test_status(
        self, 
        org_id: str, 
        platform: str, 
        test_status: str, 
        test_error: Optional[str] = None
    ) -> bool:
        """Update platform test status and error information"""
        def _update_test_status_operation():
            from database.models import PlatformConfiguration
            
            config = self.session.query(PlatformConfiguration).filter(
                PlatformConfiguration.org_id == org_id,
                PlatformConfiguration.platform == platform,
                PlatformConfiguration.is_active == True
            ).first()
            
            if not config:
                return False
            
            config.last_tested_at = datetime.utcnow()
            config.last_test_status = test_status
            config.last_test_error = test_error
            
            self.session.commit()
            return True
        
        result = self._safe_execute("update_platform_test_status", _update_test_status_operation)
        return result if result is not None else False
    
    def delete_platform_config(self, org_id: str, platform: str) -> bool:
        """Delete (deactivate) a platform configuration"""
        def _delete_config_operation():
            from database.models import PlatformConfiguration
            
            config = self.session.query(PlatformConfiguration).filter(
                PlatformConfiguration.org_id == org_id,
                PlatformConfiguration.platform == platform
            ).first()
            
            if not config:
                return False
            
            # Soft delete by setting is_active to False
            config.is_active = False
            config.updated_at = datetime.utcnow()
            
            self.session.commit()
            return True
        
        result = self._safe_execute("delete_platform_config", _delete_config_operation)
        return result if result is not None else False
    
    def update_platform_rate_limits(
        self, 
        org_id: str, 
        platform: str, 
        rate_limit_info: Dict[str, Any]
    ) -> bool:
        """Update platform rate limit information"""
        def _update_rate_limits_operation():
            from database.models import PlatformConfiguration
            
            config = self.session.query(PlatformConfiguration).filter(
                PlatformConfiguration.org_id == org_id,
                PlatformConfiguration.platform == platform,
                PlatformConfiguration.is_active == True
            ).first()
            
            if not config:
                return False
            
            config.rate_limit_info = rate_limit_info
            config.updated_at = datetime.utcnow()
            
            self.session.commit()
            return True
        
        result = self._safe_execute("update_platform_rate_limits", _update_rate_limits_operation)
        return result if result is not None else False
    
    # ============================================================================
    # CONTENT SEARCH METHODS FOR AI SERVICES
    # ============================================================================
    
    def search_content(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search for content based on comprehensive query parameters.
        Used by ContentDrivenSignalAI to analyze VoiceForge content.
        
        Args:
            query: Dictionary containing search parameters:
                - org_id: Organization ID (required)
                - content_types: List of content types to include
                - limit: Maximum number of results
                - sort_by: Sorting criteria ('relevance', 'date')
                - min_length: Minimum content length
                - include_metadata: Whether to include metadata
                
        Returns:
            List of content dictionaries with text, metadata, and other fields
        """
        def _search_content_operation():
            org_id = query.get('org_id')
            if not org_id:
                logger.error("search_content called without org_id")
                return []
            
            # Start with base query
            query_obj = self.session.query(Content).filter(
                Content.org_id == org_id
            )
            
            # Apply content type filters
            content_types = query.get('content_types', [])
            if content_types:
                # Map content type names to enum values
                type_filters = []
                for content_type in content_types:
                    if content_type == 'landing_page':
                        type_filters.append(Content.content_type == 'webpage')
                    elif content_type == 'product_description':
                        type_filters.append(Content.content_type == 'webpage')
                    elif content_type == 'blog_post':
                        type_filters.append(Content.content_type == 'article')
                    elif content_type == 'about_page':
                        type_filters.append(Content.content_type == 'webpage')
                    elif content_type == 'feature_page':
                        type_filters.append(Content.content_type == 'webpage')
                    else:
                        type_filters.append(Content.content_type == content_type)
                
                if type_filters:
                    query_obj = query_obj.filter(or_(*type_filters))
            
            # Apply minimum length filter
            min_length = query.get('min_length', 0)
            if min_length > 0:
                query_obj = query_obj.filter(
                    func.length(Content.text) >= min_length
                )
            
            # Apply sorting
            sort_by = query.get('sort_by', 'relevance')
            if sort_by == 'date':
                query_obj = query_obj.order_by(desc(Content.extracted_at))
            else:
                # Default to relevance (most recent first, then by length)
                query_obj = query_obj.order_by(
                    desc(Content.extracted_at),
                    desc(func.length(Content.text))
                )
            
            # Apply limit
            limit = query.get('limit', 100)
            results = query_obj.limit(limit).all()
            
            # Convert to the format expected by ContentDrivenSignalAI
            content_samples = []
            include_metadata = query.get('include_metadata', True)
            
            for content in results:
                content_dict = {
                    'content_id': content.id,
                    'text': content.text,
                    'content': content.text,  # Alias for compatibility
                    'url': content.url,
                    'domain': content.domain,
                    'content_type': content.content_type,
                    'extracted_at': content.extracted_at
                }
                
                if include_metadata:
                    content_dict.update({
                        'title': content.title,
                        'author': content.author,
                        'publication_date': content.publication_date,
                        'last_modified': content.last_modified,
                        'categories': content.categories,
                        'tags': content.tags,
                        'language': content.language
                    })
                
                content_samples.append(content_dict)
            
            logger.info(
                f"search_content found {len(content_samples)} content samples "
                f"for org {org_id} with query: {query}"
            )
            
            return content_samples
        
        result = self._safe_execute("search_content", _search_content_operation)
        return result if result is not None else []
    
    def get_content_count(self, org_id: str) -> int:
        """Get total content count for organization"""
        def _get_count_operation():
            return self.session.query(Content).filter(Content.org_id == org_id).count()
        
        result = self._safe_execute("get_content_count", _get_count_operation)
        return result if result is not None else 0
    
    def get_content_types_for_org(self, org_id: str) -> List[str]:
        """Get available content types for organization"""
        def _get_types_operation():
            types = self.session.query(Content.content_type).filter(
                Content.org_id == org_id
            ).distinct().all()
            return [t[0] for t in types]
        
        result = self._safe_execute("get_content_types_for_org", _get_types_operation)
        return result if result is not None else []
    
    def search_content_simple(self, org_id: str, limit: int = 10) -> List[Dict]:
        """Simple content search without filters for debugging"""
        def _search_simple_operation():
            contents = self.session.query(Content).filter(
                Content.org_id == org_id
            ).order_by(desc(Content.extracted_at)).limit(limit).all()
            
            return [
                {
                    'id': content.id,
                    'title': content.title or 'No title',
                    'content_type': content.content_type,
                    'domain': content.domain,
                    'text_length': len(content.text or ''),
                    'text_preview': (content.text or '')[:200],
                    'extracted_at': content.extracted_at
                }
                for content in contents
            ]
        
        result = self._safe_execute("search_content_simple", _search_simple_operation)
        return result if result is not None else []
    
    def get_recent_crawls(self, org_id: str, limit: int = 5) -> List[Dict]:
        """Get recent crawls for organization"""
        def _get_crawls_operation():
            crawls = self.session.query(Crawl).filter(
                Crawl.org_id == org_id
            ).order_by(desc(Crawl.start_time)).limit(limit).all()
            
            return [
                {
                    'crawl_id': crawl.id,
                    'domain': crawl.domain,
                    'status': crawl.state,
                    'pages_found': crawl.pages_crawled,
                    'pages_discovered': crawl.pages_discovered,
                    'start_time': crawl.start_time,
                    'end_time': crawl.end_time
                }
                for crawl in crawls
            ]
        
        result = self._safe_execute("get_recent_crawls", _get_crawls_operation)
        return result if result is not None else []
