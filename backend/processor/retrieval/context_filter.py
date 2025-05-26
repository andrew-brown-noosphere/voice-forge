"""
Context-aware filtering for retrieved chunks.
"""
import logging
from datetime import datetime
import math
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class ContextFilter:
    """Filter chunks based on contextual factors."""
    
    def __init__(self, config=None):
        self.config = config or {
            "min_recency_score": 0.3,  # Filter out very old content
            "min_relevance": 0.2,      # Filter out irrelevant content
            "diversify_sources": True,  # Include chunks from different sources
            "max_per_source": 2        # Max chunks from the same source
        }
    
    def filter_chunks(self, chunks, query=None, user_context=None):
        """
        Filter chunks based on context.
        
        Args:
            chunks: List of chunks to filter
            query: Original query
            user_context: Optional user context (preferences, history)
            
        Returns:
            Filtered list of chunks
        """
        if not chunks:
            return []
        
        filtered_chunks = []
        source_counts = {}  # Track counts of chunks per source
        
        # Sort chunks by similarity first
        sorted_chunks = sorted(chunks, key=lambda x: x.get("similarity", 0), reverse=True)
        
        for chunk in sorted_chunks:
            # Apply recency filter if configured
            if self.config["min_recency_score"] > 0:
                recency_score = self._get_recency_score(chunk)
                if recency_score < self.config["min_recency_score"]:
                    continue
            
            # Apply relevance filter
            if chunk.get("similarity", 0) < self.config["min_relevance"]:
                continue
            
            # Apply source diversity if configured
            if self.config["diversify_sources"]:
                source_id = self._get_source_id(chunk)
                if source_id in source_counts:
                    if source_counts[source_id] >= self.config["max_per_source"]:
                        continue
                    source_counts[source_id] += 1
                else:
                    source_counts[source_id] = 1
            
            filtered_chunks.append(chunk)
        
        # Log filtering stats
        original_count = len(chunks)
        filtered_count = len(filtered_chunks)
        logger.info(f"Filtered chunks: {original_count} -> {filtered_count} ({filtered_count/max(1, original_count):.1%} kept)")
        
        return filtered_chunks
    
    def _get_recency_score(self, chunk):
        """Extract recency score from chunk."""
        # From score_components if available
        if "score_components" in chunk and "recency" in chunk["score_components"]:
            return chunk["score_components"]["recency"]
        
        # Calculate from metadata if available
        if "chunk_metadata" in chunk and "created_at" in chunk["chunk_metadata"]:
            try:
                from datetime import datetime
                timestamp = datetime.fromisoformat(
                    chunk["chunk_metadata"]["created_at"].replace('Z', '+00:00')
                )
                now = datetime.now()
                days_ago = (now - timestamp).days
                import math
                return math.exp(-days_ago/30)
            except (ValueError, TypeError) as e:
                logger.warning(f"Error calculating recency: {str(e)}")
        
        return 0.5  # Default score
    
    def _get_source_id(self, chunk):
        """Get a unique identifier for the source of a chunk."""
        # Try content_id first
        if "content_id" in chunk:
            return chunk["content_id"]
        
        # Try domain
        if "chunk_metadata" in chunk and "domain" in chunk["chunk_metadata"]:
            return chunk["chunk_metadata"]["domain"]
        
        # Fallback to chunk id
        return chunk.get("id", "unknown")
