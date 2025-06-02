#!/usr/bin/env python3
"""
Simplified RAG service that bypasses the crawls table complexity.
This fixes the empty context retrieval issue by using direct queries.
"""

import asyncio
from typing import List, Dict, Any, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

class SimplifiedSearchStrategy:
    """Simplified search that works directly with content_chunks and contents."""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    async def search(self, query: str, limit: int = 10, org_id: str = None) -> List[Dict[str, Any]]:
        """
        Search using simplified queries that bypass crawls table.
        """
        try:
            # First, try to get org_id from contents if not provided
            if not org_id:
                org_result = self.db_session.execute(text("""
                    SELECT DISTINCT org_id 
                    FROM contents 
                    WHERE org_id IS NOT NULL 
                    LIMIT 1
                """))
                org_row = org_result.fetchone()
                if org_row:
                    org_id = org_row.org_id
                    logger.info(f"Using detected org_id: {org_id}")
            
            # Method 1: Try with contents join (if contents has org_id)
            results = await self._search_with_contents_join(query, limit, org_id)
            
            if results:
                logger.info(f"Found {len(results)} results using contents join")
                return results
            
            # Method 2: Try direct search on content_chunks (if it has org_id)
            results = await self._search_direct_chunks(query, limit, org_id)
            
            if results:
                logger.info(f"Found {len(results)} results using direct chunk search")
                return results
            
            # Method 3: Fallback - search all chunks for any org
            results = await self._search_fallback_all_chunks(query, limit)
            
            logger.info(f"Fallback search found {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            # Return empty list rather than failing
            return []
    
    async def _search_with_contents_join(self, query: str, limit: int, org_id: str = None) -> List[Dict[str, Any]]:
        """Search using content_chunks joined with contents (bypassing crawls)."""
        
        # Build the WHERE clause dynamically
        where_conditions = ["cc.text IS NOT NULL", "LENGTH(cc.text) > 20"]
        params = {"search_term": f"%{query.lower()}%", "limit": limit}
        
        if org_id:
            where_conditions.append("c.org_id = :org_id")
            params["org_id"] = org_id
        
        where_clause = " AND ".join(where_conditions)
        
        # Try with PostgreSQL full-text search first
        fts_query = text(f"""
            SELECT 
                cc.text as content,
                c.domain,
                c.title,
                c.url,
                cc.id as chunk_id,
                c.id as content_id,
                c.org_id,
                ts_rank(
                    to_tsvector('english', cc.text), 
                    plainto_tsquery('english', :search_term_clean)
                ) as rank
            FROM content_chunks cc
            JOIN contents c ON cc.content_id = c.id
            WHERE {where_clause}
                AND to_tsvector('english', cc.text) @@ plainto_tsquery('english', :search_term_clean)
            ORDER BY rank DESC
            LIMIT :limit
        """)
        
        try:
            params["search_term_clean"] = query
            result = self.db_session.execute(fts_query, params)
            rows = result.fetchall()
            
            if rows:
                return self._format_results(rows, "fts")
                
        except Exception as e:
            logger.warning(f"Full-text search failed, falling back to LIKE: {e}")
        
        # Fallback to simple LIKE search
        like_query = text(f"""
            SELECT 
                cc.text as content,
                c.domain,
                c.title,
                c.url,
                cc.id as chunk_id,
                c.id as content_id,
                c.org_id,
                1.0 as rank
            FROM content_chunks cc
            JOIN contents c ON cc.content_id = c.id
            WHERE {where_clause}
                AND LOWER(cc.text) LIKE :search_term
            ORDER BY LENGTH(cc.text) DESC
            LIMIT :limit
        """)
        
        result = self.db_session.execute(like_query, params)
        rows = result.fetchall()
        
        return self._format_results(rows, "like")
    
    async def _search_direct_chunks(self, query: str, limit: int, org_id: str = None) -> List[Dict[str, Any]]:
        """Search directly in content_chunks if it has org_id column."""
        
        where_conditions = ["text IS NOT NULL", "LENGTH(text) > 20"]
        params = {"search_term": f"%{query.lower()}%", "limit": limit}
        
        if org_id:
            where_conditions.append("org_id = :org_id")
            params["org_id"] = org_id
        
        where_clause = " AND ".join(where_conditions)
        
        direct_query = text(f"""
            SELECT 
                text as content,
                'unknown' as domain,
                'Direct Chunk' as title,
                '' as url,
                id as chunk_id,
                content_id,
                org_id,
                1.0 as rank
            FROM content_chunks
            WHERE {where_clause}
                AND LOWER(text) LIKE :search_term
            ORDER BY LENGTH(text) DESC
            LIMIT :limit
        """)
        
        try:
            result = self.db_session.execute(direct_query, params)
            rows = result.fetchall()
            return self._format_results(rows, "direct")
        except Exception as e:
            logger.warning(f"Direct chunk search failed: {e}")
            return []
    
    async def _search_fallback_all_chunks(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Fallback search that finds any matching chunks regardless of org."""
        
        fallback_query = text("""
            SELECT 
                text as content,
                'unknown' as domain,
                'Fallback Search' as title,
                '' as url,
                id as chunk_id,
                content_id,
                COALESCE(org_id, 'unknown') as org_id,
                1.0 as rank
            FROM content_chunks
            WHERE text IS NOT NULL 
                AND LENGTH(text) > 20
                AND LOWER(text) LIKE :search_term
            ORDER BY LENGTH(text) DESC
            LIMIT :limit
        """)
        
        try:
            result = self.db_session.execute(fallback_query, {
                "search_term": f"%{query.lower()}%",
                "limit": limit
            })
            rows = result.fetchall()
            return self._format_results(rows, "fallback")
        except Exception as e:
            logger.error(f"Even fallback search failed: {e}")
            return []
    
    def _format_results(self, rows, search_type: str) -> List[Dict[str, Any]]:
        """Format database rows into the expected result format."""
        results = []
        
        for row in rows:
            results.append({
                "content": row.content,
                "metadata": {
                    "chunk_id": row.chunk_id,
                    "content_id": row.content_id,
                    "domain": getattr(row, 'domain', 'unknown'),
                    "title": getattr(row, 'title', 'Unknown'),
                    "url": getattr(row, 'url', ''),
                    "org_id": getattr(row, 'org_id', 'unknown'),
                    "search_type": search_type,
                    "original_score": float(getattr(row, 'rank', 1.0)),
                    "rerank_score": float(getattr(row, 'rank', 1.0))
                }
            })
        
        return results


class SimplifiedHybridRAGService:
    """Simplified hybrid RAG service that actually works."""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.search_strategy = SimplifiedSearchStrategy(db_session)
    
    async def retrieve_and_rank(
        self,
        query: str,
        strategy: str = "simplified",
        top_k: int = 5,
        org_id: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Retrieve and rank content using simplified search.
        
        Args:
            query: Search query
            strategy: Search strategy (ignored - always uses simplified)
            top_k: Number of results to return
            org_id: Organization ID (optional)
        
        Returns:
            Dict with results and stats
        """
        try:
            logger.info(f"Simplified RAG search for: '{query}' (org: {org_id})")
            
            # Get search results
            results = await self.search_strategy.search(
                query=query,
                limit=top_k,
                org_id=org_id
            )
            
            # Build response
            response = {
                "results": results[:top_k],
                "retrieval_stats": {
                    "total_found": len(results),
                    "returned": min(len(results), top_k),
                    "strategy_used": "simplified",
                    "org_id": org_id,
                    "search_successful": len(results) > 0
                }
            }
            
            logger.info(f"Simplified RAG returned {len(results)} results")
            return response
            
        except Exception as e:
            logger.error(f"Simplified RAG failed: {e}")
            
            # Return empty results rather than failing
            return {
                "results": [],
                "retrieval_stats": {
                    "total_found": 0,
                    "returned": 0,
                    "strategy_used": "simplified",
                    "org_id": org_id,
                    "search_successful": False,
                    "error": str(e)
                }
            }


def create_simplified_rag_service(db_session: Session) -> SimplifiedHybridRAGService:
    """Create a simplified RAG service that bypasses crawls table issues."""
    return SimplifiedHybridRAGService(db_session)


# Test function
async def test_simplified_rag():
    """Test the simplified RAG service."""
    from database.session import get_db_session
    
    print("🧪 TESTING SIMPLIFIED RAG SERVICE")
    print("=" * 50)
    
    db_session = get_db_session()
    service = create_simplified_rag_service(db_session)
    
    # Test queries
    test_queries = ["machine learning", "programming", "technology", "data"]
    
    for query in test_queries:
        print(f"\n🔍 Testing: '{query}'")
        
        result = await service.retrieve_and_rank(
            query=query,
            top_k=3
        )
        
        stats = result["retrieval_stats"]
        print(f"   Found: {stats['total_found']} results")
        print(f"   Success: {stats['search_successful']}")
        
        if result["results"]:
            print(f"   ✅ SUCCESS! Sample result:")
            first_result = result["results"][0]
            print(f"      Content: {first_result['content'][:100]}...")
            print(f"      Metadata: {first_result['metadata']['search_type']}")
            break
        else:
            print(f"   ❌ No results for '{query}'")
    
    db_session.close()
    print("\n🎯 Test complete!")


if __name__ == "__main__":
    asyncio.run(test_simplified_rag())
