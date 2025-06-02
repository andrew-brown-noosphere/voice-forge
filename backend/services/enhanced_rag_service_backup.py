# Backup of original enhanced_rag_service.py
# This is the original complex version that was causing empty context retrieval
# due to complex joins with the crawls table.
# 
# Backed up on: Current timestamp
# 
# The original file has been temporarily replaced with a simplified version
# that bypasses the crawls table complexity and gets content retrieval working.

"""
Enhanced RAG Service for VoiceForge with Hybrid Retrieval and Cross-Encoder Reranking.

This service implements hybrid retrieval combining:
- Semantic search (vector similarity)
- Keyword search (PostgreSQL full-text search)
- Domain-aware filtering
- Cross-encoder reranking for improved relevance

Author: VoiceForge Development Team
"""

import asyncio
import logging
import re
import hashlib
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod

import numpy as np
import nltk
from sentence_transformers import CrossEncoder
from sqlalchemy import text
from sqlalchemy.orm import Session

# Download required NLTK data (only if not already present)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Represents a search result with metadata."""
    content: str
    metadata: Dict[str, Any]
    original_score: float
    rerank_score: Optional[float] = None
    search_type: str = "unknown"
    content_hash: Optional[str] = None

    def __post_init__(self):
        """Generate content hash for deduplication."""
        if self.content_hash is None:
            # Use first 200 characters for hashing
            content_preview = self.content[:200]
            self.content_hash = hashlib.md5(content_preview.encode()).hexdigest()

class SearchStrategy(ABC):
    """Abstract base class for search strategies."""
    
    @abstractmethod
    async def search(self, query: str, limit: int, org_id: str, **kwargs) -> List[SearchResult]:
        """Execute search strategy and return results."""
        pass

