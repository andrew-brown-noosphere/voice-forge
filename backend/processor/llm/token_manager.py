"""
Token management for LLM API calls.
"""
import logging
import re
from typing import List, Dict, Any, Optional, Union, Tuple

logger = logging.getLogger(__name__)

class TokenManager:
    """Manages token usage and optimizations for LLM calls."""
    
    def __init__(self, max_tokens=4000):
        self.max_tokens = max_tokens
        self.token_estimator = TokenEstimator()
    
    def optimize_prompt(self, prompt, context_chunks=None, reserved_tokens=200):
        """
        Optimize a prompt to fit within token limits.
        
        Args:
            prompt: Base prompt template or messages
            context_chunks: Context chunks to include
            reserved_tokens: Tokens to reserve for completion
            
        Returns:
            Optimized prompt
        """
        if not context_chunks:
            # No optimization needed
            return prompt
        
        # Calculate available tokens for context
        prompt_tokens = self.token_estimator.estimate_tokens(prompt)
        available_tokens = self.max_tokens - prompt_tokens - reserved_tokens
        
        if available_tokens <= 0:
            logger.warning(f"Prompt already exceeds token limit: {prompt_tokens} tokens")
            # Return prompt without context
            return prompt
        
        # Optimize context chunks to fit
        optimized_context = self._fit_chunks_to_tokens(context_chunks, available_tokens)
        
        # Insert context into prompt
        if isinstance(prompt, str):
            # For string prompts, append context
            prompt_with_context = prompt + "\n\nContext:\n" + optimized_context
            return prompt_with_context
        elif isinstance(prompt, list):
            # For message prompts, add context to system message or create one
            for i, msg in enumerate(prompt):
                if msg["role"] == "system":
                    prompt[i]["content"] += f"\n\nContext:\n{optimized_context}"
                    return prompt
            
            # No system message found, add one
            system_msg = {"role": "system", "content": f"Context:\n{optimized_context}"}
            return [system_msg] + prompt
        
        return prompt
    
    def _fit_chunks_to_tokens(self, chunks, max_tokens):
        """Fit chunks into token limit."""
        total_tokens = 0
        included_chunks = []
        
        # Sort chunks by relevance
        chunks = sorted(chunks, key=lambda x: x.get("similarity", 0), reverse=True)
        
        for chunk in chunks:
            chunk_text = chunk["text"]
            chunk_tokens = self.token_estimator.estimate_tokens(chunk_text)
            
            if total_tokens + chunk_tokens <= max_tokens:
                # Add complete chunk
                included_chunks.append(chunk_text)
                total_tokens += chunk_tokens
            else:
                # Try to add partial chunk if at least 100 tokens available
                if max_tokens - total_tokens >= 100:
                    # Truncate chunk to fit
                    available_tokens = max_tokens - total_tokens
                    truncated_chunk = self.token_estimator.truncate_to_tokens(chunk_text, available_tokens)
                    included_chunks.append(truncated_chunk)
                
                # Stop adding chunks
                break
        
        # Combine chunks
        return "\n\n".join(included_chunks)

class TokenEstimator:
    """Estimates token counts for text."""
    
    def __init__(self):
        # Try to import tiktoken if available
        self.tiktoken_available = False
        self.tiktoken_model = None
        
        try:
            import tiktoken
            self.tiktoken_available = True
            logger.info("Using tiktoken for token estimation")
            # Default to cl100k_base which is used by OpenAI chat models
            self.tiktoken_model = tiktoken.get_encoding("cl100k_base")
        except ImportError:
            logger.warning("tiktoken not available, using word-based token estimation")
    
    def estimate_tokens(self, text):
        """Estimate the number of tokens in text."""
        if self.tiktoken_available:
            return self._estimate_tokens_tiktoken(text)
        else:
            return self._estimate_tokens_words(text)
    
    def _estimate_tokens_tiktoken(self, text):
        """Estimate tokens using tiktoken."""
        if isinstance(text, list):
            # Handle message lists
            token_count = 0
            for msg in text:
                # Simplified message token counting
                token_count += len(self.tiktoken_model.encode(msg.get("content", "")))
                token_count += 4  # Approx overhead for role
            return token_count + 2  # Final overhead
        else:
            # Simple string
            return len(self.tiktoken_model.encode(text))
    
    def _estimate_tokens_words(self, text):
        """Estimate tokens based on word count."""
        if isinstance(text, list):
            # Handle message lists
            return sum(self._estimate_tokens_words(msg.get("content", "")) for msg in text) + len(text) * 4
        
        # Simple estimation: ~1.3 tokens per word
        words = len(re.findall(r'\b\w+\b', text))
        return int(words * 1.3) + 10  # Add small constant for safety
    
    def truncate_to_tokens(self, text, max_tokens):
        """Truncate text to fit within token limit."""
        if self.tiktoken_available:
            return self._truncate_to_tokens_tiktoken(text, max_tokens)
        else:
            return self._truncate_to_tokens_words(text, max_tokens)
    
    def _truncate_to_tokens_tiktoken(self, text, max_tokens):
        """Truncate using tiktoken."""
        tokens = self.tiktoken_model.encode(text)
        
        if len(tokens) <= max_tokens:
            return text
        
        # Truncate tokens and decode
        truncated_tokens = tokens[:max_tokens-1]  # Leave room for ellipsis
        truncated_text = self.tiktoken_model.decode(truncated_tokens)
        
        # Try to end at punctuation
        match = re.search(r'.*[.!?]', truncated_text)
        if match:
            truncated_text = match.group(0)
        
        return truncated_text + "..."
    
    def _truncate_to_tokens_words(self, text, max_tokens):
        """Truncate based on words."""
        if self._estimate_tokens_words(text) <= max_tokens:
            return text
        
        # Simple truncation by words
        words = text.split()
        words_limit = int(max_tokens / 1.3)  # Approximation
        
        truncated_text = " ".join(words[:words_limit])
        
        # Try to end at punctuation
        match = re.search(r'.*[.!?]', truncated_text)
        if match:
            truncated_text = match.group(0)
        
        return truncated_text + "..."
