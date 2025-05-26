"""
Integration test for LLM services.
"""
import os
import logging
import sys
import json
from typing import Dict, Any

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from processor.llm.llm_service import LLMService
from processor.retrieval.query_reformulation import QueryReformulator
from processor.llm.token_manager import TokenManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def test_llm_service():
    """Test the LLM service."""
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
    
    # Test provider availability
    logger.info(f"Available providers: {list(llm_service.clients.keys())}")
    
    # Test generating completions
    if "openai" in llm_service.clients:
        logger.info("Testing OpenAI...")
        try:
            response = llm_service.generate(
                prompt_type="rag_response",
                params={
                    "query": "What is retrieval augmented generation?", 
                    "context": "Retrieval Augmented Generation (RAG) is a technique that combines retrieval-based and generation-based approaches for natural language processing tasks. It first retrieves relevant information from a knowledge base and then uses this information to augment a language model's generation process."
                },
                provider="openai"
            )
            logger.info(f"OpenAI response: {response['text'][:100]}...")
            logger.info(f"Tokens used: {response.get('usage', {})}")
        except Exception as e:
            logger.error(f"OpenAI test failed: {str(e)}")
    
    if "anthropic" in llm_service.clients:
        logger.info("Testing Anthropic...")
        try:
            response = llm_service.generate(
                prompt_type="rag_response",
                params={
                    "query": "What is retrieval augmented generation?", 
                    "context": "Retrieval Augmented Generation (RAG) is a technique that combines retrieval-based and generation-based approaches for natural language processing tasks. It first retrieves relevant information from a knowledge base and then uses this information to augment a language model's generation process."
                },
                provider="anthropic"
            )
            logger.info(f"Anthropic response: {response['text'][:100]}...")
        except Exception as e:
            logger.error(f"Anthropic test failed: {str(e)}")
    
    # Test cache
    logger.info("Testing cache...")
    if "openai" in llm_service.clients:
        start = time.time()
        response1 = llm_service.generate(
            prompt_type="query_reformulation",
            params={"query": "How to implement RAG"},
            provider="openai"
        )
        first_time = time.time() - start
        
        start = time.time()
        response2 = llm_service.generate(
            prompt_type="query_reformulation",
            params={"query": "How to implement RAG"},
            provider="openai"
        )
        second_time = time.time() - start
        
        logger.info(f"First call: {first_time:.2f}s, Second call: {second_time:.2f}s")
        logger.info(f"Cache hit rate: {llm_service.get_cache_stats()['hit_rate']:.1f}%")
    
    # Test template manager
    logger.info("Template types available:")
    for template_type in llm_service.template_manager.templates:
        logger.info(f"- {template_type}")
    
    # Test token manager
    logger.info("Testing token manager...")
    token_manager = TokenManager()
    text = "This is a sample text to test token counting."
    tokens = token_manager.token_estimator.estimate_tokens(text)
    logger.info(f"Estimated tokens for '{text}': {tokens}")
    
    # Test query reformulation
    logger.info("Testing query reformulation...")
    reformulator = QueryReformulator(llm_service)
    query = "How to implement RAG with OpenAI?"
    reformulations = reformulator.reformulate(query)
    logger.info(f"Original query: {query}")
    for i, r in enumerate(reformulations):
        logger.info(f"Reformulation {i+1}: {r}")

if __name__ == "__main__":
    import time
    test_llm_service()
