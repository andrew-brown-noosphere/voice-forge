#!/usr/bin/env python
"""
Implements a search chunk by text method for SQLite.
Some environments might be using SQLite instead of PostgreSQL.
"""
import sys
import os
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import Database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def add_sqlite_extension():
    """Add a SQLite implementation of search_chunks_by_text for testing."""
    # Save the original method
    original_method = getattr(Database, 'search_chunks_by_text', None)
    
    # Add a new implementation that works with SQLite
    def sqlite_search_chunks_by_text(self, query, top_k=5, domain=None, content_type=None):
        """
        SQLite implementation of search_chunks_by_text.
        Uses a simple LIKE query instead of full-text search.
        """
        try:
            # Get SQLAlchemy imports
            from sqlalchemy import or_, func
            from database.models import ContentChunk, Content
            
            logger.info(f"SQLite text search for: {query}")
            
            # Split query into terms
            terms = [term.strip() for term in query.split() if term.strip()]
            
            # Build base query
            query_obj = self.session.query(ContentChunk)
            
            # Apply filters through joins
            if domain or content_type:
                query_obj = query_obj.join(Content, ContentChunk.content_id == Content.id)
                
                if domain:
                    query_obj = query_obj.filter(Content.domain == domain)
                
                if content_type:
                    query_obj = query_obj.filter(Content.content_type == content_type)
            
            # Add text search conditions
            conditions = []
            for term in terms:
                # Add condition for text column with LIKE
                conditions.append(ContentChunk.text.like(f'%{term}%'))
            
            if conditions:
                query_obj = query_obj.filter(or_(*conditions))
            
            # Limit results
            results = query_obj.limit(top_k).all()
            
            # Convert to dictionaries with fake similarity scores
            chunk_results = []
            
            for chunk in results:
                # Calculate a simple term frequency score
                score = 0.0
                if terms:
                    term_count = 0
                    for term in terms:
                        term_count += chunk.text.lower().count(term.lower())
                    score = min(1.0, term_count / len(terms))  # Normalize to [0, 1]
                
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
            
            return chunk_results
            
        except Exception as e:
            logger.error(f"Error in SQLite text search: {str(e)}")
            # Return an empty list as fallback
            return []
    
    # Only add the method if it doesn't already exist
    if original_method is None:
        setattr(Database, 'search_chunks_by_text', sqlite_search_chunks_by_text)
        logger.info("Added SQLite implementation of search_chunks_by_text")
    else:
        logger.info("search_chunks_by_text method already exists")

if __name__ == "__main__":
    logger.info("Adding SQLite extension for text search")
    add_sqlite_extension()
    logger.info("SQLite extension added")
