#!/usr/bin/env python
"""
Script to manually process content for the RAG system, with better text handling for marketing content.
"""
import sys
import os
import logging
import re
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.session import get_db_session
from database.models import Content, ContentChunk
from database.db import Database
from processor.chunker import ContentChunker
from processor.rag_service import RAGService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def clean_and_preprocess_text(text):
    """Clean and preprocess text for better chunking."""
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    
    # Ensure sentence breaks have a space after them
    text = re.sub(r'([.!?])"', r'\1 "', text)
    
    # Fix broken sentences (no space after period)
    text = re.sub(r'([a-z])\.([A-Z])', r'\1. \2', text)
    
    # Add paragraph breaks after testimonials/quotes
    text = re.sub(r'([.!?])"', r'\1"\n\n', text)
    
    # Add paragraph breaks after headings (capitalized sentences followed by regular text)
    text = re.sub(r'([A-Z][A-Z\s]+)([a-z])', r'\1\n\n\2', text)
    
    return text

def process_content_with_improved_chunking():
    """Process all content for RAG with improved chunking for marketing text."""
    # Get database session
    session = get_db_session()
    if hasattr(session, '__next__'):
        session = next(session)
    
    db = Database(session)
    
    try:
        # Get all content
        contents = session.query(Content).all()
        
        logger.info(f"Found {len(contents)} content items to process")
        
        # Create a custom chunker with smaller chunk size for marketing content
        chunker = ContentChunker(chunk_size=300, chunk_overlap=100)
        
        # Process each content item individually to avoid transaction issues
        for i, content in enumerate(contents):
            logger.info(f"Processing content {i+1}/{len(contents)}: {content.id}")
            
            try:
                # Create a new session for this item
                item_session = get_db_session()
                if hasattr(item_session, '__next__'):
                    item_session = next(item_session)
                
                item_db = Database(item_session)
                
                # Clean up first
                try:
                    # Delete existing chunks for this content
                    deleted = item_session.query(ContentChunk).filter(ContentChunk.content_id == content.id).delete()
                    item_session.commit()
                    logger.info(f"Deleted {deleted} existing chunks for content {content.id}")
                except Exception as e:
                    logger.error(f"Error deleting existing chunks: {str(e)}")
                    item_session.rollback()
                
                # Create content dictionary
                content_dict = {
                    "content_id": content.id,
                    "url": content.url,
                    "domain": content.domain,
                    "text": clean_and_preprocess_text(content.text),
                    "metadata": {
                        "title": content.title,
                        "author": content.author,
                        "publication_date": content.publication_date,
                        "last_modified": content.last_modified,
                        "categories": content.categories,
                        "tags": content.tags,
                        "language": content.language,
                        "content_type": content.content_type
                    },
                    "crawl_id": content.crawl_id,
                    "extracted_at": content.extracted_at
                }
                
                # Generate chunks
                chunks = chunker.process_content(content_dict)
                logger.info(f"Generated {len(chunks)} chunks for content {content.id}")
                
                # Create RAG service
                rag_service = RAGService(item_db)
                
                # Get embedding model
                model = rag_service.rag_system.get_embedding_model()
                
                # Process chunks in batches
                batch_size = 10
                for j in range(0, len(chunks), batch_size):
                    batch = chunks[j:j+batch_size]
                    texts = [chunk["text"] for chunk in batch]
                    
                    try:
                        # Generate embeddings
                        embeddings = model.encode(texts)
                        
                        # Update chunks with embeddings
                        for k, embedding in enumerate(embeddings):
                            batch[k]["embedding"] = embedding.tolist()
                        
                        # Store chunks
                        item_db.store_content_chunks(batch)
                        logger.info(f"Stored batch {j//batch_size + 1}/{(len(chunks) + batch_size - 1)//batch_size} for content {content.id}")
                    except Exception as e:
                        logger.error(f"Error processing batch: {str(e)}")
                
                # Close the session
                item_session.close()
                
            except Exception as e:
                logger.error(f"Error processing content {content.id}: {str(e)}")
                continue
        
        logger.info("Finished processing all content")
        
    except Exception as e:
        logger.error(f"Error processing content: {str(e)}")
    finally:
        session.close()

def test_rag_query(query="marketing"):
    """Test the RAG system with a specific query."""
    # Get database session
    session = get_db_session()
    if hasattr(session, '__next__'):
        session = next(session)
    
    db = Database(session)
    
    try:
        # Create RAG service
        rag_service = RAGService(db)
        
        # Try a text search first
        logger.info(f"Searching for text containing '{query}'...")
        chunks = db.search_chunks_by_text(query=query, top_k=5)
        
        if chunks:
            logger.info(f"Found {len(chunks)} chunks containing '{query}':")
            for i, chunk in enumerate(chunks):
                logger.info(f"Chunk {i+1}: {chunk['text'][:100]}...")
        else:
            logger.info(f"No chunks found containing '{query}'")
        
        # Now try vector search
        logger.info(f"Performing vector search for '{query}'...")
        chunks = rag_service.rag_system.retrieve_relevant_chunks(query=query, top_k=5)
        
        if chunks:
            logger.info(f"Found {len(chunks)} relevant chunks for '{query}':")
            for i, chunk in enumerate(chunks):
                logger.info(f"Chunk {i+1} (similarity: {chunk['similarity']:.2f}): {chunk['text'][:100]}...")
        else:
            logger.info(f"No relevant chunks found for '{query}'")
        
        # Try generating content
        logger.info(f"Generating content for '{query}'...")
        response = rag_service.rag_system.process_and_generate(
            query=query,
            platform="website",
            tone="professional"
        )
        
        logger.info(f"Generated response: {response['text']}")
        
    except Exception as e:
        logger.error(f"Error testing RAG query: {str(e)}")
    finally:
        session.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Improved content processing for RAG")
    parser.add_argument("--test-only", action="store_true", help="Test the current RAG system without processing content")
    parser.add_argument("--query", default="marketing", help="Query to test")
    
    args = parser.parse_args()
    
    if args.test_only:
        logger.info(f"Testing RAG with query: {args.query}")
        test_rag_query(args.query)
    else:
        logger.info("Starting improved content processing for RAG")
        process_content_with_improved_chunking()
        logger.info("Testing RAG after processing")
        test_rag_query(args.query)