class SemanticSearchStrategy(SearchStrategy):
    """Vector similarity search strategy."""
    
    def __init__(self, db: Session, vector_service):
        self.db = db
        self.vector_service = vector_service
    
    async def search(self, query: str, limit: int, org_id: str, **kwargs) -> List[SearchResult]:
        """Execute semantic search using vector similarity."""
        try:
            # Get query embedding
            query_embedding = await self.vector_service.get_embedding(query)
            
            if not query_embedding:
                logger.warning("Failed to generate query embedding for semantic search")
                return []
            
            # Build vector similarity query
            similarity_query = text("""
                SELECT 
                    cc.text as content,
                    c.domain,
                    c.id as content_id,
                    c.title,
                    cc.id as chunk_id,
                    cc.chunk_metadata,
                    1 - (cc.embedding <=> :query_embedding) as similarity
                FROM content_chunks cc
                JOIN contents c ON cc.content_id = c.id
                JOIN crawls cr ON c.crawl_id = cr.id
                WHERE cr.org_id = :org_id
                    AND cc.embedding IS NOT NULL
                ORDER BY cc.embedding <=> :query_embedding
                LIMIT :limit
            """)
            
            # Apply domain filter if specified
            domain_filter = kwargs.get('domain')
            if domain_filter:
                similarity_query = text(str(similarity_query).replace(
                    "WHERE cr.org_id = :org_id",
                    "WHERE cr.org_id = :org_id AND c.domain = :domain"
                ))
            
            # Apply content type filter if specified
            content_type_filter = kwargs.get('content_type')
            if content_type_filter:
                similarity_query = text(str(similarity_query).replace(
                    "AND cc.embedding IS NOT NULL",
                    "AND cc.embedding IS NOT NULL AND c.content_type = :content_type"
                ))
            
            params = {
                'query_embedding': query_embedding,
                'org_id': org_id,
                'limit': limit
            }
            
            if domain_filter:
                params['domain'] = domain_filter
            if content_type_filter:
                params['content_type'] = content_type_filter
            
            result = self.db.execute(similarity_query, params)
            rows = result.fetchall()
            
            results = []
            for row in rows:
                metadata = {
                    'search_type': 'semantic',
                    'content_id': row.content_id,
                    'chunk_id': row.chunk_id,
                    'domain': row.domain,
                    'title': row.title,
                    'chunk_metadata': row.chunk_metadata or {}
                }
                
                results.append(SearchResult(
                    content=row.content,
                    metadata=metadata,
                    original_score=float(row.similarity),
                    search_type='semantic'
                ))
            
            logger.info(f"Semantic search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []

class KeywordSearchStrategy(SearchStrategy):
    """PostgreSQL full-text search strategy."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def search(self, query: str, limit: int, org_id: str, **kwargs) -> List[SearchResult]:
        """Execute keyword search using PostgreSQL full-text search."""
        try:
            # Extract search terms from query
            search_terms = self._extract_search_terms(query)
            
            if not search_terms:
                logger.warning("No valid search terms extracted for keyword search")
                return []
            
            # Build full-text search query
            keyword_query = text("""
                SELECT 
                    cc.text as content,
                    c.domain,
                    c.id as content_id,
                    c.title,
                    cc.id as chunk_id,
                    cc.chunk_metadata,
                    ts_rank(to_tsvector('english', cc.text), plainto_tsquery('english', :search_terms)) as rank
                FROM content_chunks cc
                JOIN contents c ON cc.content_id = c.id
                JOIN crawls cr ON c.crawl_id = cr.id
                WHERE cr.org_id = :org_id
                    AND to_tsvector('english', cc.text) @@ plainto_tsquery('english', :search_terms)
                ORDER BY rank DESC
                LIMIT :limit
            """)
            
            # Apply domain filter if specified
            domain_filter = kwargs.get('domain')
            if domain_filter:
                keyword_query = text(str(keyword_query).replace(
                    "WHERE cr.org_id = :org_id",
                    "WHERE cr.org_id = :org_id AND c.domain = :domain"
                ))
            
            # Apply content type filter if specified
            content_type_filter = kwargs.get('content_type')
            if content_type_filter:
                keyword_query = text(str(keyword_query).replace(
                    "AND to_tsvector",
                    "AND c.content_type = :content_type AND to_tsvector"
                ))
            
            params = {
                'search_terms': search_terms,
                'org_id': org_id,
                'limit': limit
            }
            
            if domain_filter:
                params['domain'] = domain_filter
            if content_type_filter:
                params['content_type'] = content_type_filter
            
            result = self.db.execute(keyword_query, params)
            rows = result.fetchall()
            
            results = []
            for row in rows:
                metadata = {
                    'search_type': 'keyword',
                    'content_id': row.content_id,
                    'chunk_id': row.chunk_id,
                    'domain': row.domain,
                    'title': row.title,
                    'chunk_metadata': row.chunk_metadata or {}
                }
                
                results.append(SearchResult(
                    content=row.content,
                    metadata=metadata,
                    original_score=float(row.rank),
                    search_type='keyword'
                ))
            
            logger.info(f"Keyword search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Keyword search failed: {e}")
            return []
    
    def _extract_search_terms(self, query: str) -> str:
        """Extract meaningful search terms from query."""
        try:
            # Tokenize and clean
            tokens = word_tokenize(query.lower())
            
            # Remove stopwords and short words
            stop_words = set(stopwords.words('english'))
            meaningful_terms = [
                token for token in tokens 
                if token.isalnum() and len(token) > 2 and token not in stop_words
            ]
            
            # Return top 10 terms
            return ' '.join(meaningful_terms[:10])
            
        except Exception as e:
            logger.warning(f"Failed to extract search terms: {e}")
            return query  # Fallback to original query

class DomainFilteredSearchStrategy(SearchStrategy):
    """Domain-aware vector search strategy."""
    
    def __init__(self, db: Session, vector_service):
        self.db = db
        self.vector_service = vector_service
    
    async def search(self, query: str, limit: int, org_id: str, **kwargs) -> List[SearchResult]:
        """Execute domain-filtered semantic search."""
        try:
            domain_hints = self._extract_domain_hints(query)
            
            if not domain_hints:
                return []  # No domain hints found
            
            # Get query embedding
            query_embedding = await self.vector_service.get_embedding(query)
            
            if not query_embedding:
                return []
            
            results = []
            
            for domain_hint in domain_hints:
                # Build domain-specific query
                domain_query = text("""
                    SELECT 
                        cc.text as content,
                        c.domain,
                        c.id as content_id,
                        c.title,
                        cc.id as chunk_id,
                        cc.chunk_metadata,
                        1 - (cc.embedding <=> :query_embedding) as similarity
                    FROM content_chunks cc
                    JOIN contents c ON cc.content_id = c.id
                    JOIN crawls cr ON c.crawl_id = cr.id
                    WHERE cr.org_id = :org_id
                        AND cc.embedding IS NOT NULL
                        AND c.domain ILIKE :domain_pattern
                    ORDER BY cc.embedding <=> :query_embedding
                    LIMIT :limit_per_domain
                """)
                
                params = {
                    'query_embedding': query_embedding,
                    'org_id': org_id,
                    'domain_pattern': f'%{domain_hint}%',
                    'limit_per_domain': limit // len(domain_hints)
                }
                
                result = self.db.execute(domain_query, params)
                rows = result.fetchall()
                
                for row in rows:
                    metadata = {
                        'search_type': 'domain',
                        'content_id': row.content_id,
                        'chunk_id': row.chunk_id,
                        'domain': row.domain,
                        'title': row.title,
                        'chunk_metadata': row.chunk_metadata or {},
                        'domain_hint': domain_hint
                    }
                    
                    results.append(SearchResult(
                        content=row.content,
                        metadata=metadata,
                        original_score=float(row.similarity),
                        search_type='domain'
                    ))
            
            logger.info(f"Domain search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Domain search failed: {e}")
            return []
    
    def _extract_domain_hints(self, query: str) -> List[str]:
        """Extract domain hints from query using pattern matching."""
        # Look for common domain indicators
        domain_patterns = [
            r'\b([a-zA-Z0-9-]+\.(?:com|org|net|edu|gov|io|co))\b',  # Full domains
            r'\b(twitter|facebook|instagram|linkedin|github|stackoverflow)\b',  # Platform names
            r'\b(blog|docs|support|help|api)\b'  # Common subdomains
        ]
        
        domain_hints = []
        for pattern in domain_patterns:
            matches = re.findall(pattern, query.lower())
            domain_hints.extend(matches)
        
        return list(set(domain_hints))  # Remove duplicates

class CrossEncoderReranker:
    """Cross-encoder model for reranking search results."""
    
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the cross-encoder model."""
        try:
            self.model = CrossEncoder(self.model_name)
            logger.info(f"Cross-encoder model {self.model_name} loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load cross-encoder model: {e}")
            self.model = None
    
    async def rerank(self, query: str, results: List[SearchResult]) -> List[SearchResult]:
        """Rerank results using cross-encoder model."""
        if not self.model or not results:
            return results
        
        try:
            # Prepare query-document pairs
            pairs = []
            for result in results:
                # Truncate content to 512 tokens for efficiency
                truncated_content = result.content[:512]
                pairs.append([query, truncated_content])
            
            # Get rerank scores
            scores = self.model.predict(pairs)
            
            # Update results with rerank scores
            for i, result in enumerate(results):
                result.rerank_score = float(scores[i])
            
            # Sort by rerank score
            reranked_results = sorted(results, key=lambda x: x.rerank_score or 0, reverse=True)
            
            logger.info(f"Reranked {len(results)} results")
            return reranked_results
            
        except Exception as e:
            logger.error(f"Reranking failed: {e}")
            return results  # Return original results if reranking fails

class HybridRAGService:
    """Main hybrid RAG service orchestrating multiple search strategies."""
    
    def __init__(self, db: Session, vector_service=None):
        self.db = db
        self.vector_service = vector_service
        self.reranker = CrossEncoderReranker()
        
        # Initialize search strategies
        self.strategies = {
            'semantic': SemanticSearchStrategy(db, vector_service),
            'keyword': KeywordSearchStrategy(db),
            'domain': DomainFilteredSearchStrategy(db, vector_service)
        }
    
    async def retrieve_and_rank(
        self,
        query: str,
        strategy: str = "hybrid",
        top_k: int = 10,
        org_id: str = None,
        domain: Optional[str] = None,
        content_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main method for hybrid retrieval and reranking.
        
        Args:
            query: Search query
            strategy: "hybrid", "semantic", "keyword", or "domain"
            top_k: Number of results to return
            org_id: Organization ID for multi-tenant filtering
            domain: Optional domain filter
            content_type: Optional content type filter
            
        Returns:
            Dictionary with ranked results and retrieval statistics
        """
        try:
            # Determine which strategies to use
            if strategy == "hybrid":
                strategy_names = ["semantic", "keyword", "domain"]
            elif strategy in self.strategies:
                strategy_names = [strategy]
            else:
                raise ValueError(f"Unknown strategy: {strategy}")
            
            # Execute search strategies concurrently
            search_tasks = []
            for strategy_name in strategy_names:
                if strategy_name in self.strategies:
                    task = self.strategies[strategy_name].search(
                        query=query,
                        limit=top_k * 2,  # Get more results for better merging
                        org_id=org_id,
                        domain=domain,
                        content_type=content_type
                    )
                    search_tasks.append((strategy_name, task))
            
            # Await all search tasks
            strategy_results = {}
            for strategy_name, task in search_tasks:
                try:
                    results = await task
                    strategy_results[strategy_name] = results
                except Exception as e:
                    logger.error(f"Strategy {strategy_name} failed: {e}")
                    strategy_results[strategy_name] = []
            
            # Merge and deduplicate results
            merged_results = self._merge_and_deduplicate(strategy_results)
            
            # Rerank using cross-encoder
            reranked_results = await self.reranker.rerank(query, merged_results)
            
            # Take top_k results
            final_results = reranked_results[:top_k]
            
            # Calculate retrieval statistics
            stats = self._calculate_retrieval_stats(strategy_results, merged_results, final_results)
            
            # Format response
            response = {
                "query": query,
                "results": [self._format_result(result) for result in final_results],
                "retrieval_stats": stats
            }
            
            logger.info(f"Hybrid retrieval completed: {len(final_results)} results returned")
            return response
            
        except Exception as e:
            logger.error(f"Hybrid retrieval failed: {e}")
            return {
                "query": query,
                "results": [],
                "retrieval_stats": {"error": str(e)},
                "error": str(e)
            }
    
    def _merge_and_deduplicate(self, strategy_results: Dict[str, List[SearchResult]]) -> List[SearchResult]:
        """Merge results from different strategies and remove duplicates."""
        all_results = []
        seen_hashes = set()
        
        # Collect all results
        for strategy_name, results in strategy_results.items():
            for result in results:
                if result.content_hash not in seen_hashes:
                    seen_hashes.add(result.content_hash)
                    all_results.append(result)
        
        # Normalize scores to 0-1 range for fair comparison
        self._normalize_scores(all_results)
        
        # Sort by normalized score
        all_results.sort(key=lambda x: x.original_score, reverse=True)
        
        return all_results
    
    def _normalize_scores(self, results: List[SearchResult]):
        """Normalize scores from different search methods to 0-1 scale."""
        if not results:
            return
        
        # Group by search type
        by_type = {}
        for result in results:
            if result.search_type not in by_type:
                by_type[result.search_type] = []
            by_type[result.search_type].append(result)
        
        # Normalize within each type
        for search_type, type_results in by_type.items():
            scores = [r.original_score for r in type_results]
            if len(scores) <= 1:
                continue
                
            min_score = min(scores)
            max_score = max(scores)
            score_range = max_score - min_score
            
            if score_range > 0:
                for result in type_results:
                    result.original_score = (result.original_score - min_score) / score_range
    
    def _calculate_retrieval_stats(
        self,
        strategy_results: Dict[str, List[SearchResult]],
        merged_results: List[SearchResult],
        final_results: List[SearchResult]
    ) -> Dict[str, Any]:
        """Calculate retrieval statistics for debugging and optimization."""
        strategy_counts = {k: len(v) for k, v in strategy_results.items()}
        
        # Calculate average final score
        avg_final_score = 0.0
        if final_results:
            final_scores = [r.rerank_score or r.original_score for r in final_results]
            avg_final_score = sum(final_scores) / len(final_scores)
        
        # Calculate deduplication ratio
        total_before_dedup = sum(strategy_counts.values())
        dedup_ratio = len(merged_results) / total_before_dedup if total_before_dedup > 0 else 1.0
        
        return {
            "total_strategies_used": len([k for k, v in strategy_counts.items() if v > 0]),
            "strategy_results": strategy_counts,
            "merged_unique_results": len(merged_results),
            "final_ranked_results": len(final_results),
            "deduplication_ratio": round(dedup_ratio, 3),
            "avg_final_score": round(avg_final_score, 3)
        }
    
    def _format_result(self, result: SearchResult) -> Dict[str, Any]:
        """Format search result for API response."""
        return {
            "content": result.content,
            "metadata": {
                **result.metadata,
                "rerank_score": round(result.rerank_score, 3) if result.rerank_score else None,
                "original_score": round(result.original_score, 3),
                "search_type": result.search_type
            }
        }

# Keyword extraction utility
class KeywordExtractor:
    """Utility class for extracting keywords from queries."""
    
    @staticmethod
    def extract_keywords(query: str, max_keywords: int = 10) -> List[str]:
        """Extract meaningful keywords from a query."""
        try:
            # Tokenize and clean
            tokens = word_tokenize(query.lower())
            
            # Remove stopwords and short words
            stop_words = set(stopwords.words('english'))
            keywords = [
                token for token in tokens 
                if token.isalnum() and len(token) > 2 and token not in stop_words
            ]
            
            return keywords[:max_keywords]
            
        except Exception as e:
            logger.warning(f"Failed to extract keywords: {e}")
            return []

# Factory function for creating the service
def create_hybrid_rag_service(db: Session, vector_service=None) -> HybridRAGService:
    """Factory function to create a HybridRAGService instance."""
    return HybridRAGService(db, vector_service)
