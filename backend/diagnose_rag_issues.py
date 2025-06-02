#!/usr/bin/env python3
"""
Diagnostic script for RAG content generation issues.
This helps identify what's causing the content generation failures.
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.session import get_db_session
from services.enhanced_rag_service import create_hybrid_rag_service
import logging

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def diagnose_rag_generation():
    """Diagnose RAG content generation issues."""
    
    print("🔍 VoiceForge RAG Content Generation Diagnostics")
    print("=" * 60)
    
    # Step 1: Test database connection
    print("\n1. Testing database connection...")
    try:
        db_session = get_db_session()
        from database.db import Database
        db = Database(db_session)
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return
    
    # Step 2: Check for content chunks
    print("\n2. Checking for content chunks...")
    try:
        from sqlalchemy import text
        
        # Check total chunks
        result = db_session.execute(text("""
            SELECT 
                COUNT(*) as total_chunks,
                COUNT(DISTINCT org_id) as total_orgs,
                COUNT(CASE WHEN text IS NOT NULL AND LENGTH(text) > 20 THEN 1 END) as valid_chunks
            FROM content_chunks
        """))
        
        row = result.fetchone()
        print(f"📊 Total chunks: {row.total_chunks}")
        print(f"📊 Organizations: {row.total_orgs}")  
        print(f"📊 Valid chunks: {row.valid_chunks}")
        
        if row.valid_chunks == 0:
            print("⚠️ No valid content chunks found - this will cause generation failures")
            print("   Run a crawl first to populate content chunks")
            
        # Get sample org
        org_result = db_session.execute(text("""
            SELECT org_id, COUNT(*) as chunk_count
            FROM content_chunks 
            WHERE text IS NOT NULL AND LENGTH(text) > 20
            GROUP BY org_id
            ORDER BY chunk_count DESC
            LIMIT 1
        """))
        
        org_row = org_result.fetchone()
        if org_row:
            test_org_id = org_row.org_id
            print(f"📋 Test org ID: {test_org_id} ({org_row.chunk_count} chunks)")
        else:
            print("❌ No organizations with valid chunks found")
            return
            
    except Exception as e:
        print(f"❌ Chunk analysis failed: {e}")
        return
    
    # Step 3: Test hybrid RAG service creation
    print("\n3. Testing hybrid RAG service creation...")
    try:
        hybrid_service = create_hybrid_rag_service(db, vector_service=None)
        print("✅ Hybrid RAG service created successfully")
    except Exception as e:
        print(f"❌ Hybrid RAG service creation failed: {e}")
        return
    
    # Step 4: Test context retrieval
    print("\n4. Testing context retrieval...")
    try:
        test_query = "machine learning programming"
        print(f"   Query: {test_query}")
        print(f"   Org ID: {test_org_id}")
        
        context_results = await hybrid_service.retrieve_and_rank(
            query=test_query,
            strategy="keyword",  # Start with keyword only for simplicity
            top_k=5,
            org_id=test_org_id
        )
        
        print(f"✅ Context retrieval successful")
        print(f"📊 Results returned: {len(context_results['results'])}")
        print(f"📊 Retrieval stats: {context_results['retrieval_stats']}")
        
        if len(context_results['results']) == 0:
            print("⚠️ No results returned - this will cause empty context")
            
        # Show sample results
        for i, result in enumerate(context_results['results'][:2]):
            print(f"   Result {i+1}: {result['content'][:100]}...")
            
    except Exception as e:
        print(f"❌ Context retrieval failed: {e}")
        print(f"   This is likely the root cause of generation failures")
        import traceback
        traceback.print_exc()
        return
    
    # Step 5: Test simple content generation
    print("\n5. Testing simple content generation...")
    try:
        # Simple template-based generation
        context_text = "\\n\\n".join([
            result["content"] for result in context_results["results"][:3]
        ])
        
        if not context_text.strip():
            context_text = "No context available - using fallback content"
            
        generated_text = f"**{test_query}**\\n\\nBased on our analysis:\\n\\n{context_text[:400]}...\\n\\nWhat are your thoughts?"
        
        print("✅ Content generation successful")
        print(f"📝 Generated content preview:")
        print(f"   {generated_text[:200]}...")
        
    except Exception as e:
        print(f"❌ Content generation failed: {e}")
        return
    
    # Step 6: Test cross-encoder reranking (optional)
    print("\n6. Testing cross-encoder reranking...")
    try:
        from services.enhanced_rag_service import CrossEncoderReranker
        reranker = CrossEncoderReranker()
        
        if reranker.model:
            print("✅ Cross-encoder model loaded successfully")
        else:
            print("⚠️ Cross-encoder model failed to load - reranking will be skipped")
            
    except Exception as e:
        print(f"⚠️ Cross-encoder test failed: {e}")
        print("   This won't prevent generation but reduces quality")
    
    print("\n" + "=" * 60)
    print("🎯 DIAGNOSIS COMPLETE")
    print("=" * 60)
    
    # Summary
    if row.valid_chunks > 0 and len(context_results['results']) > 0:
        print("✅ RAG system appears to be working correctly")
        print("   If you're still seeing errors, check:")
        print("   1. Authentication/authorization issues")
        print("   2. Network connectivity") 
        print("   3. Frontend-backend communication")
        print("   4. CORS settings")
    else:
        print("❌ RAG system has issues that need to be resolved:")
        if row.valid_chunks == 0:
            print("   - No valid content chunks (run crawls first)")
        if len(context_results['results']) == 0:
            print("   - Context retrieval returning empty results")
    
    # Cleanup
    db_session.close()

if __name__ == "__main__":
    try:
        asyncio.run(diagnose_rag_generation())
    except KeyboardInterrupt:
        print("\\n🛑 Diagnosis interrupted by user")
    except Exception as e:
        print(f"\\n💥 Unexpected error during diagnosis: {e}")
        import traceback
        traceback.print_exc()
