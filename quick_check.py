#!/usr/bin/env python3
"""
Quick RAG Diagnostic - Check what's in the database
"""

import os
import sys

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

def quick_check():
    """Quick check of what's in the database"""
    print("🔍 Quick RAG Database Check")
    print("=" * 30)
    
    try:
        from database.session import get_db_session
        from database.models import Content, ContentChunk
        
        session = get_db_session()
        
        # Basic counts
        content_count = session.query(Content).count()
        chunk_count = session.query(ContentChunk).count()
        
        print(f"📊 Database Status:")
        print(f"   Content items: {content_count}")
        print(f"   Content chunks: {chunk_count}")
        
        if content_count == 0:
            print("\n❌ NO CONTENT - You need to crawl first!")
            session.close()
            return False
        
        # Show sample content
        print(f"\n📄 Sample Content:")
        contents = session.query(Content).limit(3).all()
        for i, content in enumerate(contents, 1):
            title = content.title[:50] if content.title else 'No title'
            text_preview = content.text[:100] if content.text else 'No text'
            print(f"   {i}. {title}")
            print(f"      Text: {text_preview}...")
            print(f"      Domain: {content.domain}")
            print()
        
        if chunk_count == 0:
            print("❌ NO CHUNKS - Content needs processing!")
            print("🔧 Run: python process_simple.py")
        else:
            print(f"✅ Found {chunk_count} chunks")
            
            # Check embeddings
            chunks_with_embeddings = session.query(ContentChunk).filter(
                ContentChunk.embedding.isnot(None)
            ).count()
            
            print(f"   Chunks with embeddings: {chunks_with_embeddings}")
            
            if chunks_with_embeddings == 0:
                print("❌ NO EMBEDDINGS - Chunks need embedding generation!")
                print("🔧 Run: python process_simple.py")
        
        session.close()
        return chunk_count > 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    quick_check()
