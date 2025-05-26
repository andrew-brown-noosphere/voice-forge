#!/usr/bin/env python
"""
Script to directly fix the RAG implementation by replacing the process_and_generate method.
"""
import sys
import os
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def fix_rag_implementation():
    """Fix the RAG implementation by replacing the problematic method."""
    # Path to the RAG module
    rag_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          'processor', 'rag.py')
    
    try:
        # Read the current file
        with open(rag_path, 'r') as f:
            content = f.read()
        
        # Create a backup
        backup_path = rag_path + '.bak'
        with open(backup_path, 'w') as f:
            f.write(content)
        logger.info(f"Created backup of rag.py at {backup_path}")
        
        # Find the process_and_generate method
        method_start = content.find('def process_and_generate(')
        if method_start == -1:
            logger.error("Could not find process_and_generate method")
            return False
        
        # Find the next method (to determine the end of process_and_generate)
        next_method = content.find('def ', method_start + 10)
        if next_method == -1:
            # It's the last method in the file
            method_end = len(content)
        else:
            method_end = next_method
        
        # New implementation of process_and_generate method
        new_implementation = """    def process_and_generate(
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
                "text": f"Sorry, I couldn't find relevant information for '{query}'. Try a different query or ensure content has been processed for RAG.",
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
        new_content = content[:method_start] + new_implementation + content[method_end:]
        
        # Write the updated file
        with open(rag_path, 'w') as f:
            f.write(new_content)
        
        logger.info("Successfully updated the process_and_generate method")
        return True
        
    except Exception as e:
        logger.error(f"Error fixing RAG implementation: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Starting RAG implementation fix")
    success = fix_rag_implementation()
    if success:
        logger.info("Successfully fixed RAG implementation")
    else:
        logger.error("Failed to fix RAG implementation")
