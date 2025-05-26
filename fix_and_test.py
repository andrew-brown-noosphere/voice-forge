#!/usr/bin/env python3
"""
Fix Database Transaction Issues and Test RAG
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

def fix_and_test():
    """Fix database issues and test RAG"""
    print("🔧 Fixing Database Transaction Issues")
    print("=" * 40)
    
    try:
        from database.session import get_db_session
        from database.models import Content, ContentChunk
        from database.db import Database
        
        # Use a fresh session
        session = get_db_session()
        
        try:
            # Check what we have
            content_count = session.query(Content).count()
            chunk_count = session.query(ContentChunk).count()
            
            print(f"📊 Database Status:")
            print(f"   Content items: {content_count}")
            print(f"   Content chunks: {chunk_count}")
            
            if content_count == 0:
                print("\n❌ NO CONTENT FOUND!")
                print("🔧 You need to crawl some content first")
                return False
            
            if chunk_count == 0:
                print("\n❌ NO CHUNKS FOUND!")
                print("🔧 Content needs to be processed for RAG")
                return False
            
            # Test direct chunk search without domain filter
            print(f"\n🔍 Testing chunk search...")
            
            # Simple test - find chunks containing "sign"
            chunks = session.query(ContentChunk).filter(
                ContentChunk.text.ilike('%sign%')
            ).limit(5).all()
            
            print(f"   Found {len(chunks)} chunks containing 'sign'")
            
            if chunks:
                print("\n📦 Sample chunks:")
                for i, chunk in enumerate(chunks[:3], 1):
                    print(f"   {i}. {chunk.text[:100]}...")
                    print(f"      Content ID: {chunk.content_id}")
                    print(f"      Has embedding: {'✅' if chunk.embedding else '❌'}")
                
                # Test with the RAG system using a fresh session
                session.close()
                
                # Create new session for RAG test
                print(f"\n🧪 Testing RAG system...")
                session2 = get_db_session()
                db = Database(session2)
                
                # Simple test - search for chunks containing signing
                search_results = db.search_chunks_by_text(
                    query="signing",
                    top_k=3
                )
                
                print(f"   RAG search found: {len(search_results)} chunks")
                
                if search_results:
                    print("✅ RAG system is working!")
                    for i, result in enumerate(search_results[:2], 1):
                        print(f"   {i}. Score: {result.get('similarity', 0):.3f}")
                        print(f"      Text: {result.get('text', '')[:80]}...")
                else:
                    print("❌ RAG search returned no results")
                
                session2.close()
                return len(search_results) > 0
            else:
                print("❌ No chunks found even with simple search")
                return False
                
        except Exception as e:
            print(f"❌ Database error: {e}")
            session.rollback()  # Rollback failed transaction
            return False
        finally:
            session.close()
            
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        return False

def test_simple_generation():
    """Test content generation with simpler approach"""
    print("\n🤖 Testing Simple Content Generation")
    print("=" * 35)
    
    try:
        from database.session import get_db_session
        from database.db import Database
        from processor.rag import RAGSystem
        
        session = get_db_session()
        db = Database(session)
        rag_system = RAGSystem(db)
        
        # Test without domain filter (which seems to cause issues)
        print("🔍 Testing content generation...")
        
        response = rag_system.process_and_generate(
            query="signing software",  # Simpler query
            platform="website",
            tone="informative",
            domain=None,  # No domain filter
            content_type=None,
            top_k=3
        )
        
        print(f"📝 Generated content:")
        print(f"   Length: {len(response['text'])} chars")
        print(f"   Content: {response['text'][:200]}...")
        print(f"   Sources: {len(response.get('source_chunks', []))}")
        
        session.close()
        
        if "Sorry, I couldn't find relevant information" in response['text']:
            print("❌ Still getting 'no information' error")
            return False
        else:
            print("✅ Content generation working!")
            return True
            
    except Exception as e:
        print(f"❌ Generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🚀 VoiceForge RAG Database Fix & Test")
    print("=" * 38)
    
    # Step 1: Fix and test database
    db_ok = fix_and_test()
    
    if not db_ok:
        print("\n🔧 Database issues found. Try:")
        print("   1. Restart PostgreSQL: brew services restart postgresql")
        print("   2. Process content: python process_simple.py")
        print("   3. Check backend logs for errors")
        return False
    
    # Step 2: Test content generation
    gen_ok = test_simple_generation()
    
    if gen_ok:
        print("\n🎉 RAG system is working!")
        print("🔗 Try the frontend: http://localhost:5173")
    else:
        print("\n🔧 Content generation issues. Try:")
        print("   1. Restart backend server")
        print("   2. Use simpler queries")
        print("   3. Check OpenAI API key")
    
    return gen_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
