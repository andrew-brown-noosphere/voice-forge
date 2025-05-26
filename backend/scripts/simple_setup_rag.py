#!/usr/bin/env python3
"""
Simple RAG Setup
Simplified version that processes content step by step with better error handling
"""

import os
import sys

# Load environment variables from .env file FIRST
def load_env_file():
    backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(backend_path, '.env')
    
    print(f"📄 Loading environment from: {env_path}")
    
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        
        # Verify key variables are loaded
        key_vars = ['OPENAI_API_KEY', 'DATABASE_URL']
        print("✅ Environment variables loaded:")
        for var in key_vars:
            if os.environ.get(var):
                print(f"   ✅ {var}: SET")
            else:
                print(f"   ❌ {var}: NOT SET")
        return True
    else:
        print(f"❌ .env file not found at {env_path}")
        return False

# Load environment first
load_env_file()

# Now add to Python path and import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_simple_setup():
    """Run a simplified setup process"""
    print("\n🚀 Starting Simple RAG Setup")
    print("=" * 40)
    
    try:
        # Step 1: Test database connection
        print("\n1️⃣ Testing database connection...")
        from database.session import get_db_session
        from sqlalchemy import text
        session = get_db_session()
        session.execute(text("SELECT 1"))
        print("   ✅ Database connection working")
        
        # Step 2: Check current content
        print("\n2️⃣ Checking current content...")
        from database.models import Content, ContentChunk
        content_count = session.query(Content).count()
        chunk_count = session.query(ContentChunk).count()
        print(f"   📄 Content items: {content_count}")
        print(f"   🧩 Content chunks: {chunk_count}")
        
        # Step 3: Add sample content if needed
        if content_count < 5:
            print("\n3️⃣ Adding sample content...")
            from scripts.add_sample_content import add_sample_content
            added = add_sample_content()
            print(f"   ✅ Added {added} content items")
        else:
            print("\n3️⃣ Sufficient content already exists")
        
        # Step 4: Process content for embeddings
        print("\n4️⃣ Processing content for embeddings...")
        
        # Initialize RAG system (needed for both embedding generation and testing)
        from processor.rag import RAGSystem
        from database.db import Database
        db = Database(session)
        rag_system = RAGSystem(db)
        
        # Check current embedding status
        chunks_with_embeddings = session.query(ContentChunk).filter(
            ContentChunk.embedding.isnot(None)
        ).count()
        
        print(f"   📊 Current embeddings: {chunks_with_embeddings}")
        
        if chunks_with_embeddings == 0:
            print("   🔄 Generating embeddings...")
            
            embedding_model = rag_system.get_embedding_model()
            
            # Get chunks without embeddings
            chunks_to_process = session.query(ContentChunk).filter(
                ContentChunk.embedding.is_(None)
            ).limit(10).all()  # Process first 10 chunks
            
            processed = 0
            for chunk in chunks_to_process:
                try:
                    embedding = embedding_model.encode(chunk.content)
                    chunk.embedding = embedding.tolist()
                    processed += 1
                    print(f"   📝 Processed chunk {processed}/{len(chunks_to_process)}")
                except Exception as e:
                    print(f"   ❌ Error processing chunk {chunk.id}: {e}")
            
            session.commit()
            print(f"   ✅ Generated {processed} embeddings")
        else:
            print("   ✅ Embeddings already exist")
        
        # Step 5: Test basic RAG functionality
        print("\n5️⃣ Testing RAG functionality...")
        try:
            results = rag_system.retrieve_relevant_chunks("test query", top_k=3)
            print(f"   ✅ Vector search working: found {len(results)} results")
        except Exception as e:
            print(f"   ❌ Vector search failed: {e}")
        
        # Step 6: Test LLM integration
        print("\n6️⃣ Testing LLM integration...")
        try:
            from processor.llm.llm_service import LLMService
            llm_service = LLMService()
            
            # Test with simple generation
            response = llm_service.generate(
                prompt_type="content_generation",
                params={
                    "query": "What is AI?",
                    "platform": "website", 
                    "tone": "informative",
                    "context_chunks": []
                }
            )
            response_text = response.get('content', response.get('text', str(response)))
            print(f"   ✅ LLM working: generated {len(response_text)} characters")
        except Exception as e:
            print(f"   ❌ LLM test failed: {e}")
        
        session.close()
        
        print(f"\n🎉 Simple RAG setup complete!")
        print(f"\n📋 Next steps:")
        print(f"   • Test full pipeline: python scripts/test_full_rag_pipeline.py")
        print(f"   • Add more content with your crawler")
        print(f"   • Check status: python scripts/quick_status.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_simple_setup()
    sys.exit(0 if success else 1)
