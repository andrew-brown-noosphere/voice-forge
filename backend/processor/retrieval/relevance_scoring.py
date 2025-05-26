"""
Relevance scoring for retrieved chunks.
"""
import logging
import re
from datetime import datetime
import math
import numpy as np
from typing import Dict, List, Any, Tuple, Optional, Union

logger = logging.getLogger(__name__)

class RelevanceScorer:
    """Improved relevance scoring for retrieved chunks."""
    
    def __init__(self, config=None):
        self.config = config or {
            "semantic_weight": 0.7,
            "keyword_weight": 0.3,
            "recency_weight": 0.1,
            "authority_weight": 0.1
        }
    
    def score_chunk(self, chunk, query, query_embedding=None):
        """
        Score a chunk based on multiple factors.
        
        Args:
            chunk: The content chunk
            query: Original query string
            query_embedding: Embedding vector for the query
            
        Returns:
            Enhanced relevance score and detailed score components
        """
        scores = {}
        
        # Semantic similarity (if available)
        if query_embedding is not None and "embedding" in chunk:
            try:
                from sklearn.metrics.pairwise import cosine_similarity
                chunk_embedding = np.array(chunk["embedding"]).reshape(1, -1)
                query_embedding_arr = np.array(query_embedding).reshape(1, -1)
                scores["semantic"] = float(cosine_similarity(chunk_embedding, query_embedding_arr)[0][0])
            except Exception as e:
                logger.warning(f"Error calculating semantic similarity: {str(e)}")
                scores["semantic"] = chunk.get("similarity", 0)
        else:
            scores["semantic"] = chunk.get("similarity", 0)
        
        # Keyword match score
        scores["keyword"] = self._calculate_keyword_score(chunk["text"], query)
        
        # Recency score (if available)
        if "chunk_metadata" in chunk and "created_at" in chunk["chunk_metadata"]:
            scores["recency"] = self._calculate_recency_score(chunk["chunk_metadata"]["created_at"])
        else:
            scores["recency"] = 0.5  # Neutral score
        
        # Authority score (if available)
        if "chunk_metadata" in chunk and "domain" in chunk["chunk_metadata"]:
            scores["authority"] = self._calculate_authority_score(chunk["chunk_metadata"]["domain"])
        else:
            scores["authority"] = 0.5  # Neutral score
        
        # Calculate weighted score
        final_score = (
            self.config["semantic_weight"] * scores["semantic"] +
            self.config["keyword_weight"] * scores["keyword"] +
            self.config["recency_weight"] * scores["recency"] +
            self.config["authority_weight"] * scores["authority"]
        )
        
        # Ensure score is between 0 and 1
        final_score = max(0, min(1, final_score))
        
        return final_score, scores
    
    def _calculate_keyword_score(self, text, query):
        """Calculate keyword match score."""
        query_terms = set(query.lower().split())
        text_lower = text.lower()
        
        # Count matching terms
        matches = sum(1 for term in query_terms if term in text_lower)
        
        # Calculate score
        if len(query_terms) > 0:
            return min(1.0, matches / len(query_terms))
        return 0
    
    def _calculate_recency_score(self, timestamp_str):
        """Calculate recency score (1.0 = very recent, 0.0 = very old)."""
        try:
            # Parse timestamp
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            
            # Calculate days since creation
            now = datetime.now()
            days_ago = (now - timestamp).days
            
            # Exponential decay function: score = exp(-days_ago/30)
            score = math.exp(-days_ago/30)
            return score
            
        except (ValueError, TypeError) as e:
            logger.warning(f"Error calculating recency score: {str(e)}")
            return 0.5  # Default score
    
    def _calculate_authority_score(self, domain):
        """Calculate authority score based on domain."""
        # This would ideally be based on a curated list of authoritative domains
        # For now, just use a simple heuristic
        authority_domains = {
            "wikipedia.org": 0.9,
            "github.com": 0.8,
            "medium.com": 0.7,
            "techcrunch.com": 0.8,
            "nytimes.com": 0.9,
            "harvard.edu": 0.9,
            "stanford.edu": 0.9,
            "mit.edu": 0.9,
            "gov": 0.85,
            "edu": 0.8,
            # Add more domains as needed
        }
        
        # Check if domain matches or is a subdomain of an authority domain
        for auth_domain, score in authority_domains.items():
            if domain.endswith(auth_domain):
                return score
            
        # Check top-level domain
        tld_scores = {
            ".org": 0.7,
            ".edu": 0.8,
            ".gov": 0.85
        }
        
        for tld, score in tld_scores.items():
            if domain.endswith(tld):
                return score
        
        return 0.5  # Default score
