#!/usr/bin/env python3
"""
Diagnose RAG Content Issues
Shows exactly what content and chunks are in your database
"""

import os
import sys
from datetime import datetime

# Load environment
def load_env_file():
    backend_path = '/Users/andrewbrown/Sites/noosphere/github/voice-forge/backend'
    env_path = os.path.join(backend_path, '.env')
    
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env_file()

# Add backend to path
backend_path = '/Users/andrewbrown/Sites/noosphere/github/voice-forge/backend'
sys.path.append(backend_path)

def diagnose_rag_content():
    """Diagnose what content exists and why RAG might not be working"""
    print("🔍 VoiceForge RAG Content Diagnosis")
    print("=" * 40)
    
    try:
        from database.session import get_db_session
        from database.models import Content, ContentChunk
        from sqlalchemy import func
        
        session = get_db_session()
        
        # Basic counts
        content_count = session.query(Content).count()
        chunk_count = session.query(ContentChunk).count()
        chunks_with_embeddings = session.query(ContentChunk).filter(
            ContentChunk.embedding.isnot(None)
        ).count()
        
        print(f"📊 Database Overview:")
        print(f"   Content items: {content_count}")
        print(f"   Content chunks: {chunk_count}")
        print(f"   Chunks with embeddings: {chunks_with_embeddings}")
        
        if content_count == 0:
            print("\n❌ NO CONTENT FOUND!")
            print("🔧 You need to crawl some websites first:")
            print("   • Use the frontend to start a crawl")
            print("   • Or run: python setup_sample_content.py")
            session.close()
            return False
        
        # Show content details
        print(f"\n📄 Content Details:")
        contents = session.query(Content).limit(10).all()
        for i, content in enumerate(contents, 1):
            content_length = len(content.text or '')
            print(f"   {i}. {content.title[:50] if content.title else 'No title'}...")
            print(f"      URL: {content.url}")
            print(f"      Domain: {content.domain}")
            print(f"      Type: {content.content_type}")
            print(f"      Content length: {content_length:,} chars")
            
            # Check if this content has chunks
            content_chunks = session.query(ContentChunk).filter(
                ContentChunk.content_id == content.id
            ).count()
            print(f"      Chunks: {content_chunks}")
            
            if content_length < 100:
                print("      ⚠️  Content very short - may not generate good chunks")
            
            print()
        
        if chunk_count == 0:
            print("❌ NO CHUNKS FOUND!")
            print("🔧 Your content needs to be processed for RAG:")
            print("   python process_crawled_content.py")
            session.close()
            return False
        
        if chunks_with_embeddings == 0:
            print("❌ NO EMBEDDINGS FOUND!")
            print("🔧 Your chunks need embeddings:")
            print("   python process_crawled_content.py")
            session.close()
            return False
        
        # Show sample chunks
        print(f"📦 Sample Chunks:")
        chunks = session.query(ContentChunk).limit(5).all()
        for i, chunk in enumerate(chunks, 1):
            print(f"   {i}. Chunk ID: {chunk.id[:8]}...")
            print(f"      Content ID: {chunk.content_id[:8]}...")
            print(f"      Text: {chunk.text[:100]}...")
            print(f"      Has embedding: {'✅' if chunk.embedding else '❌'}")
            print()
        
        # Test a simple query
        print("🧪 Testing RAG Query...")
        try:
            from database.db import Database
            from processor.rag import RAGSystem
            
            db = Database(session)
            rag_system = RAGSystem(db)
            
            # Try to retrieve chunks for "office macros"
            test_query = "office macros"
            print(f"   Query: '{test_query}'")
            
            chunks = rag_system.retrieve_relevant_chunks(test_query, top_k=3)
            print(f"   Retrieved chunks: {len(chunks)}")
            
            if chunks:
                print("   ✅ RAG retrieval working!")
                for i, chunk in enumerate(chunks, 1):
                    print(f"      {i}. Score: {chunk.get('similarity', 0):.3f}")
                    print(f"         Text: {chunk.get('text', '')[:80]}...")
            else:
                print("   ❌ No chunks retrieved")
                print("   💡 Try a different query or check if your content covers this topic")
            
        except Exception as e:
            print(f"   ❌ RAG test failed: {e}")
        
        # Show domains and content types
        print(f"\n📊 Content Analysis:")
        domains = session.query(Content.domain, func.count(Content.id)).group_by(Content.domain).all()
        print("   Domains:")
        for domain, count in domains:
            print(f"      {domain}: {count} items")
        
        content_types = session.query(Content.content_type, func.count(Content.id)).group_by(Content.content_type).all()
        print("   Content Types:")
        for content_type, count in content_types:
            print(f"      {content_type or 'None'}: {count} items")
        
        session.close()
        
        print(f"\n✅ Diagnosis complete!")
        if chunks_with_embeddings > 0:
            print("🎉 Your RAG system should be working!")
            print("💡 Try queries related to your crawled content topics")
        
        return True
        
    except Exception as e:
        print(f"❌ Diagnosis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    success = diagnose_rag_content()
    
    if not success:
        print("\n🔧 Quick Fixes:")
        print("   1. Add content: python setup_sample_content.py")
        print("   2. Process content: python process_crawled_content.py")
        print("   3. Check status: cd backend && python scripts/quick_status.py")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
