"""
Database interface implementation.
"""
import json
from typing import List, Dict, Optional, Any
from datetime import datetime
from sqlalchemy import desc, func, cast, Float
from sqlalchemy.dialects.postgresql import ARRAY

from database.models import Crawl, Content
from api.models import CrawlStatus, CrawlState, CrawlProgress, ContentType, ContentMetadata

class Database:
    """Database interface for VoiceForge."""
    
    def __init__(self, session):
        """Initialize the database interface."""
        self.session = session
    
    def save_crawl_status(self, status: CrawlStatus):
        """Save a new crawl status to the database."""
        crawl = Crawl(
            id=status.crawl_id,
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
    
    def update_crawl_status(self, status: CrawlStatus):
        """Update an existing crawl status in the database."""
        crawl = self.session.query(Crawl).filter(Crawl.id == status.crawl_id).first()
        
        if not crawl:
            return self.save_crawl_status(status)
        
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
    
    def get_crawl_status(self, crawl_id: str) -> Optional[CrawlStatus]:
        """Get a crawl status from the database."""
        crawl = self.session.query(Crawl).filter(Crawl.id == crawl_id).first()
        
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
    
    def list_crawl_statuses(self, limit: int, offset: int) -> List[CrawlStatus]:
        """List all crawl statuses with pagination."""
        crawls = self.session.query(Crawl) \
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
    
    def save_content(self, content_data: Dict[str, Any]):
        """Save content to the database."""
        metadata = content_data["metadata"]
        
        content = Content(
            id=content_data["content_id"],
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
    
    def get_content(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get content by ID."""
        content = self.session.query(Content).filter(Content.id == content_id).first()
        
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
        offset: int = 0
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
        query = self.session.query(Content)
        
        # Apply filters
        if domain:
            query = query.filter(Content.domain == domain)
        
        if content_type:
            query = query.filter(Content.content_type == content_type.value)
        
        # Filter for processed content with embeddings
        query = query.filter(Content.is_processed == True)
        query = query.filter(Content.embedding.isnot(None))
        
        # Calculate vector similarity
        # Note: This requires pgvector extension
        query_vector = func.array_to_vector(cast(query_embedding, ARRAY(Float)))
        similarity = func.cosine_similarity(func.vector(Content.embedding), query_vector)
        
        # Order by similarity
        query = query.order_by(desc(similarity))
        
        # Apply pagination
        query = query.limit(limit).offset(offset)
        
        # Execute query
        results = query.all()
        
        # Convert to dictionaries with relevance scores
        content_results = []
        for content in results:
            # Calculate cosine similarity (can be done in Python if pgvector is not available)
            from sklearn.metrics.pairwise import cosine_similarity
            import numpy as np
            
            similarity_score = cosine_similarity(
                [np.array(query_embedding)],
                [np.array(content.embedding)]
            )[0][0]
            
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
    
    def get_all_domains(self) -> List[str]:
        """Get all domains that have been crawled."""
        domains = self.session.query(Content.domain).distinct().all()
        return [domain[0] for domain in domains]
