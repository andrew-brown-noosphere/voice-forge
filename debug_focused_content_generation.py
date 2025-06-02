#!/usr/bin/env python3
"""
Focused Content Generation Debug - Test the exact API endpoint that's failing.
"""

import sys
import os
import requests
import json
from datetime import datetime

# Add backend to path
backend_path = '/Users/andrewbrown/Sites/noosphere/github/voice-forge/backend'
sys.path.append(backend_path)

# Load environment variables
env_path = os.path.join(backend_path, '.env')
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

def test_database_content():
    """Check what's actually in the database."""
    print("🗄️ DATABASE CONTENT CHECK")
    print("=" * 30)
    
    try:
        from database.session import get_db_session
        
        session = get_db_session()
        
        # Raw SQL to check what we have (with proper text() wrapping)
        from sqlalchemy import text
        
        result = session.execute(text("SELECT COUNT(*) FROM content_chunks"))
        chunk_count = result.fetchone()[0]
        
        result = session.execute(text("SELECT COUNT(*) FROM contents"))
        content_count = result.fetchone()[0]
        
        print(f"Content items: {content_count}")
        print(f"Content chunks: {chunk_count}")
        
        if chunk_count > 0:
            # Get a sample chunk
            result = session.execute(text("SELECT text, org_id FROM content_chunks LIMIT 1"))
            sample = result.fetchone()
            if sample:
                print(f"Sample chunk: {sample.text[:100]}...")
                print(f"Sample org_id: {sample.org_id}")
        
        session.close()
        return chunk_count > 0
        
    except Exception as e:
        print(f"Database error: {e}")
        return False

def test_rag_service_directly():
    """Test the RAG service directly without the API layer."""
    print("\n🔍 RAG SERVICE DIRECT TEST")
    print("=" * 30)
    
    try:
        from database.session import get_db_session
        from services.simplified_rag_service import create_simplified_rag_service
        import asyncio
        
        async def run_rag_test():
            session = get_db_session()
            rag_service = create_simplified_rag_service(session)
            
            result = await rag_service.retrieve_and_rank(
                query="test content generation",
                top_k=3
            )
            
            print(f"RAG Results: {len(result['results'])} found")
            print(f"Search successful: {result['retrieval_stats']['search_successful']}")
            
            if result['results']:
                first = result['results'][0]
                print(f"First result: {first['content'][:100]}...")
                return True
            else:
                print("No results returned")
                return False
        
        return asyncio.run(run_rag_test())
        
    except Exception as e:
        print(f"RAG service error: {e}")
        return False

def test_api_endpoint():
    """Test the actual API endpoint that's failing."""
    print("\n🌐 API ENDPOINT TEST")
    print("=" * 30)
    
    # Test without authentication first
    url = "http://localhost:8000/rag/generate"
    
    payload = {
        "query": "test content generation",
        "platform": "twitter",
        "tone": "professional",
        "top_k": 3
    }
    
    print(f"Testing: POST {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 401:
            print("❌ Authentication required")
            
            # Get token from user
            token = input("\n🔑 Paste your JWT token to test with auth: ").strip()
            
            if token:
                headers = {"Authorization": f"Bearer {token}"}
                print("Retrying with authentication...")
                
                response = requests.post(url, json=payload, headers=headers, timeout=30)
                print(f"Auth Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print("✅ Success!")
                    print(f"Response keys: {list(data.keys())}")
                    
                    if 'text' in data:
                        print(f"Generated text length: {len(data['text'])}")
                        print(f"Text preview: {data['text'][:100]}...")
                    else:
                        print("❌ No 'text' field in response")
                        
                    return True
                else:
                    print(f"❌ Auth request failed: {response.text}")
                    return False
            else:
                print("Skipping authenticated test")
                return False
        
        elif response.status_code == 200:
            data = response.json()
            print("✅ Success (no auth required)!")
            print(f"Response keys: {list(data.keys())}")
            
            if 'text' in data:
                print(f"Generated text length: {len(data['text'])}")
                print(f"Text preview: {data['text'][:100]}...")
            else:
                print("❌ No 'text' field in response")
                
            return True
        
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - is the backend running?")
        return False
    except Exception as e:
        print(f"❌ Request error: {e}")
        return False

def test_backend_health():
    """Test if the backend is running."""
    print("🏥 BACKEND HEALTH CHECK")
    print("=" * 30)
    
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        print(f"Backend status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Backend message: {data.get('status', 'No status')}")
            return True
        else:
            print(f"Backend returned: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Backend not responding: {e}")
        return False

def main():
    """Run focused debugging."""
    print("🎯 FOCUSED CONTENT GENERATION DEBUG")
    print("=" * 50)
    print(f"Time: {datetime.now().isoformat()}")
    print("")
    
    # Step 1: Check if backend is running
    backend_ok = test_backend_health()
    if not backend_ok:
        print("\n❌ ISSUE: Backend is not running!")
        print("💡 START BACKEND: cd backend && python -m uvicorn api.main:app --reload")
        return
    
    # Step 2: Check database content
    has_data = test_database_content()
    if not has_data:
        print("\n❌ ISSUE: No content chunks in database!")
        print("💡 SOLUTION:")
        print("   1. Run a crawl: python test_crawl_api.py")
        print("   2. Process content: python process_simple.py")
        return
    
    # Step 3: Test RAG service directly
    rag_ok = test_rag_service_directly()
    if not rag_ok:
        print("\n❌ ISSUE: RAG service not working!")
        print("💡 SOLUTION: Check RAG service implementation")
        return
    
    # Step 4: Test API endpoint
    api_ok = test_api_endpoint()
    if not api_ok:
        print("\n❌ ISSUE: API endpoint failing!")
        print("💡 SOLUTION: Check API authentication and error handling")
        return
    
    print("\n✅ ALL TESTS PASSED!")
    print("🎯 Content generation should be working.")
    print("\nIf frontend still shows errors:")
    print("1. Check browser console for specific error messages")
    print("2. Verify JWT token is valid")
    print("3. Check network tab for actual API responses")
    print("4. Try refreshing the page")

if __name__ == "__main__":
    main()
