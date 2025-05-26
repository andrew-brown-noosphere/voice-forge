#!/usr/bin/env python
"""
Complete test and fix for the Voice Forge RAG system.
This script tries to diagnose and fix issues with minimal content.
"""
import sys
import os
import logging
import uuid
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def fix_session_issue():
    """Fix the session issue by monkeypatching."""
    try:
        # Import the session module
        import database.session
        
        # Check if get_db_session returns a generator
        original_get_db_session = database.session.get_db_session
        
        try:
            # Test the original function
            session = original_get_db_session()
            is_generator = hasattr(session, '__next__')
            
            if is_generator:
                logger.info("get_db_session returns a generator, applying monkey patch...")
                
                # Create a fixed version
                def fixed_get_db_session():
                    """Fixed version that returns a session directly."""
                    return next(original_get_db_session())
                
                # Apply the monkey patch
                database.session.get_db_session = fixed_get_db_session
                logger.info("Session monkey patch applied")
        except Exception as e:
            logger.error(f"Error testing get_db_session: {str(e)}")
    except Exception as e:
        logger.error(f"Error importing database.session: {str(e)}")

def fix_rag_system():
    """Fix the RAG system's error handling."""
    try:
        # Import the rag module
        from processor.rag import RAGSystem
        from datetime import datetime
        
        # Patch the process_and_generate method
        original_method = RAGSystem.process_and_generate
        
        def safe_process_and_generate(self, query, platform, tone, domain=None, content_type=None, top_k=5):
            """Safe version of process_and_generate that doesn't create new sessions."""
            # Log processing request
            logger.info(f"Processing content generation request for query: {query}")
            
            # Step 1: Retrieve relevant chunks
            chunks = self.retrieve_relevant_chunks(
                query=query,
                top_k=top_k,
                domain=domain,
                content_type=content_type
            )
            
            # Step 2: Generate response
            if not chunks:
                # Debug logs
                logger.warning(f"No chunks found for query: {query}")
                
                # No chunks found, return generic response
                return {
                    "text": f"Sorry, I couldn't find relevant information for '{query}'. Try a different query or make sure content has been crawled and processed.",
                    "source_chunks": [],
                    "metadata": {
                        "platform": platform,
                        "tone": tone,
                        "generated_at": datetime.utcnow().isoformat(),
                        "query": query,
                        "error": "no_relevant_chunks"
                    }
                }
            
            response = self.generate_template_response(
                query=query,
                platform=platform,
                tone=tone,
                chunks=chunks
            )
            
            return response
        
        # Apply the patch
        RAGSystem.process_and_generate = safe_process_and_generate
        logger.info("RAG system patched successfully")
    except Exception as e:
        logger.error(f"Error patching RAG system: {str(e)}")

def test_minimal_rag():
    """Test the RAG system with minimal content."""
    try:
        # First fix the session issue
        fix_session_issue()
        
        # Then fix the RAG system
        fix_rag_system()
        
        # Import the necessary modules
        from database.session import get_db_session
        from database.db import Database
        from processor.rag_service import RAGService
        from api.models import ContentPlatform, ContentTone
        
        # Get a session
        session = get_db_session()
        
        # Create a database instance
        db = Database(session)
        
        # Create a RAG service
        rag_service = RAGService(db)
        
        # Test queries
        test_queries = ["security", "trust", "content", "voice forge"]
        
        for query in test_queries:
            logger.info(f"\nTesting query: '{query}'")
            
            try:
                # Test search_chunks
                chunks = rag_service.search_chunks(
                    query=query,
                    top_k=5
                )
                
                if chunks:
                    logger.info(f"Found {len(chunks)} chunks for query: {query}")
                    
                    # Log the first chunk
                    if chunks[0]:
                        logger.info(f"First chunk: {chunks[0].text[:100]}...")
                        logger.info(f"Similarity: {chunks[0].similarity}")
                else:
                    logger.warning(f"No chunks found for query: {query}")
                
                # Test generate_content
                content = rag_service.generate_content(
                    query=query,
                    platform=ContentPlatform.WEBSITE,
                    tone=ContentTone.PROFESSIONAL
                )
                
                if content:
                    logger.info(f"Generated content for query: {query}")
                    logger.info(f"Response: {content.text[:200]}...")
                    logger.info(f"Number of source chunks: {len(content.source_chunks)}")
                else:
                    logger.warning(f"No content generated for query: {query}")
            except Exception as e:
                logger.error(f"Error testing query '{query}': {str(e)}")
    
    except Exception as e:
        logger.error(f"Error in minimal RAG test: {str(e)}")

if __name__ == "__main__":
    logger.info("Starting complete RAG test and fix")
    test_minimal_rag()
    logger.info("Test completed")
