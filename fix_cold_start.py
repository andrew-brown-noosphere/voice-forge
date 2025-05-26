#!/usr/bin/env python3
"""
Fix Cold Start Issues in RAG System
Add better timeout handling and connection warming
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

def create_warmup_endpoint():
    """Create a backend warmup script"""
    warmup_code = '''
# Add this to your backend/api/main.py

@app.get("/warmup")
async def warmup_system():
    """Warmup endpoint to initialize all systems"""
    try:
        from database.session import get_db_session
        from database.db import Database
        from processor.rag import RAGSystem
        from processor.ai_content_generator import AIContentGenerator
        
        # Test database connection
        session = get_db_session()
        db = Database(session)
        
        # Initialize RAG system (loads embedding model)
        rag_system = RAGSystem(db)
        rag_system.get_embedding_model()  # Force load
        
        # Initialize AI generator (tests OpenAI connection)
        ai_gen = AIContentGenerator()
        
        # Test chunk retrieval
        test_chunks = rag_system.retrieve_relevant_chunks("test", top_k=1)
        
        session.close()
        
        return {
            "status": "warmed_up",
            "systems": {
                "database": "ready",
                "rag": "ready", 
                "ai_generator": "ready",
                "chunks_available": len(test_chunks) > 0
            }
        }
        
    except Exception as e:
        return {
            "status": "warmup_failed",
            "error": str(e)
        }
'''
    
    print("🔥 Backend Warmup Endpoint Code:")
    print(warmup_code)

def test_cold_start_issue():
    """Test the cold start issue"""
    print("🧪 Testing Cold Start Issue")
    print("=" * 28)
    
    try:
        from database.session import get_db_session
        from database.db import Database
        from processor.rag import RAGSystem
        import time
        
        print("🔍 First request (cold start)...")
        start_time = time.time()
        
        session = get_db_session()
        db = Database(session)
        rag_system = RAGSystem(db)
        
        # This might be slow the first time
        response1 = rag_system.process_and_generate(
            query="code signing",
            platform="twitter",
            tone="professional"
        )
        
        first_time = time.time() - start_time
        first_success = "Sorry, I couldn't find" not in response1['text']
        
        print(f"   Time: {first_time:.2f}s")
        print(f"   Success: {'✅' if first_success else '❌'}")
        print(f"   Response: {response1['text'][:50]}...")
        
        print("\n🔍 Second request (warm)...")
        start_time = time.time()
        
        response2 = rag_system.process_and_generate(
            query="code signing",
            platform="twitter", 
            tone="professional"
        )
        
        second_time = time.time() - start_time
        second_success = "Sorry, I couldn't find" not in response2['text']
        
        print(f"   Time: {second_time:.2f}s")
        print(f"   Success: {'✅' if second_success else '❌'}")
        print(f"   Response: {response2['text'][:50]}...")
        
        session.close()
        
        print(f"\n📊 Analysis:")
        print(f"   Speed improvement: {first_time/second_time:.1f}x faster")
        print(f"   Cold start issue: {'✅ Confirmed' if not first_success and second_success else '❌ Not detected'}")
        
        if first_time > 10:
            print("⚠️  First request very slow - likely timeout issue")
        
        return first_time, second_time, first_success, second_success
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return None, None, False, False

def suggest_fixes():
    """Suggest fixes for cold start issues"""
    print("\n🔧 Cold Start Fixes")
    print("=" * 18)
    
    print("1️⃣ **Increase Frontend Timeout** (Quick fix):")
    print("   Edit: frontend/src/services/api.js")
    print("   Add: timeout: 30000 // 30 seconds")
    print("   In axios.create() config")
    
    print("\n2️⃣ **Backend Connection Pooling:**")
    print("   Keep database connections warm")
    print("   Pre-load embedding models on startup")
    
    print("\n3️⃣ **Add Warmup Endpoint:**")
    print("   Call /warmup when backend starts")
    print("   Initialize all systems proactively")
    
    print("\n4️⃣ **Frontend Loading State:**")
    print("   Show 'Initializing AI...' on first request")
    print("   Better user experience during cold start")

def create_timeout_fix():
    """Create frontend timeout fix"""
    print("\n📝 Frontend Timeout Fix")
    print("=" * 23)
    
    timeout_fix = '''
// In frontend/src/services/api.js
// Update the axios instance creation:

const api = axios.create({
  baseURL: API_URL,
  timeout: 30000, // 30 seconds for AI generation
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add request interceptor for AI endpoints
api.interceptors.request.use((config) => {
  // Increase timeout for AI generation endpoints
  if (config.url?.includes('/rag/generate')) {
    config.timeout = 45000; // 45 seconds for AI generation
  }
  return config;
})
'''
    
    print(timeout_fix)

def main():
    print("🚀 VoiceForge Cold Start Fix")
    print("=" * 28)
    
    # Test the cold start issue
    test_cold_start_issue()
    
    # Show fix options
    suggest_fixes()
    
    # Show specific fixes
    create_timeout_fix()
    create_warmup_endpoint()
    
    print(f"\n🎯 Recommended Quick Fix:")
    print(f"   1. Update frontend timeout (see code above)")
    print(f"   2. Add better loading message")
    print(f"   3. Consider warmup endpoint for production")
    
    print(f"\n✨ This will eliminate the first-request failure!")

if __name__ == "__main__":
    main()
