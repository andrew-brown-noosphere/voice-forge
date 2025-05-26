#!/usr/bin/env python3
"""
Test script for OpenAI API connection.
Run this to verify your API key is working.
"""
import os
import sys
import logging
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables from .env file
load_dotenv()

from processor.llm.llm_service import LLMService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_openai_connection():
    """Test OpenAI API connection."""
    
    # Check if API key is set
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY not found in environment variables.")
        logger.info("Please set your OpenAI API key in one of these ways:")
        logger.info("1. Environment variable: export OPENAI_API_KEY='your-key-here'")
        logger.info("2. Add to .env file: OPENAI_API_KEY=your-key-here")
        return False
    
    logger.info(f"Found OpenAI API key: {api_key[:10]}...")
    
    # Initialize LLM service
    config = {
        "openai_model": "gpt-3.5-turbo",
        "cache_size": 10,
        "cache_ttl": 300  # 5 minutes
    }
    
    try:
        llm_service = LLMService(config)
        
        if "openai" not in llm_service.clients:
            logger.error("OpenAI client not initialized. Check your API key.")
            return False
        
        logger.info("OpenAI client initialized successfully!")
        
        # Test a simple completion
        logger.info("Testing OpenAI API call...")
        response = llm_service.generate(
            prompt_type="rag_response",
            params={
                "query": "What is artificial intelligence?",
                "context": "Artificial intelligence (AI) is the simulation of human intelligence in machines that are programmed to think and learn."
            },
            provider="openai"
        )
        
        logger.info("✅ OpenAI API test successful!")
        logger.info(f"Response: {response['text'][:200]}...")
        logger.info(f"Tokens used: {response.get('usage', {})}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ OpenAI API test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_openai_connection()
    if success:
        print("\n🎉 Your OpenAI API key is working correctly!")
    else:
        print("\n❌ OpenAI API test failed. Please check your API key.")
