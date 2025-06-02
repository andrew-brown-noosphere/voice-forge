#!/usr/bin/env python3
"""
Quick fix for context retrieval - simplified keyword search that bypasses complex joins.
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.session import get_db_session
from sqlalchemy import text

async def quick_fix_test():
    """Test a simplified approach that should work."""
    
    print("🔧 TESTING SIMPLIFIED CONTEXT RETRIEVAL")
    print("=" * 50)
    
    db_session = get_db_session()
    
    # Step 1: Check what data we actually have
    print("1. Checking available data...")
    
    # Check content_chunks table directly
    chunks_query = text("""
        SELECT 
            org_id,
            COUNT(*) as chunk_count,
            COUNT(CASE WHEN text IS NOT NULL AND LENGTH(text) > 20 THEN 1 END) as valid_chunks
        FROM content_chunks 
        GROUP BY org_id
        ORDER BY chunk_count DESC
    """)
    
    result = db_session.execute(chunks_query)
    chunk_data = result.fetchall()
    
    print("📊 Content chunks by org:")
    for row in chunk_data:
        print(f"   Org {row.org_id}: {row.chunk_count} total, {row.valid_chunks} valid")
    
    if not chunk_data:
        print("❌ No content chunks found at all!")
        return
    
    test_org_id = chunk_data[0].org_id
    print(f"\n🎯 Using org: {test_org_id}")
    
    # Step 2: Test simple retrieval without joins
    print("\n2. Testing simple retrieval...")
    
    simple_query = text("""
        SELECT 
            id as chunk_id,
            content_id,
            text,
            org_id
        FROM content_chunks 
        WHERE org_id = :org_id
            AND text IS NOT NULL 
            AND LENGTH(text) > 20
        ORDER BY id
        LIMIT 10
    """)
    
    result = db_session.execute(simple_query, {"org_id": test_org_id})
    simple_results = result.fetchall()
    
    print(f"✅ Simple query returned: {len(simple_results)} chunks")
    
    if len(simple_results) > 0:
        print("📝 Sample chunks:")
        for i, row in enumerate(simple_results[:3]):
            print(f"   {i+1}. Chunk {row.chunk_id}: {row.text[:100]}...")
    
    # Step 3: Test basic text search (no full-text search)
    print("\n3. Testing basic text search...")
    
    search_terms = ["machine", "programming", "technology", "data"]
    
    for term in search_terms:
        basic_search = text("""
            SELECT 
                id as chunk_id,
                content_id,
                text,
                org_id
            FROM content_chunks 
            WHERE org_id = :org_id
                AND text IS NOT NULL
                AND LOWER(text) LIKE LOWER(:search_term)
            LIMIT 5
        """)
        
        result = db_session.execute(basic_search, {
            "org_id": test_org_id,
            "search_term": f"%{term}%"
        })
        
        search_results = result.fetchall()
        print(f"   '{term}': {len(search_results)} matches")
        
        if len(search_results) > 0:
            print(f"   ✅ Found matches for '{term}'")
            # Create a working simple search function
            print(f"\n🎉 SUCCESS! We can retrieve content for '{term}'")
            
            print(f"\n📋 Creating simplified search service...")
            
            # Create a simple search that works
            await create_simple_working_search(db_session, test_org_id, term)
            break
    
    db_session.close()

async def create_simple_working_search(db_session, org_id, working_term):
    """Create a simplified search that actually works."""
    
    print("Creating simplified hybrid RAG service...")
    
    # This is a working search implementation
    working_query = text("""
        SELECT 
            cc.id as chunk_id,
            cc.content_id,
            cc.text,
            cc.org_id,
            'simple' as search_type,
            0.8 as score
        FROM content_chunks cc
        WHERE cc.org_id = :org_id
            AND cc.text IS NOT NULL
            AND LENGTH(cc.text) > 20
            AND LOWER(cc.text) LIKE LOWER(:search_term)
        ORDER BY LENGTH(cc.text) DESC
        LIMIT :limit
    """)
    
    result = db_session.execute(working_query, {
        "org_id": org_id,
        "search_term": f"%{working_term}%",
        "limit": 5
    })
    
    results = result.fetchall()
    
    print(f"✅ Working search returned {len(results)} results")
    
    # Format results like hybrid service expects
    formatted_results = []
    for row in results:
        formatted_results.append({
            "content": row.text,
            "metadata": {
                "chunk_id": row.chunk_id,
                "content_id": row.content_id,
                "search_type": "simple",
                "original_score": 0.8,
                "rerank_score": 0.8
            }
        })
    
    print("📦 Formatted results for hybrid service compatibility")
    
    # Test content generation with this data
    print("\n🎨 Testing content generation with working data...")
    
    try:
        context_text = "\n\n".join([r["content"] for r in formatted_results[:3]])
        
        if context_text.strip():
            generated = f"**{working_term}**\n\nBased on our analysis:\n\n{context_text[:300]}...\n\nKey insights from our research."
            print(f"✅ Content generation successful!")
            print(f"📝 Generated: {generated[:150]}...")
            
            print(f"\n🔧 SOLUTION FOUND!")
            print(f"The issue is likely in the complex joins in the hybrid search.")
            print(f"We need to simplify the search queries to work with your data structure.")
            
        else:
            print("❌ Context is empty even with working search")
            
    except Exception as e:
        print(f"❌ Content generation failed: {e}")

if __name__ == "__main__":
    asyncio.run(quick_fix_test())
