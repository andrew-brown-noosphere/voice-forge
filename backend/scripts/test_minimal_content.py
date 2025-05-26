#!/usr/bin/env python
"""
Script to test the RAG system with a small text sample.
This helps verify the system works with minimal content.
"""
import sys
import os
import logging
import uuid
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.session import get_db_session
from database.models import Content, ContentChunk
from database.db import Database
from processor.rag_service import RAGService
from processor.chunker import ContentChunker
from api.models import ContentType, ContentMetadata

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def create_test_content():
    """Create a small test content item and process it for RAG."""
    # Get database session
    session = next(get_db_session())
    db = Database(session)
    
    try:
        # Create a test content item
        content_id = str(uuid.uuid4())
        
        test_text = """
        Voice Forge is a powerful tool for content creation and management.
        Our platform helps you search, analyze, and generate content based on your needs.
        We provide security features to keep your data safe.
        The Voice Forge system uses state-of-the-art RAG technology.
        Trust our expertise to enhance your content strategy.
        """
        
        # Create content metadata
        metadata = ContentMetadata(
            title="Voice Forge Test Content",
            author="Test Script",
            publication_date=datetime.utcnow(),
            last_modified=datetime.utcnow(),
            categories=["test"],
            tags=["test", "sample"],
            language="en",
            content_type=ContentType.BLOG_POST
        )
        
        # Store in database format
        content = Content(
            id=content_id,
            url="https://example.com/test",
            domain="example.com",
            text=test_text,
            html=f"<html><body>{test_text}</body></html>",
            crawl_id="test_crawl",
            extracted_at=datetime.utcnow(),
            title=metadata.title,
            author=metadata.author,
            publication_date=metadata.publication_date,
            last_modified=metadata.last_modified,
            categories=metadata.categories,
            tags=metadata.tags,
            language=metadata.language,
            content_type=metadata.content_type.value
        )
        
        # Save to database
        session.add(content)
        session.commit()
        
        logger.info(f"Created test content with ID: {content_id}")
        
        # Process content into chunks
        rag_service = RAGService(db)
        chunker = ContentChunker(chunk_size=200, chunk_overlap=50)  # Smaller chunks for test
        
        content_dict = {
            "content_id": content_id,
            "url": "https://example.com/test",
            "domain": "example.com",
            "text": test_text,
            "metadata": metadata,
            "crawl_id": "test_crawl",
            "extracted_at": datetime.utcnow()
        }
        
        # Generate chunks
        chunks = chunker.process_content(content_dict)
        
        # Get embedding model
        model = rag_service.rag_system.get_embedding_model()
        
        # Add embeddings
        for chunk in chunks:
            chunk["embedding"] = model.encode(chunk["text"]).tolist()
        
        # Store chunks
        db.store_content_chunks(chunks)
        
        logger.info(f"Created {len(chunks)} chunks with embeddings")
        
        # Test retrieval
        logger.info("Testing retrieval with queries...")
        
        # Test some queries
        test_queries = ["security", "trust", "content", "voice forge"]
        
        for query in test_queries:
            logger.info(f"\nTesting query: '{query}'")
            chunks = rag_service.rag_system.retrieve_relevant_chunks(query=query, top_k=3)
            
            if chunks:
                logger.info(f"Found {len(chunks)} chunks:")
                for chunk in chunks:
                    logger.info(f"Similarity: {chunk['similarity']:.4f}")
                    logger.info(f"Text: {chunk['text']}")
            else:
                logger.warning(f"No chunks found for query: {query}")
        
        # Test content generation
        logger.info("\nTesting content generation...")
        for query in test_queries:
            logger.info(f"\nGenerating content for query: '{query}'")
            response = rag_service.rag_system.process_and_generate(
                query=query,
                platform="website",
                tone="professional"
            )
            
            logger.info(f"Generated content: {response['text']}")
        
        logger.info("Test completed successfully")
        return content_id
        
    except Exception as e:
        logger.error(f"Error creating test content: {str(e)}")
        return None
    finally:
        session.close()

def cleanup_test_content(content_id):
    """Clean up the test content."""
    if not content_id:
        return
        
    # Get database session
    session = next(get_db_session())
    
    try:
        # Delete chunks first (foreign key constraint)
        chunks = session.query(ContentChunk).filter(ContentChunk.content_id == content_id).all()
        for chunk in chunks:
            session.delete(chunk)
        
        # Delete content
        content = session.query(Content).filter(Content.id == content_id).first()
        if content:
            session.delete(content)
        
        session.commit()
        logger.info(f"Cleaned up test content with ID: {content_id}")
        
    except Exception as e:
        logger.error(f"Error cleaning up test content: {str(e)}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test RAG with minimal content")
    parser.add_argument("--cleanup", action="store_true", help="Clean up test content when done")
    
    args = parser.parse_args()
    
    logger.info("Creating and testing minimal content for RAG")
    content_id = create_test_content()
    
    if args.cleanup and content_id:
        logger.info("Cleaning up test content")
        cleanup_test_content(content_id)
