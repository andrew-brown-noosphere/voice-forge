#!/usr/bin/env python
"""
Script to analyze content and chunks in the database.
This helps diagnose issues with RAG when using limited content.
"""
import sys
import os
import logging
import json
from datetime import datetime
from textwrap import dedent
from sqlalchemy import func, desc

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.session import get_db_session
from database.models import Content, ContentChunk
from database.db import Database
from processor.rag_service import RAGService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def analyze_database_content():
    """Analyze the content and chunks in the database."""
    # Get database session
    session = next(get_db_session())
    db = Database(session)
    
    try:
        # Get content count by domain
        content_by_domain = session.query(Content.domain, func.count(Content.id)).group_by(Content.domain).all()
        logger.info("\n=== CONTENT BY DOMAIN ===")
        for domain, count in content_by_domain:
            logger.info(f"Domain: {domain} - {count} item(s)")
        
        # Get total content count
        total_content = session.query(func.count(Content.id)).scalar()
        logger.info(f"Total content items: {total_content}")
        
        # Get content type breakdown
        content_by_type = session.query(Content.content_type, func.count(Content.id)).group_by(Content.content_type).all()
        logger.info("\n=== CONTENT BY TYPE ===")
        for content_type, count in content_by_type:
            logger.info(f"Type: {content_type} - {count} item(s)")
        
        # Get chunk count
        total_chunks = session.query(func.count(ContentChunk.id)).scalar()
        logger.info(f"\nTotal content chunks: {total_chunks}")
        
        # Get chunk count by content
        chunks_per_content = session.query(
            Content.id, Content.domain, Content.title, func.count(ContentChunk.id)
        ).join(ContentChunk, ContentChunk.content_id == Content.id) \
         .group_by(Content.id) \
         .order_by(desc(func.count(ContentChunk.id))) \
         .all()
        
        logger.info("\n=== CHUNKS PER CONTENT ===")
        for content_id, domain, title, chunk_count in chunks_per_content:
            logger.info(f"Content: {title or content_id} - Domain: {domain} - {chunk_count} chunk(s)")
        
        # Get chunks with/without embeddings
        chunks_with_embeddings = session.query(ContentChunk).filter(ContentChunk.embedding != None).count()
        logger.info(f"\nChunks with embeddings: {chunks_with_embeddings}/{total_chunks}")
        
        # Check if any chunks exist without embeddings
        if chunks_with_embeddings < total_chunks:
            logger.warning(f"Found {total_chunks - chunks_with_embeddings} chunks without embeddings!")
        
        # Sample the content if there's only a few items
        if total_content <= 5:
            logger.info("\n=== CONTENT SAMPLES ===")
            contents = session.query(Content).all()
            for content in contents:
                # Truncate text to first 200 characters
                text_sample = content.text[:200] + "..." if len(content.text) > 200 else content.text
                logger.info(f"Content ID: {content.id}")
                logger.info(f"URL: {content.url}")
                logger.info(f"Title: {content.title}")
                logger.info(f"Content Type: {content.content_type}")
                logger.info(f"Text Sample: {text_sample}")
                logger.info(f"Full Text Length: {len(content.text)} characters")
                logger.info(f"Has Embedding: {content.embedding is not None}")
                logger.info(f"Is Processed: {content.is_processed}")
                logger.info("")
        
        # Sample chunks if there are only a few
        if total_chunks <= 20:
            logger.info("\n=== CHUNK SAMPLES ===")
            chunks = session.query(ContentChunk).order_by(ContentChunk.content_id, ContentChunk.chunk_index).all()
            for chunk in chunks:
                # Truncate text to first 100 characters
                text_sample = chunk.text[:100] + "..." if len(chunk.text) > 100 else chunk.text
                logger.info(f"Chunk ID: {chunk.id}")
                logger.info(f"Content ID: {chunk.content_id}")
                logger.info(f"Chunk Index: {chunk.chunk_index}")
                logger.info(f"Text Sample: {text_sample}")
                logger.info(f"Full Text Length: {len(chunk.text)} characters")
                logger.info(f"Has Embedding: {chunk.embedding is not None}")
                logger.info("")
        
        # Check min/avg/max chunk sizes
        if total_chunks > 0:
            logger.info("\n=== CHUNK SIZE STATISTICS ===")
            
            # Using Python to calculate since SQLite might not have all aggregate functions
            chunks = session.query(ContentChunk).all()
            chunk_sizes = [len(chunk.text) for chunk in chunks]
            
            min_size = min(chunk_sizes) if chunk_sizes else 0
            max_size = max(chunk_sizes) if chunk_sizes else 0
            avg_size = sum(chunk_sizes) / len(chunk_sizes) if chunk_sizes else 0
            
            logger.info(f"Minimum chunk size: {min_size} characters")
            logger.info(f"Maximum chunk size: {max_size} characters")
            logger.info(f"Average chunk size: {avg_size:.2f} characters")
            
            # Find the smallest chunk
            if min_size < 50 and chunk_sizes:  # Only show if suspiciously small
                smallest_idx = chunk_sizes.index(min_size)
                smallest_chunk = chunks[smallest_idx]
                logger.warning(f"Smallest chunk content: \"{smallest_chunk.text}\"")
        
        # Provide guidance based on findings
        logger.info("\n=== ANALYSIS RECOMMENDATIONS ===")
        
        if total_content == 0:
            logger.warning("No content found! You need to crawl websites first.")
            return
        
        if total_chunks == 0:
            logger.warning(dedent("""
                No chunks found! You need to process content for RAG:
                python scripts/process_content_for_rag.py
            """))
            return
        
        # Check if content is too small
        small_content = False
        if total_content > 0:
            avg_text_length = session.query(func.avg(func.length(Content.text))).scalar()
            if avg_text_length < 500:  # Arbitrary threshold for "small" content
                small_content = True
                logger.warning(dedent(f"""
                    Your content is quite small (average {avg_text_length:.0f} characters). 
                    The RAG system works best with substantial text content.
                    Consider crawling more content-rich pages for better results.
                """))
        
        # Check chunk count ratio
        if total_content > 0 and total_chunks > 0:
            chunks_per_content_avg = total_chunks / total_content
            if chunks_per_content_avg < 3 and small_content:
                logger.warning(dedent(f"""
                    Low chunk count per content ({chunks_per_content_avg:.1f}) and small content size.
                    Try crawling more content-rich pages with more text.
                    The RAG system needs enough text to generate meaningful chunks.
                """))
        
        # Make specific recommendations
        logger.info(dedent("""
            For better RAG performance:
            1. Crawl content-rich pages with substantial text
            2. Make sure all content is processed into chunks (run process_content_for_rag.py)
            3. Ensure chunks have embeddings
            4. Use queries that match the topics covered in your content
        """))
        
    except Exception as e:
        logger.error(f"Error analyzing database content: {str(e)}")
    finally:
        session.close()

if __name__ == "__main__":
    logger.info("Starting database content analysis")
    analyze_database_content()
    logger.info("Analysis completed")
