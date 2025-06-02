#!/usr/bin/env python3
"""
Deep diagnostic for context retrieval issues.
This investigates why hybrid search is returning empty results.
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.session import get_db_session
from database.db import Database
from services.enhanced_rag_service import KeywordSearchStrategy, create_hybrid_rag_service
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def deep_diagnosis():
    """Deep diagnosis of context retrieval issues."""
    
    print("🔍 DEEP RAG CONTEXT RETRIEVAL DIAGNOSIS")
    print("=" * 60)
    
    # Setup
    db_session = get_db_session()
    db = Database(db_session)
    
    # Get test org and data
    org_result = db_session.execute(text("""
        SELECT org_id, COUNT(*) as chunk_count
        FROM content_chunks 
        WHERE text IS NOT NULL AND LENGTH(text) > 20
        GROUP BY org_id
        ORDER BY chunk_count DESC
        LIMIT 1
    """))
    
    org_row = org_result.fetchone()
    if not org_row:
        print("❌ No valid chunks found!")
        return
        
    test_org_id = org_row.org_id
    print(f"📋 Using org: {test_org_id} ({org_row.chunk_count} chunks)")
    
    # Step 1: Test direct database query
    print("\n1. Testing direct database query...")
    try:
        direct_query = text("""
            SELECT 
                cc.text,
                c.domain,
                c.title,
                cc.id as chunk_id,
                c.id as content_id
            FROM content_chunks cc
            JOIN contents c ON cc.content_id = c.id
            JOIN crawls cr ON c.crawl_id = cr.id
            WHERE cr.org_id = :org_id
                AND cc.text IS NOT NULL
                AND LENGTH(cc.text) > 20
            LIMIT 5
        """)
        
        result = db_session.execute(direct_query, {"org_id": test_org_id})
        rows = result.fetchall()
        
        print(f"✅ Direct query returned {len(rows)} rows")
        for i, row in enumerate(rows[:2]):
            print(f"   Row {i+1}: {row.text[:100]}...")
            print(f"           Domain: {row.domain}, Title: {row.title}")
            
    except Exception as e:
        print(f"❌ Direct query failed: {e}")
        return
    
    # Step 2: Test keyword search strategy directly
    print("\n2. Testing keyword search strategy...")
    try:
        keyword_strategy = KeywordSearchStrategy(db_session)
        
        # Test with simple query first
        test_queries = ["machine", "learning", "the"]
        
        for query in test_queries:
            print(f"   Testing query: '{query}'")
            
            # Test the actual SQL query
            keyword_query = text("""
                SELECT 
                    cc.text as content,
                    c.domain,
                    c.id as content_id,
                    c.title,
                    cc.id as chunk_id
                FROM content_chunks cc
                JOIN contents c ON cc.content_id = c.id
                JOIN crawls cr ON c.crawl_id = cr.id
                WHERE cr.org_id = :org_id
                    AND cc.text IS NOT NULL
                LIMIT 5
            """)
            
            result = db_session.execute(keyword_query, {
                "org_id": test_org_id
            })
            rows = result.fetchall()
            print(f"      Basic query returned: {len(rows)} rows")
            
            # Test with full-text search
            if len(rows) > 0:
                fts_query = text("""
                    SELECT 
                        cc.text as content,
                        c.domain,
                        c.id as content_id,
                        c.title,
                        cc.id as chunk_id,
                        ts_rank(to_tsvector('english', cc.text), plainto_tsquery('english', :search_terms)) as rank
                    FROM content_chunks cc
                    JOIN contents c ON cc.content_id = c.id
                    JOIN crawls cr ON c.crawl_id = cr.id
                    WHERE cr.org_id = :org_id
                        AND to_tsvector('english', cc.text) @@ plainto_tsquery('english', :search_terms)
                    ORDER BY rank DESC
                    LIMIT 5
                """)
                
                try:
                    fts_result = db_session.execute(fts_query, {
                        "org_id": test_org_id,
                        "search_terms": query
                    })
                    fts_rows = fts_result.fetchall()
                    print(f"      Full-text search returned: {len(fts_rows)} rows")
                    
                    if len(fts_rows) > 0:
                        print(f"      ✅ Full-text search working for '{query}'")
                        break
                    else:
                        print(f"      ⚠️ Full-text search found nothing for '{query}'")
                        
                except Exception as fts_error:
                    print(f"      ❌ Full-text search failed: {fts_error}")
            
    except Exception as e:
        print(f"❌ Keyword strategy test failed: {e}")
        return
    
    # Step 3: Test search strategy method
    print("\n3. Testing search strategy method...")
    try:
        keyword_strategy = KeywordSearchStrategy(db_session)
        
        for query in ["machine learning", "programming", "technology"]:
            print(f"   Testing strategy with: '{query}'")
            
            results = await keyword_strategy.search(
                query=query,
                limit=5,
                org_id=test_org_id
            )
            
            print(f"      Strategy returned: {len(results)} results")
            if len(results) > 0:
                print(f"      ✅ Strategy working for '{query}'")
                for i, result in enumerate(results[:2]):
                    print(f"        Result {i+1}: {result.content[:80]}...")
                break
            else:
                print(f"      ⚠️ Strategy returned empty for '{query}'")
                
    except Exception as e:
        print(f"❌ Strategy method test failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 4: Test hybrid service
    print("\n4. Testing hybrid service...")
    try:
        hybrid_service = create_hybrid_rag_service(db, vector_service=None)
        
        test_result = await hybrid_service.retrieve_and_rank(
            query="technology programming",
            strategy="keyword",  # Use keyword only
            top_k=5,
            org_id=test_org_id
        )
        
        print(f"✅ Hybrid service returned: {len(test_result['results'])} results")
        print(f"📊 Stats: {test_result['retrieval_stats']}")
        
    except Exception as e:
        print(f"❌ Hybrid service test failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 5: Check for FTS index
    print("\n5. Checking full-text search index...")
    try:
        index_query = text("""
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE tablename = 'content_chunks'
            AND indexname LIKE '%fts%'
        """)
        
        result = db_session.execute(index_query)
        indexes = result.fetchall()
        
        if indexes:
            print(f"✅ Found FTS indexes: {[idx.indexname for idx in indexes]}")
        else:
            print("⚠️ No full-text search indexes found")
            print("   This could slow down keyword search but shouldn't break it")
            
    except Exception as e:
        print(f"❌ Index check failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 DEEP DIAGNOSIS COMPLETE")
    print("=" * 60)
    
    db_session.close()

if __name__ == "__main__":
    asyncio.run(deep_diagnosis())
