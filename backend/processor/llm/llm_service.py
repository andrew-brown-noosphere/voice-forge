"""
LLM service to handle API calls to OpenAI and Anthropic.
"""
import logging
import os
from typing import Dict, List, Any, Optional, Union
import time

from processor.llm.api_client import OpenAIClient, AnthropicClient
from processor.llm.token_manager import TokenManager
from processor.llm.response_cache import ResponseCache
from processor.llm.prompt_templates import PromptTemplateManager

logger = logging.getLogger(__name__)

class LLMService:
    """Service for interacting with large language models."""
    
    def __init__(self, config=None):
        self.config = config or {}
        
        # Initialize clients
        self.clients = self._init_clients()
        
        # Initialize token manager
        self.token_manager = TokenManager(
            max_tokens=self.config.get("max_tokens", 4000)
        )
        
        # Initialize response cache
        self.response_cache = ResponseCache(
            max_size=self.config.get("cache_size", 1000),
            ttl_seconds=self.config.get("cache_ttl", 3600)
        )
        
        # Initialize prompt templates
        template_file = self.config.get("template_file")
        self.template_manager = PromptTemplateManager(template_file)
        
        logger.info(f"Initialized LLM service with providers: {', '.join(self.clients.keys())}")
    
    def _init_clients(self):
        """Initialize LLM API clients."""
        clients = {}
        
        # OpenAI client
        openai_api_key = self.config.get("openai_api_key") or os.environ.get("OPENAI_API_KEY")
        if openai_api_key:
            clients["openai"] = OpenAIClient(
                api_key=openai_api_key,
                model=self.config.get("openai_model", "gpt-3.5-turbo")
            )
            logger.info(f"Initialized OpenAI client with model {self.config.get('openai_model', 'gpt-3.5-turbo')}")
        
        # Anthropic client
        anthropic_api_key = self.config.get("anthropic_api_key") or os.environ.get("ANTHROPIC_API_KEY")
        if anthropic_api_key:
            clients["anthropic"] = AnthropicClient(
                api_key=anthropic_api_key,
                model=self.config.get("anthropic_model", "claude-2")
            )
            logger.info(f"Initialized Anthropic client with model {self.config.get('anthropic_model', 'claude-2')}")
        
        # Ensure at least one client is initialized
        if not clients:
            logger.warning("No LLM clients initialized. Set API keys in config or environment variables.")
        
        return clients
    
    def generate(self, prompt_type, params, provider=None, use_cache=True):
        """
        Generate a response using the LLM.
        
        Args:
            prompt_type: Type of prompt template to use
            params: Parameters for the prompt template
            provider: LLM provider to use (openai, anthropic)
            use_cache: Whether to use response caching
            
        Returns:
            Generated response
        """
        # Get provider
        if provider is None:
            provider = next(iter(self.clients.keys()), None)
        
        if provider not in self.clients:
            available = ", ".join(self.clients.keys())
            logger.error(f"Provider '{provider}' not available. Available providers: {available}")
            raise ValueError(f"Provider '{provider}' not available. Available providers: {available}")
        
        # Get client
        client = self.clients[provider]
        
        # Generate cache key
        if use_cache:
            cache_key = {
                "prompt_type": prompt_type,
                "params": params,
                "provider": provider
            }
            
            # Check cache
            cached_response = self.response_cache.get(cache_key)
            if cached_response:
                return cached_response
        
        # Get prompt template
        try:
            prompt = self.template_manager.get_prompt(prompt_type, provider, params)
        except Exception as e:
            logger.error(f"Error preparing prompt: {str(e)}")
            raise
        
        # Optimize prompt if context is provided
        context_chunks = params.get("context_chunks")
        if context_chunks:
            prompt = self.token_manager.optimize_prompt(
                prompt=prompt,
                context_chunks=context_chunks
            )
        
        # Generate response
        start_time = time.time()
        try:
            response = client.complete(prompt)
            
            # Log completion
            elapsed_time = time.time() - start_time
            tokens = response.get("usage", {}).get("total_tokens", 0)
            logger.info(f"Generated response with {provider} in {elapsed_time:.2f}s ({tokens} tokens)")
            
            # Add to cache
            if use_cache:
                self.response_cache.set(cache_key, response)
            
            return response
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"Error generating response with {provider} after {elapsed_time:.2f}s: {str(e)}")
            
            # Try fallback provider if available
            if provider == "openai" and "anthropic" in self.clients:
                logger.info("Trying fallback to Anthropic")
                return self.generate(prompt_type, params, "anthropic", use_cache)
            elif provider == "anthropic" and "openai" in self.clients:
                logger.info("Trying fallback to OpenAI")
                return self.generate(prompt_type, params, "openai", use_cache)
            
            # No fallback available
            raise
    
    def get_cache_stats(self):
        """Get cache statistics."""
        return self.response_cache.stats()
    
    def clear_cache(self):
        """Clear the response cache."""
        self.response_cache.clear()
    
    def add_template(self, prompt_type, provider, template):
        """Add a new template."""
        self.template_manager.add_template(prompt_type, provider, template)
    
    def save_templates(self, template_file=None):
        """Save templates to file."""
        return self.template_manager.save_templates(template_file)
