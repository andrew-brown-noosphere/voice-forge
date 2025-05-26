#!/usr/bin/env python3
"""
Minimal RAG Test
Very simple test to verify basic functionality works
"""

import os
import sys

# Load environment variables from .env file
def load_env_file():
    backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(backend_path, '.env')
    
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        return True
    return False

# Load environment
load_env_file()
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_basic_functionality():
    """Test very basic functionality"""
    print("🧪 Minimal RAG Functionality Test")
    print("=" * 35)
    
    try:
        # Test 1: Database connection
        print("\n1️⃣ Database connection...")
        from database.session import get_db_session
        from sqlalchemy import text
        session = get_db_session()
        result = session.execute(text("SELECT 1")).fetchone()
        print(f"   ✅ Connected: {result[0]}")
        
        # Test 2: Check tables exist
        print("\n2️⃣ Database tables...")
        from database.models import Content, ContentChunk
        content_count = session.query(Content).count()
        chunk_count = session.query(ContentChunk).count()
        print(f"   📄 Content: {content_count} items")
        print(f"   🧩 Chunks: {chunk_count} items")
        
        # Test 3: Check embeddings
        print("\n3️⃣ Embeddings...")
        chunks_with_embeddings = session.query(ContentChunk).filter(
            ContentChunk.embedding.isnot(None)
        ).count()
        print(f"   🎯 With embeddings: {chunks_with_embeddings}/{chunk_count}")
        
        # Test 4: Basic RAG system
        print("\n4️⃣ RAG system...")
        from processor.rag import RAGSystem
        from database.db import Database
        db = Database(session)
        rag = RAGSystem(db)
        print(f"   ✅ RAG system initialized")
        
        # Test 5: Embedding model
        print("\n5️⃣ Embedding model...")
        embedding_model = rag.get_embedding_model()
        test_embedding = embedding_model.encode("test text")
        print(f"   ✅ Embedding model: {len(test_embedding)} dimensions")
        
        session.close()
        
        print(f"\n🎉 Basic functionality test: PASSED")
        
        # Provide next steps
        if chunks_with_embeddings == 0:
            print(f"\n📋 Next step: Generate embeddings")
            print(f"   python scripts/simple_setup_rag.py")
        else:
            print(f"\n📋 Next step: Test full pipeline")
            print(f"   python scripts/test_full_rag_pipeline.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_basic_functionality()
    sys.exit(0 if success else 1)
