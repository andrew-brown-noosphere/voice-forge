#!/usr/bin/env python
"""
Simple fix for the 'Session is not an iterator' error in the RAG system.
"""
import sys
import os
import logging
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def apply_quick_fix():
    """
    Apply a quick fix to the RAG system to prevent the 
    'Session is not an iterator' error.
    """
    try:
        # Import the necessary modules
        from processor.rag import RAGSystem
        
        # Get the original method
        original_process_and_generate = RAGSystem.process_and_generate
        
        # Define a safer version of the method
        def safer_process_and_generate(self, query, platform, tone, domain=None, content_type=None, top_k=5):
            """
            A safer version of process_and_generate that avoids the session error.
            """
            logger.info(f"Processing query: {query}")
            
            # Step 1: Retrieve relevant chunks
            chunks = self.retrieve_relevant_chunks(
                query=query,
                top_k=top_k,
                domain=domain,
                content_type=content_type
            )
            
            # Step 2: Generate response
            if not chunks:
                logger.warning(f"No chunks found for query: {query}")
                
                # Skip the problematic chunks_exist check
                error_detail = "no_relevant_chunks"
                
                return {
                    "text": f"Sorry, I couldn't find relevant information for '{query}'. The system may need more content to be processed for RAG.",
                    "source_chunks": [],
                    "metadata": {
                        "platform": platform,
                        "tone": tone,
                        "generated_at": datetime.utcnow().isoformat(),
                        "query": query,
                        "error": error_detail
                    }
                }
            
            response = self.generate_template_response(
                query=query,
                platform=platform,
                tone=tone,
                chunks=chunks
            )
            
            return response
        
        # Replace the method
        RAGSystem.process_and_generate = safer_process_and_generate
        
        logger.info("Successfully applied quick fix to RAG system")
        
        # Also patch RAGService to create safer RAG systems
        from processor.rag_service import RAGService
        
        # Get the original method
        original_init = RAGService.__init__
        
        # Define a patched initialization method
        def patched_init(self, db, processor_service=None):
            """
            A patched version of RAGService.__init__ that creates a safer RAG system.
            """
            # Call the original init method
            original_init(self, db, processor_service)
            
            # Replace the rag_system's process_and_generate method
            self.rag_system.process_and_generate = safer_process_and_generate.__get__(self.rag_system, RAGSystem)
        
        # Replace the method
        RAGService.__init__ = patched_init
        
        logger.info("Successfully patched RAGService.__init__")
        
        # Check if the patch worked by testing a RAG system
        from database.session import get_db_session
        from database.db import Database
        
        try:
            # Get a session
            session = get_db_session()
            
            # Check if it's a session or a generator
            if hasattr(session, '__next__'):
                logger.warning("get_db_session() returns a generator, not a session")
                session = next(session)
            
            # Create a database instance
            db = Database(session)
            
            # Create a RAG service
            rag_service = RAGService(db)
            
            # Test the RAG system
            logger.info("Testing patched RAG system...")
            rag_system = rag_service.rag_system
            
            # Check if process_and_generate is the safer version
            if rag_system.process_and_generate.__name__ == 'safer_process_and_generate':
                logger.info("RAG system is using the safer version of process_and_generate")
            else:
                logger.warning("RAG system is not using the safer version of process_and_generate")
            
            logger.info("Patch test completed successfully")
        except Exception as e:
            logger.error(f"Error testing the patch: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error applying quick fix: {str(e)}")

if __name__ == "__main__":
    logger.info("Starting quick fix for RAG system")
    apply_quick_fix()
    logger.info("Quick fix completed")
