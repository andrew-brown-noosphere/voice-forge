#!/usr/bin/env python
"""
Simple script to test the minimum functionality of RAG in Voice Forge by creating
a very small content database and testing content generation on it.
"""
import sys
import os
import logging
import uuid
from datetime import datetime
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.session import get_db_session, Base, engine
from database.models import Content, ContentChunk
from api.models import ContentType, ContentMetadata, ContentPlatform, ContentTone

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Test content
TEST_CONTENT = """
Voice Forge is a powerful tool for content creation and management.
Our platform helps you search, analyze, and generate content.
We provide security features to keep your data safe.
Voice Forge uses state-of-the-art technology for content processing.
Trust our expertise to enhance your content strategy.
Our system is reliable and efficient for all your content needs.
"""

def setup_test_database():
    """Create a minimal test database with content."""
    # Recreate the database schema
    logger.info("Dropping and recreating tables...")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    
    # Get a session
    session_factory = get_db_session
    session = next(session_factory())
    
    try:
        # Create test content
        content_id = str(uuid.uuid4())
        content = Content(
            id=content_id,
            url="https://example.com/test",
            domain="example.com",
            text=TEST_CONTENT,
            html=f"<div>{TEST_CONTENT}</div>",
            crawl_id="test_crawl",
            extracted_at=datetime.utcnow(),
            title="Test Content",
            author="Test Script",
            publication_date=datetime.utcnow(),
            last_modified=datetime.utcnow(),
            categories=["test"],
            tags=["test", "security", "trust"],
            language="en",
            content_type=ContentType.BLOG_POST.value
        )
        
        session.add(content)
        session.commit()
        logger.info(f"Created test content with ID: {content_id}")
        
        # Create chunks manually
        chunks = []
        lines = [line.strip() for line in TEST_CONTENT.split('\n') if line.strip()]
        
        for i, line in enumerate(lines):
            chunk_id = str(uuid.uuid4())
            chunk = ContentChunk(
                id=chunk_id,
                content_id=content_id,
                chunk_index=i,
                text=line,
                start_char=TEST_CONTENT.find(line),
                end_char=TEST_CONTENT.find(line) + len(line),
                chunk_metadata={
                    "title": "Test Content",
                    "content_type": ContentType.BLOG_POST.value,
                    "domain": "example.com",
                    "url": "https://example.com/test",
                    "chunking_method": "line_based",
                    "created_at": datetime.utcnow().isoformat()
                }
            )
            
            # Create a simple embedding
            # This is just a random vector for testing - in production this would be a real embedding
            import numpy as np
            embedding = np.random.rand(768).astype(np.float32).tolist()
            chunk.embedding = embedding
            
            chunks.append(chunk)
            session.add(chunk)
        
        session.commit()
        logger.info(f"Created {len(chunks)} test chunks with embeddings")
        
        return content_id
    except Exception as e:
        logger.error(f"Error setting up test database: {str(e)}")
        session.rollback()
        return None
    finally:
        session.close()

def test_rag_direct_methods():
    """Test RAG functionality using direct database access."""
    # Get a session
    session_factory = get_db_session
    session = next(session_factory())
    
    try:
        # Verify content exists
        content_count = session.query(Content).count()
        logger.info(f"Content count: {content_count}")
        
        # Verify chunks exist
        chunk_count = session.query(ContentChunk).count()
        logger.info(f"Chunk count: {chunk_count}")
        
        if content_count == 0 or chunk_count == 0:
            logger.error("No content or chunks found. Database setup failed.")
            return
        
        # Test simple retrieval
        # For each test query, find chunks that contain the words
        test_queries = ["security", "trust", "content", "voice forge"]
        
        for query in test_queries:
            logger.info(f"\n=== Testing query: '{query}' ===")
            # Simple text-based search
            query_terms = query.lower().split()
            
            found_chunks = []
            chunks = session.query(ContentChunk).all()
            
            for chunk in chunks:
                score = 0.0
                chunk_text = chunk.text.lower()
                
                for term in query_terms:
                    if term in chunk_text:
                        score += 1.0
                
                if score > 0:
                    # Normalize score
                    score = score / len(query_terms)
                    found_chunks.append({
                        "id": chunk.id,
                        "text": chunk.text,
                        "similarity": score
                    })
            
            # Sort by similarity
            found_chunks.sort(key=lambda x: x["similarity"], reverse=True)
            
            if found_chunks:
                logger.info(f"Found {len(found_chunks)} chunks containing terms in '{query}':")
                for chunk in found_chunks:
                    logger.info(f"Similarity: {chunk['similarity']:.2f} - Text: {chunk['text']}")
                
                # Simple content generation
                if len(found_chunks) > 0:
                    # Generate a response using the found chunks
                    top_chunks = found_chunks[:3]  # Use top 3 chunks
                    context = "\n".join([chunk["text"] for chunk in top_chunks])
                    
                    response = f"Based on the Voice Forge documentation, here's information about {query}:\n\n"
                    response += context
                    
                    logger.info(f"\nGenerated response for '{query}':")
                    logger.info(response)
            else:
                logger.warning(f"No chunks found for query: '{query}'")
        
        # Test the actual endpoint without using the API
        try:
            from processor.rag_service import RAGService
            from database.db import Database
            
            logger.info("\n=== Testing RAG Service directly ===")
            
            db = Database(session)
            rag_service = RAGService(db)
            
            for query in test_queries:
                logger.info(f"\nTesting RAG service with query: '{query}'")
                
                # Make sure no errors happen in the process
                try:
                    # Generate content
                    response = rag_service.generate_content(
                        query=query,
                        platform=ContentPlatform.WEBSITE,
                        tone=ContentTone.PROFESSIONAL
                    )
                    
                    # Log the response
                    logger.info(f"RAG Service Response for '{query}':")
                    logger.info(response.text)
                    logger.info(f"Source chunks: {len(response.source_chunks)}")
                    
                    # Check if the default "not found" message is returned
                    if "Sorry, I couldn't find relevant information" in response.text:
                        logger.warning("Default 'not found' message returned.")
                    
                except Exception as inner_e:
                    logger.error(f"Error generating content with RAG service: {str(inner_e)}")
        except Exception as e:
            logger.error(f"Error testing RAG service directly: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error in direct RAG testing: {str(e)}")
    finally:
        session.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test RAG with minimal database")
    parser.add_argument("--skip-setup", action="store_true", help="Skip database setup")
    
    args = parser.parse_args()
    
    if not args.skip_setup:
        logger.info("Setting up test database...")
        content_id = setup_test_database()
        if not content_id:
            logger.error("Failed to set up test database. Exiting.")
            sys.exit(1)
    
    logger.info("Testing RAG functionality...")
    test_rag_direct_methods()
    logger.info("Test completed.")
