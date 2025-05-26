"""
Integration script to connect RAG with the LLM service.
"""
import os
import sys
import logging
import json
from datetime import datetime

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.session import get_db_session
from database.db import Database
from processor.rag import RAGSystem
from processor.llm.llm_service import LLMService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def connect_rag_with_llm():
    """Connect RAG system with LLM service."""
    # Initialize database
    db_session = get_db_session()
    db = Database(db_session)
    
    # Initialize LLM service
    config = {
        "openai_model": "gpt-3.5-turbo",
        "anthropic_model": "claude-instant-1",
        "cache_size": 100,
        "cache_ttl": 3600
    }
    
    # Check if API keys are set
    openai_key = os.environ.get("OPENAI_API_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    
    if not openai_key and not anthropic_key:
        logger.error("No API keys found. Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variables.")
        return
    
    llm_service = LLMService(config)
    
    # Initialize RAG system
    rag_system = RAGSystem(db)
    
    # Connect LLM service to query reformulator
    rag_system.query_reformulator.llm_service = llm_service
    
    # Test with a sample query
    query = "What is voice forge?"
    platform = "twitter"
    tone = "professional"
    
    try:
        # Search for content
        chunks = rag_system.retrieve_relevant_chunks(
            query=query,
            top_k=3
        )
        
        if chunks:
            logger.info(f"Found {len(chunks)} relevant chunks")
            for i, chunk in enumerate(chunks):
                logger.info(f"Chunk {i+1}: {chunk['text'][:100]}... (score: {chunk['similarity']:.4f})")
            
            # Use LLM to enhance response generation
            if "openai" in llm_service.clients or "anthropic" in llm_service.clients:
                # Default provider
                provider = next(iter(llm_service.clients.keys()))
                
                logger.info(f"Generating enhanced response with {provider}...")
                response = llm_service.generate(
                    prompt_type="content_generation",
                    params={
                        "topic": query,
                        "context": chunks,
                        "platform": platform,
                        "tone": tone,
                        "audience": "technology professionals"
                    },
                    provider=provider
                )
                
                logger.info(f"Generated response: {response['text']}")
            else:
                logger.info("No LLM provider available for enhanced generation")
        else:
            logger.info("No relevant chunks found")
    
    except Exception as e:
        logger.error(f"Error testing RAG with LLM: {str(e)}")
    
    finally:
        db_session.close()

if __name__ == "__main__":
    connect_rag_with_llm()
