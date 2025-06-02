#!/usr/bin/env python3
"""
Script to apply the full-text search index migration for enhanced RAG.

Run this script to create the necessary PostgreSQL indexes for hybrid search.
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from database.session import DATABASE_URL
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def apply_fts_migration():
    """Apply the full-text search migration."""
    try:
        # Get database URL
        engine = create_engine(DATABASE_URL)
        
        logger.info("Applying full-text search index migration...")
        
        with engine.connect() as conn:
            # Create full-text search index
            logger.info("Creating full-text search index...")
            conn.execute(text("""
                CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_chunks_fts 
                ON content_chunks USING GIN (to_tsvector('english', text));
            """))
            
            # Create additional performance index
            logger.info("Creating additional performance index...")
            conn.execute(text("""
                CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_chunks_org_content_type
                ON content_chunks (org_id, content_id);
            """))
            
            conn.commit()
            
        logger.info("✅ Full-text search indexes created successfully!")
        
        # Verify the indexes were created
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT indexname FROM pg_indexes 
                WHERE tablename = 'content_chunks' 
                AND indexname IN ('idx_content_chunks_fts', 'idx_content_chunks_org_content_type');
            """))
            
            indexes = [row[0] for row in result.fetchall()]
            logger.info(f"Verified indexes: {indexes}")
            
            if 'idx_content_chunks_fts' in indexes:
                logger.info("✅ Full-text search index is ready!")
            else:
                logger.warning("⚠️ Full-text search index may not have been created")
                
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = apply_fts_migration()
    sys.exit(0 if success else 1)
