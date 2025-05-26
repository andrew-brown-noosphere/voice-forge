#!/usr/bin/env python
"""
Script to patch the database session handling to fix the 'Session is not an iterator' error.
"""
import sys
import os
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.session import get_db_session
from processor.rag import RAGSystem
from processor.rag_service import RAGService
from database.db import Database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def apply_session_fix():
    """Apply fixes to session handling in the RAG system."""
    logger.info("Applying session handling fixes...")
    
    # First, check how get_db_session works
    try:
        session = get_db_session()
        # Is it a generator or a direct session?
        if hasattr(session, '__next__'):
            logger.info("get_db_session() returns a generator, applying patch...")
            
            # Patch the process_and_generate method
            original_method = RAGSystem.process_and_generate
            
            def patched_process_and_generate(self, query, platform, tone, domain=None, content_type=None, top_k=5):
                """Patched version of process_and_generate with safer session handling."""
                # Log processing request
                logger.info(f"Processing content generation request for query: {query}")
                logger.info(f"Parameters: platform={platform}, tone={tone}, domain={domain}, content_type={content_type}")
                
                # Use direct session check instead of creating a new session
                content_exists = True  # Assume content exists by default
                chunks_exist = True    # Assume chunks exist by default
                
                # Step 1: Retrieve relevant chunks
                chunks = self.retrieve_relevant_chunks(
                    query=query,
                    top_k=top_k,
                    domain=domain,
                    content_type=content_type
                )
                
                # Step 2: Generate response
                if not chunks:
                    # Debug logs to help identify why no chunks were found
                    logger.warning(f"No chunks found for query: {query}")
                    
                    # Simplified check - don't try to create new sessions
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
            
            # Apply the patch
            # This is safer than modifying the class directly
            import types
            from datetime import datetime
            
            # Create a bound method for each instance
            logger.info("Patching RAGSystem.process_and_generate method...")
            
            # Create helper function to patch instances
            def patch_instance(instance):
                instance.process_and_generate = types.MethodType(patched_process_and_generate, instance)
                return instance
            
            # Patch the RAGService class to wrap created RAG systems
            original_init = RAGService.__init__
            
            def patched_init(self, db, processor_service=None):
                # Call original init
                original_init(self, db, processor_service)
                # Patch the RAG system
                self.rag_system = patch_instance(self.rag_system)
            
            # Apply the patch to RAGService
            RAGService.__init__ = patched_init
            
            logger.info("Patch applied successfully!")
        else:
            logger.info("get_db_session() doesn't return a generator, no patch needed.")
    except Exception as e:
        logger.error(f"Error checking session type: {str(e)}")

if __name__ == "__main__":
    logger.info("Starting session fix application")
    apply_session_fix()
    logger.info("Session fix completed")
