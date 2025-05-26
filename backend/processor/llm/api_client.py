"""
API clients for LLM providers (OpenAI and Anthropic).
"""
import requests
import json
import time
import logging
import os
from typing import Dict, List, Any, Optional, Union

logger = logging.getLogger(__name__)

class LLMAPIClient:
    """Base class for LLM API clients."""
    
    def __init__(self, api_key=None, timeout=30, max_retries=3, retry_delay=1):
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def _make_request(self, url, data, headers, method="POST"):
        """Make an HTTP request with retries."""
        for attempt in range(self.max_retries):
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                    timeout=self.timeout
                )
                
                # Check for success
                response.raise_for_status()
                
                # Return response
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt+1}/{self.max_retries}): {str(e)}")
                
                # Check if we should retry
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    sleep_time = self.retry_delay * (2 ** attempt)
                    logger.debug(f"Retrying in {sleep_time} seconds")
                    time.sleep(sleep_time)
                else:
                    # Max retries reached
                    logger.error(f"Max retries reached: {str(e)}")
                    raise
    
    def complete(self, prompt, **kwargs):
        """
        Generate a completion.
        
        Args:
            prompt: The prompt text
            **kwargs: Additional parameters
            
        Returns:
            Completion response
        """
        raise NotImplementedError("Subclasses must implement this method")

class OpenAIClient(LLMAPIClient):
    """Client for OpenAI API."""
    
    def __init__(
        self, 
        api_key=None, 
        model="gpt-3.5-turbo",
        base_url="https://api.openai.com/v1",
        **kwargs
    ):
        super().__init__(api_key=api_key or os.environ.get("OPENAI_API_KEY"), **kwargs)
        self.model = model
        self.base_url = base_url
        self.chat_url = f"{self.base_url}/chat/completions"
    
    def complete(self, prompt, **kwargs):
        """Generate a completion using OpenAI API."""
        # Prepare request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Format as messages
        if isinstance(prompt, str):
            messages = [{"role": "user", "content": prompt}]
        elif isinstance(prompt, list):
            messages = prompt
        else:
            raise ValueError("Prompt must be a string or a list of messages")
        
        # Prepare data
        data = {
            "model": kwargs.get("model", self.model),
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 800),
            "top_p": kwargs.get("top_p", 1.0),
            "frequency_penalty": kwargs.get("frequency_penalty", 0),
            "presence_penalty": kwargs.get("presence_penalty", 0),
        }
        
        # Log request (without API key)
        logger.debug(f"OpenAI request: model={data['model']}, temp={data['temperature']}")
        
        # Make request
        try:
            response = self._make_request(self.chat_url, data, headers)
            
            # Process response
            if "choices" in response and len(response["choices"]) > 0:
                return {
                    "text": response["choices"][0]["message"]["content"],
                    "finish_reason": response["choices"][0]["finish_reason"],
                    "model": response["model"],
                    "usage": response.get("usage", {}),
                    "raw_response": response
                }
            else:
                logger.error(f"Unexpected response format: {response}")
                raise ValueError("Unexpected response format")
                
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise

class AnthropicClient(LLMAPIClient):
    """Client for Anthropic API."""
    
    def __init__(
        self, 
        api_key=None, 
        model="claude-2",
        base_url="https://api.anthropic.com/v1",
        **kwargs
    ):
        super().__init__(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"), **kwargs)
        self.model = model
        self.base_url = base_url
        self.api_url = f"{self.base_url}/complete"
    
    def complete(self, prompt, **kwargs):
        """Generate a completion using Anthropic API."""
        # Prepare request
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        # Format prompt
        if isinstance(prompt, list):
            # Convert messages to Anthropic format
            formatted_prompt = ""
            for msg in prompt:
                role = msg.get("role", "user")
                if role == "system":
                    formatted_prompt += f"{msg['content']}\n\n"
                elif role == "user":
                    formatted_prompt += f"Human: {msg['content']}\n\n"
                elif role == "assistant":
                    formatted_prompt += f"Assistant: {msg['content']}\n\n"
            
            # Add final "Assistant:" if needed
            if not formatted_prompt.endswith("Assistant: "):
                formatted_prompt += "Assistant: "
        else:
            # Single string
            formatted_prompt = f"Human: {prompt}\n\nAssistant: "
        
        # Prepare data
        data = {
            "prompt": formatted_prompt,
            "model": kwargs.get("model", self.model),
            "max_tokens_to_sample": kwargs.get("max_tokens", 1000),
            "temperature": kwargs.get("temperature", 0.7),
            "top_p": kwargs.get("top_p", 1.0),
            "stop_sequences": kwargs.get("stop_sequences", ["\n\nHuman:"])
        }
        
        # Log request (without API key)
        logger.debug(f"Anthropic request: model={data['model']}, temp={data['temperature']}")
        
        # Make request
        try:
            response = self._make_request(self.api_url, data, headers)
            
            # Process response
            if "completion" in response:
                return {
                    "text": response["completion"],
                    "finish_reason": response.get("stop_reason", "stop"),
                    "model": self.model,
                    "usage": {"prompt_tokens": -1, "completion_tokens": -1, "total_tokens": -1},  # Not provided by Anthropic
                    "raw_response": response
                }
            else:
                logger.error(f"Unexpected response format: {response}")
                raise ValueError("Unexpected response format")
                
        except Exception as e:
            logger.error(f"Anthropic API error: {str(e)}")
            raise
