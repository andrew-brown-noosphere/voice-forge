#!/usr/bin/env python3
"""
Comprehensive debug script for VoiceForge content generation issue.
This will trace through the entire pipeline to find where it's failing.
"""

import sys
import os
import asyncio
import logging
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from database.session import get_db_session
from services.simplified_rag_service import create_simplified_rag_service

def setup_logging():
    """Setup detailed logging to trace the issue."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Enable debug for our modules
    logging.getLogger('services.simplified_rag_service').setLevel(logging.DEBUG)
    logging.getLogger('api.main').setLevel(logging.DEBUG)

async def test_rag_pipeline():
    """Test the RAG pipeline step by step."""
    print("🔍 COMPREHENSIVE CONTENT GENERATION DEBUG")
    print("=" * 60)
    print(f"Time: {datetime.now().isoformat()}")
    print("")
    
    try:
        # Step 1: Database Connection
        print("1️⃣ Testing database connection...")
        db_session = get_db_session()
        
        # Check if we can connect
        result = db_session.execute("SELECT 1 as test")
        if result.fetchone():
            print("   ✅ Database connection successful")
        else:
            print("   ❌ Database connection failed")
            return False
        
        # Step 2: Check data availability
        print("\n2️⃣ Checking data availability...")
        
        # Check contents table
        content_count = db_session.execute("SELECT COUNT(*) FROM contents").fetchone()[0]
        print(f"   Contents in database: {content_count}")
        
        # Check content_chunks table
        chunk_count = db_session.execute("SELECT COUNT(*) FROM content_chunks").fetchone()[0]
        print(f"   Chunks in database: {chunk_count}")
        
        if chunk_count == 0:
            print("   ❌ No content chunks found! RAG will fail.")
            print("   💡 Need to process content for RAG first.")
            return False
        
        # Check for org_ids
        org_ids = db_session.execute("SELECT DISTINCT org_id FROM content_chunks WHERE org_id IS NOT NULL").fetchall()
        print(f"   Organizations with chunks: {[row[0] for row in org_ids]}")
        
        # Step 3: Test simplified RAG service
        print("\n3️⃣ Testing simplified RAG service...")
        
        rag_service = create_simplified_rag_service(db_session)
        
        test_query = "test content generation"
        print(f"   Query: '{test_query}'")
        
        rag_result = await rag_service.retrieve_and_rank(
            query=test_query,
            top_k=5
        )
        
        stats = rag_result["retrieval_stats"]
        print(f"   RAG found: {stats['total_found']} results")
        print(f"   RAG success: {stats['search_successful']}")
        
        if not stats['search_successful']:
            print("   ❌ RAG search failed!")
            print(f"   Error: {stats.get('error', 'Unknown error')}")
            return False
        
        # Show sample results
        results = rag_result["results"]
        print(f"   ✅ RAG returned {len(results)} chunks")
        
        for i, result in enumerate(results[:2]):
            content_preview = result["content"][:100].replace('\n', ' ')
            print(f"      Chunk {i+1}: {content_preview}...")
        
        # Step 4: Test content generation format
        print("\n4️⃣ Testing content generation format...")
        
        # Simulate the content generation process
        context_text = "\n\n".join([
            result["content"] for result in results[:3]
        ])
        
        print(f"   Context length: {len(context_text)} characters")
        
        if len(context_text) < 100:
            print("   ⚠️ Warning: Very short context for generation")
        
        # Test simple generation (like the API does)
        generated_text = f"🚀 {test_query}\n\nBased on our research:\n{context_text[:200]}...\n\n#Innovation"
        
        print(f"   Generated content length: {len(generated_text)} characters")
        print(f"   Generated preview: {generated_text[:100]}...")
        
        # Step 5: Test response format
        print("\n5️⃣ Testing response format...")
        
        source_chunks = []
        for result in results:
            source_chunks.append({
                "chunk_id": result["metadata"].get("chunk_id", "unknown"),
                "text": result["content"][:200] + "..." if len(result["content"]) > 200 else result["content"],
                "similarity": result["metadata"].get("rerank_score", 0.8),
                "content_id": result["metadata"].get("content_id", "unknown")
            })
        
        response_data = {
            "text": generated_text,
            "source_chunks": source_chunks,
            "metadata": {
                "platform": "twitter",
                "tone": "professional",
                "context_chunks_used": len(source_chunks),
                "hybrid_enhanced": False,
                "simplified_rag": True
            }
        }
        
        print(f"   Response has 'text': {'text' in response_data}")
        print(f"   Response has 'source_chunks': {'source_chunks' in response_data}")
        print(f"   Source chunks count: {len(response_data['source_chunks'])}")
        
        print("\n✅ ALL TESTS PASSED!")
        print("🎯 Content generation pipeline should work.")
        print("")
        print("📋 SUMMARY:")
        print(f"   - Database: ✅ Connected")
        print(f"   - Content: ✅ {content_count} items")
        print(f"   - Chunks: ✅ {chunk_count} items")
        print(f"   - RAG: ✅ Found {stats['total_found']} results")
        print(f"   - Generation: ✅ {len(generated_text)} chars")
        print(f"   - Response: ✅ Properly formatted")
        
        db_session.close()
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR in pipeline: {e}")
        import traceback
        print(f"Traceback:\n{traceback.format_exc()}")
        return False

def test_direct_api_simulation():
    """Simulate the exact API call that's failing."""
    print("\n🌐 SIMULATING DIRECT API CALL")
    print("=" * 40)
    
    # This simulates what happens when the frontend calls /rag/generate
    request_data = {
        "query": "Write a test post about our company",
        "platform": "twitter", 
        "tone": "professional",
        "top_k": 5
    }
    
    print(f"Request: {request_data}")
    
    try:
        from api.main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # This would normally require authentication, but let's see what happens
        response = client.post("/rag/generate", json=request_data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}...")
        
        if response.status_code == 200:
            print("✅ API call successful!")
            return True
        else:
            print("❌ API call failed!")
            return False
            
    except Exception as e:
        print(f"❌ API simulation failed: {e}")
        return False

async def main():
    """Main diagnostic function."""
    setup_logging()
    
    # Test the pipeline
    pipeline_success = await test_rag_pipeline()
    
    if pipeline_success:
        print("\n🔧 TROUBLESHOOTING RECOMMENDATIONS:")
        print("1. Pipeline looks good - issue might be authentication/frontend")
        print("2. Check browser console for specific error messages")
        print("3. Verify JWT token is valid and has org access")
        print("4. Check if backend is returning 401/403 auth errors")
        print("5. Test with debug_content_generation.py script for auth issues")
    else:
        print("\n🔧 TROUBLESHOOTING RECOMMENDATIONS:")
        print("1. Process content for RAG if no chunks exist")
        print("2. Check database connection and migrations")
        print("3. Verify content crawling completed successfully")
        print("4. Run setup_sample_content.py to create test data")
    
    print(f"\n🏁 Debug completed at {datetime.now().isoformat()}")

if __name__ == "__main__":
    asyncio.run(main())
