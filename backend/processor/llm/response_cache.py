"""
Caching system for LLM responses.
"""
import hashlib
import json
import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ResponseCache:
    """Cache for LLM responses to reduce API calls."""
    
    def __init__(self, max_size=1000, ttl_seconds=3600):
        self.cache = {}
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.access_times = {}  # Track last access time for LRU eviction
        self.hit_count = 0
        self.miss_count = 0
    
    def get(self, key):
        """
        Get a cached response.
        
        Args:
            key: Cache key
            
        Returns:
            Cached response or None if not found
        """
        # Generate hash key
        hash_key = self._hash_key(key)
        
        # Check if key exists and is not expired
        if hash_key in self.cache:
            entry = self.cache[hash_key]
            
            # Check expiration
            if "expiration" in entry and entry["expiration"] < datetime.now():
                # Expired, remove from cache
                logger.debug(f"Cache expired for {hash_key[:8]}...")
                del self.cache[hash_key]
                if hash_key in self.access_times:
                    del self.access_times[hash_key]
                self.miss_count += 1
                return None
            
            # Update access time
            self.access_times[hash_key] = datetime.now()
            
            # Record hit
            self.hit_count += 1
            hit_rate = self.hit_count / (self.hit_count + self.miss_count) * 100
            logger.debug(f"Cache hit for {hash_key[:8]}... (hit rate: {hit_rate:.1f}%)")
            
            return entry["response"]
        
        # Record miss
        self.miss_count += 1
        logger.debug(f"Cache miss for {hash_key[:8]}...")
        return None
    
    def set(self, key, response):
        """
        Store a response in the cache.
        
        Args:
            key: Cache key
            response: Response to cache
            
        Returns:
            None
        """
        # Check cache size
        if len(self.cache) >= self.max_size:
            self._evict()
        
        # Generate hash key
        hash_key = self._hash_key(key)
        
        # Calculate expiration
        expiration = datetime.now() + timedelta(seconds=self.ttl_seconds)
        
        # Store in cache
        self.cache[hash_key] = {
            "response": response,
            "expiration": expiration
        }
        
        # Update access time
        self.access_times[hash_key] = datetime.now()
        logger.debug(f"Cached response for {hash_key[:8]}... (cache size: {len(self.cache)})")
    
    def _hash_key(self, key):
        """Generate a hash for a cache key."""
        if isinstance(key, (dict, list, tuple)):
            key = json.dumps(key, sort_keys=True)
        
        return hashlib.md5(str(key).encode()).hexdigest()
    
    def _evict(self):
        """Evict least recently used entries."""
        if not self.access_times:
            return
        
        # Find oldest entry
        oldest_key = min(self.access_times, key=lambda k: self.access_times[k])
        
        # Remove from cache
        if oldest_key in self.cache:
            del self.cache[oldest_key]
        
        # Remove from access times
        del self.access_times[oldest_key]
        logger.debug(f"Evicted LRU entry {oldest_key[:8]}... from cache")
    
    def clear(self):
        """Clear the cache."""
        self.cache = {}
        self.access_times = {}
        logger.info(f"Cache cleared. Hit rate: {self.hit_rate():.1f}%")
    
    def hit_rate(self):
        """Calculate hit rate percentage."""
        total = self.hit_count + self.miss_count
        if total == 0:
            return 0
        return (self.hit_count / total) * 100
    
    def stats(self):
        """Get cache statistics."""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "ttl_seconds": self.ttl_seconds,
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate": self.hit_rate()
        }
