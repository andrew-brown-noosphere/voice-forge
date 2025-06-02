#!/usr/bin/env python3
"""
Quick database content checker with proper SQL syntax.
"""

import sys
import os

# Add backend to path
backend_path = '/Users/andrewbrown/Sites/noosphere/github/voice-forge/backend'
sys.path.append(backend_path)

# Load environment
env_path = os.path.join(backend_path, '.env')
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

def check_database():
    """Check database contents with proper SQL syntax."""
    print("🗄️ DATABASE CONTENT CHECK")
    print("=" * 30)
    
    try:
        from database.session import get_db_session
        from database.models import Content, ContentChunk, Crawl
        from sqlalchemy import text
        
        session = get_db_session()
        
        # Check table counts using proper SQLAlchemy syntax
        print("📊 Table Counts:")
        
        # Count crawls
        crawl_count = session.query(Crawl).count()
        print(f"   Crawls: {crawl_count}")
        
        # Count content
        content_count = session.query(Content).count()
        print(f"   Content items: {content_count}")
        
        # Count chunks
        chunk_count = session.query(ContentChunk).count()
        print(f"   Content chunks: {chunk_count}")
        
        if crawl_count == 0:
            print("\n❌ NO CRAWLS - Need to crawl websites first!")
            print("💡 SOLUTION:")
            print("   1. Use the frontend to start a crawl")
            print("   2. Or run: python test_crawl_api.py")
            return False
        
        if content_count == 0:
            print("\n❌ NO CONTENT - Crawls exist but no content extracted!")
            print("💡 Check crawl status and errors")
            return False
        
        if chunk_count == 0:
            print("\n❌ NO CHUNKS - Content exists but not processed for RAG!")
            print("💡 SOLUTION:")
            print("   Run: python process_simple.py")
            return False
        
        # Show sample data if available
        if content_count > 0:
            print(f"\n📄 Sample Content:")
            contents = session.query(Content).limit(2).all()
            for i, content in enumerate(contents, 1):
                print(f"   {i}. {content.title or 'No title'}")
                print(f"      Domain: {content.domain}")
                print(f"      URL: {content.url}")
                print(f"      Text length: {len(content.text or '')} chars")
                print(f"      Org ID: {content.org_id}")
                print()
        
        if chunk_count > 0:
            # Check embeddings
            chunks_with_embeddings = session.query(ContentChunk).filter(
                ContentChunk.embedding.isnot(None)
            ).count()
            
            print(f"📦 Chunk Details:")
            print(f"   Total chunks: {chunk_count}")
            print(f"   Chunks with embeddings: {chunks_with_embeddings}")
            
            if chunks_with_embeddings == 0:
                print("   ⚠️ No embeddings - RAG search may not work well")
            else:
                print("   ✅ Embeddings available - RAG should work!")
        
        session.close()
        return chunk_count > 0
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def recommend_next_steps():
    """Recommend what to do next."""
    print("\n🎯 RECOMMENDED NEXT STEPS:")
    print("=" * 30)
    
    print("1. 🌐 **If no crawls exist:**")
    print("   - Open frontend: http://localhost:5173")
    print("   - Go to 'Crawl List' and start a new crawl")
    print("   - Try crawling: https://python.org or https://fastapi.tiangolo.com")
    print()
    
    print("2. 📊 **If content exists but no chunks:**")
    print("   - Run: cd backend && python process_simple.py")
    print("   - This will create chunks for RAG")
    print()
    
    print("3. 🚀 **Test content generation:**")
    print("   - Once chunks exist, try the frontend content generator")
    print("   - Should now work with the fix we applied!")
    print()
    
    print("4. 🔧 **If still having issues:**")
    print("   - Check backend logs for errors")
    print("   - Verify OpenAI API key in .env file")
    print("   - Try: python debug_content_generation.py")

if __name__ == "__main__":
    print("🔍 VOICEFORGE DATABASE STATUS CHECK")
    print("=" * 40)
    
    has_content = check_database()
    recommend_next_steps()
    
    if has_content:
        print("\n✅ Ready for content generation!")
    else:
        print("\n⚠️ Need to set up content first")
