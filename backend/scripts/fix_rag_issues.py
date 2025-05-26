#!/usr/bin/env python
"""
Script to apply patches to fix RAG issues.
"""
import sys
import os
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Define the path to the RAG module
RAG_MODULE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'processor', 'rag.py'
)

def apply_rag_patches():
    """Apply patches to fix RAG issues."""
    try:
        # Read the current RAG module
        with open(RAG_MODULE_PATH, 'r') as f:
            rag_code = f.read()
        
        # Create a backup
        backup_path = RAG_MODULE_PATH + '.bak'
        with open(backup_path, 'w') as f:
            f.write(rag_code)
        logger.info(f"Created backup of rag.py at {backup_path}")
        
        # Patch 1: Add text search fallback to retrieve_relevant_chunks method
        if 'def retrieve_relevant_chunks(' in rag_code:
            # Find the right location to add the text search fallback
            method_end = rag_code.find("        return chunks", rag_code.find('def retrieve_relevant_chunks('))
            
            if method_end > 0:
                # Insert the text search fallback code
                text_search_fallback = """
            # If no chunks found, try fallback text-based search if available
            if not chunks and hasattr(self.db, 'search_chunks_by_text'):
                logger.info(f"No chunks found with vector search, trying text-based search for: {query}")
                try:
                    text_chunks = self.db.search_chunks_by_text(
                        query=query,
                        top_k=top_k,
                        domain=domain,
                        content_type=content_type
                    )
                    if text_chunks:
                        logger.info(f"Found {len(text_chunks)} chunks using text search")
                        chunks = text_chunks
                except Exception as text_e:
                    logger.error(f"Text search fallback failed: {str(text_e)}")
            """
                
                # Add the fallback before returning chunks
                patched_code = rag_code[:method_end] + text_search_fallback + rag_code[method_end:]
                rag_code = patched_code
                logger.info("Added text search fallback to retrieve_relevant_chunks method")
        
        # Patch 2: Simplify process_and_generate method to avoid transaction issues
        process_start = rag_code.find('def process_and_generate(')
        if process_start > 0:
            process_end = rag_code.find('def', process_start + 1)
            if process_end < 0:  # If it's the last method in the file
                process_end = len(rag_code)
            
            # Replace with simplified implementation
            simplified_implementation = """    def process_and_generate(
        self,
        query: str,
        platform: str,
        tone: str,
        domain: Optional[str] = None,
        content_type: Optional[str] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        \"\"\"
        End-to-end process to retrieve relevant chunks and generate a response.
        
        Args:
            query: Search query
            platform: Target platform
            tone: Desired tone
            domain: Optional domain filter
            content_type: Optional content type filter
            top_k: Number of chunks to retrieve
            
        Returns:
            Generated response with source information
        \"\"\"
        # Log processing request
        logger.info(f"Processing content generation request for query: {query}")
        logger.info(f"Parameters: platform={platform}, tone={tone}, domain={domain}, content_type={content_type}")
        
        # Step 1: Try to retrieve relevant chunks using vector search
        chunks = self.retrieve_relevant_chunks(
            query=query,
            top_k=top_k,
            domain=domain,
            content_type=content_type
        )
        
        # Step 2: Generate response
        if not chunks:
            # No chunks found - error
            logger.warning(f"No chunks found for query: {query}")
            
            return {
                "text": f"Sorry, I couldn't find relevant information for '{query}'. Try a different query or make sure content has been processed for RAG.",
                "source_chunks": [],
                "metadata": {
                    "platform": platform,
                    "tone": tone,
                    "generated_at": datetime.utcnow().isoformat(),
                    "query": query,
                    "error": "no_relevant_chunks"
                }
            }
        
        # Generate response from chunks
        response = self.generate_template_response(
            query=query,
            platform=platform,
            tone=tone,
            chunks=chunks
        )
        
        return response
"""
            
            # Replace the method
            patched_code = rag_code[:process_start] + simplified_implementation + rag_code[process_end:]
            rag_code = patched_code
            logger.info("Simplified process_and_generate method to avoid transaction issues")
        
        # Write the patched RAG module
        with open(RAG_MODULE_PATH, 'w') as f:
            f.write(rag_code)
        
        logger.info(f"Successfully patched {RAG_MODULE_PATH}")
        
        return True
    
    except Exception as e:
        logger.error(f"Failed to apply patches: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Starting RAG patches application")
    success = apply_rag_patches()
    
    if success:
        logger.info("Successfully applied all patches")
        logger.info("Restart your server to apply the changes")
    else:
        logger.error("Failed to apply patches")
