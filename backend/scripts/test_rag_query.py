#!/usr/bin/env python
"""
Test script for the RAG system to see if query retrieval is working.
"""
import sys
import os
import logging
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.session import get_db_session
from processor.rag_service import RAGService
from database.db import Database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def test_rag_query(query="security", domain=None):
    """Test retrieving chunks for a specific query."""
    # Get database session
    session = next(get_db_session())
    db = Database(session)
    
    # Initialize RAG service
    rag_service = RAGService(db)
    
    try:
        # Get the RAG system
        rag_system = rag_service.rag_system
        
        # Test retrieval with the query
        logger.info(f"Testing retrieval for query: {query}")
        
        chunks = rag_system.retrieve_relevant_chunks(
            query=query,
            top_k=5,
            domain=domain
        )
        
        logger.info(f"Retrieved {len(chunks)} chunks")
        
        if len(chunks) > 0:
            logger.info("Top chunks found:")
            for i, chunk in enumerate(chunks):
                logger.info(f"Chunk {i+1} (similarity: {chunk['similarity']:.4f}):")
                # Print the first 100 characters of the chunk text
                logger.info(f"  {chunk['text'][:100]}...")
                logger.info(f"  Content ID: {chunk['content_id']}")
                if chunk.get('metadata') and chunk['metadata'].get('title'):
                    logger.info(f"  Title: {chunk['metadata']['title']}")
        else:
            logger.warning(f"No chunks found for query: {query}")
            
            # Try text search as a fallback
            logger.info("Trying text search as a fallback...")
            
            # Get a fresh session for the text search to avoid transaction issues
            text_search_session = next(get_db_session())
            text_search_db = Database(text_search_session)
            
            try:
                chunks = text_search_db.search_chunks_by_text(
                    query=query,
                    top_k=5,
                    domain=domain
                )
                
                if len(chunks) > 0:
                    logger.info(f"Text search found {len(chunks)} chunks:")
                    for i, chunk in enumerate(chunks):
                        logger.info(f"Chunk {i+1} (similarity: {chunk['similarity']:.4f}):")
                        logger.info(f"  {chunk['text'][:100]}...")
                else:
                    logger.warning("No chunks found using text search either.")
                    
                    # Count total chunks to see if there's any data
                    # Use a fresh session for counting to avoid transaction issues
                    count_session = next(get_db_session())
                    
                    try:
                        from database.models import ContentChunk
                        from sqlalchemy import func
                        
                        total_chunks = count_session.query(func.count(ContentChunk.id)).scalar()
                        logger.info(f"Total chunks in database: {total_chunks}")
                        
                        if total_chunks > 0:
                            # Get a sample chunk
                            sample_chunk = count_session.query(ContentChunk).first()
                            if sample_chunk:
                                logger.info("Sample chunk from database:")
                                logger.info(f"  ID: {sample_chunk.id}")
                                logger.info(f"  Text: {sample_chunk.text[:100]}...")
                                logger.info(f"  Has embedding: {sample_chunk.embedding is not None}")
                    except Exception as count_error:
                        logger.error(f"Error counting chunks: {str(count_error)}")
                    finally:
                        count_session.close()
            except Exception as text_search_error:
                logger.error(f"Error in text search: {str(text_search_error)}")
            finally:
                text_search_session.close()
        
        return chunks
        
    except Exception as e:
        logger.error(f"Error testing RAG query: {str(e)}")
        return []
    finally:
        session.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test RAG query retrieval")
    parser.add_argument("--query", default="security", help="Query to test")
    parser.add_argument("--domain", help="Domain to filter by")
    
    args = parser.parse_args()
    
    logger.info(f"Testing RAG query: {args.query}")
    chunks = test_rag_query(args.query, args.domain)
    
    if chunks:
        logger.info(f"Found {len(chunks)} chunks for query: {args.query}")
    else:
        logger.info(f"No chunks found for query: {args.query}")
