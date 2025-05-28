"""
Hybrid retrieval combining vector and keyword search.
"""
import logging
from typing import Dict, List, Any, Optional, Union
import time

logger = logging.getLogger(__name__)

class HybridRetriever:
    """Combines vector and keyword search results."""
    
    def __init__(self, db, embedding_model=None):
        self.db = db
        self.embedding_model = embedding_model
        self.vector_weight = 0.7  # Weight for vector search results
        self.keyword_weight = 0.3  # Weight for keyword search results
    
    def retrieve(self, query, top_k=5, domain=None, content_type=None, org_id=None):
        """
        Perform hybrid retrieval.
        
        Args:
            query: Search query
            top_k: Number of results to return
            domain: Optional domain filter
            content_type: Optional content type filter
            org_id: Organization ID for multi-tenant isolation
            
        Returns:
            Combined search results
        """
        start_time = time.time()
        
        # Step 1: Get query embedding
        query_embedding = None
        if self.embedding_model:
            try:
                query_embedding = self.embedding_model.encode(query).tolist()
                logger.debug(f"Generated query embedding for: {query[:30]}...")
            except Exception as e:
                logger.warning(f"Error generating query embedding: {str(e)}")
        
        # Step 2: Perform vector search
        vector_results = []
        if query_embedding:
            try:
                vector_results = self.db.search_chunks_by_vector(
                    query_embedding=query_embedding,
                    top_k=top_k*2,  # Get more results than needed
                    domain=domain,
                    content_type=content_type,
                    org_id=org_id  # Pass org_id for multi-tenant isolation
                )
                logger.debug(f"Vector search found {len(vector_results)} results")
            except Exception as e:
                logger.warning(f"Vector search failed: {str(e)}")
        
        # Step 3: Perform keyword search
        keyword_results = []
        try:
            keyword_results = self.db.search_chunks_by_text(
                query=query,
                top_k=top_k*2,  # Get more results than needed
                domain=domain,
                content_type=content_type,
                org_id=org_id  # Pass org_id for multi-tenant isolation
            )
            logger.debug(f"Keyword search found {len(keyword_results)} results")
        except Exception as e:
            logger.warning(f"Keyword search failed: {str(e)}")
        
        # Step 4: Combine results
        combined_results = self._combine_results(
            vector_results=vector_results,
            keyword_results=keyword_results,
            top_k=top_k
        )
        
        elapsed_time = time.time() - start_time
        logger.info(f"Hybrid retrieval completed in {elapsed_time:.2f}s, found {len(combined_results)} results")
        
        return combined_results
    
    def _combine_results(self, vector_results, keyword_results, top_k):
        """Combine vector and keyword search results."""
        # Create a mapping of chunk_id to chunk
        all_chunks = {}
        
        # Process vector results
        for chunk in vector_results:
            chunk_id = chunk["id"]
            if chunk_id not in all_chunks:
                all_chunks[chunk_id] = chunk.copy()
                all_chunks[chunk_id]["vector_score"] = chunk["similarity"]
                all_chunks[chunk_id]["keyword_score"] = 0
            else:
                all_chunks[chunk_id]["vector_score"] = chunk["similarity"]
        
        # Process keyword results
        for chunk in keyword_results:
            chunk_id = chunk["id"]
            if chunk_id not in all_chunks:
                all_chunks[chunk_id] = chunk.copy()
                all_chunks[chunk_id]["keyword_score"] = chunk["similarity"]
                all_chunks[chunk_id]["vector_score"] = 0
            else:
                all_chunks[chunk_id]["keyword_score"] = chunk["similarity"]
        
        # Calculate combined scores
        for chunk_id, chunk in all_chunks.items():
            combined_score = (
                self.vector_weight * chunk.get("vector_score", 0) +
                self.keyword_weight * chunk.get("keyword_score", 0)
            )
            chunk["similarity"] = combined_score
            chunk["score_components"] = {
                "vector": chunk.get("vector_score", 0),
                "keyword": chunk.get("keyword_score", 0)
            }
        
        # Convert to list and sort by combined score
        combined_results = list(all_chunks.values())
        combined_results.sort(key=lambda x: x["similarity"], reverse=True)
        
        # Return top_k results
        return combined_results[:top_k]
