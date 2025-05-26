#!/usr/bin/env python3
"""
Test End-to-End RAG
Test the complete RAG pipeline with a simple query
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

def test_rag_pipeline():
    """Test the complete RAG pipeline"""
    print("🚀 End-to-End RAG Pipeline Test")
    print("=" * 35)
    
    try:
        # Initialize database and RAG system
        from database.session import get_db_session
        from database.db import Database
        from processor.rag import RAGSystem
        from sqlalchemy import text
        
        session = get_db_session()
        db = Database(session)
        rag_system = RAGSystem(db)
        
        print("\n✅ RAG system initialized")
        
        # Test query
        test_query = "What is artificial intelligence?"
        print(f"\n🔍 Testing query: '{test_query}'")
        
        # Test retrieval
        print("\n1️⃣ Testing chunk retrieval...")
        chunks = rag_system.retrieve_relevant_chunks(test_query, top_k=3)
        print(f"   📊 Found {len(chunks)} relevant chunks")
        
        if chunks:
            for i, chunk in enumerate(chunks):
                print(f"   📄 Chunk {i+1}: {chunk['text'][:100]}... (score: {chunk.get('similarity', 0):.3f})")
        
        # Test full generation
        print("\n2️⃣ Testing content generation...")
        response = rag_system.process_and_generate(
            query=test_query,
            platform="website",
            tone="informative"
        )
        
        print(f"   📝 Generated response ({len(response['text'])} characters):")
        print(f"   📖 Preview: {response['text'][:200]}...")
        
        # Show sources
        sources = response.get('source_chunks', [])
        print(f"\n3️⃣ Sources used: {len(sources)}")
        for i, source in enumerate(sources):
            print(f"   📚 Source {i+1}: {source.get('text', 'N/A')[:80]}...")
        
        session.close()
        
        print(f"\n🎉 RAG Pipeline Test: SUCCESS!")
        print(f"   Your VoiceForge RAG system is working end-to-end!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ RAG Pipeline Test: FAILED")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_rag_pipeline()
    
    if success:
        print(f"\n🎯 Next Steps:")
        print(f"   • Your RAG system is ready to use!")
        print(f"   • Add more content with your crawler")
        print(f"   • Integrate with your VoiceForge API")
        print(f"   • Run comprehensive tests: python scripts/test_full_rag_pipeline.py")
    else:
        print(f"\n🔧 Troubleshooting:")
        print(f"   • Check if you have content: python scripts/quick_status.py")
        print(f"   • Add content: python scripts/add_sample_content.py")
        print(f"   • Process content: python scripts/simple_setup_rag.py")
    
    sys.exit(0 if success else 1)
