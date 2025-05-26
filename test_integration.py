#!/usr/bin/env python3
"""
VoiceForge RAG Integration Test
Tests the complete frontend-backend integration
"""

import os
import sys
import time
import requests
import json
from datetime import datetime

def load_env_file():
    """Load environment variables from .env file"""
    backend_path = '/Users/andrewbrown/Sites/noosphere/github/voice-forge/backend'
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

def test_backend_health():
    """Test if backend is running and healthy"""
    try:
        response = requests.get('http://localhost:8000/', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'VoiceForge API' in data.get('status', ''):
                print("✅ Backend is running and healthy")
                return True
    except requests.exceptions.RequestException:
        pass
    
    print("❌ Backend is not running or not healthy")
    return False

def test_frontend_health():
    """Test if frontend is running"""
    try:
        response = requests.get('http://localhost:5173/', timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is running")
            return True
    except requests.exceptions.RequestException:
        pass
    
    print("❌ Frontend is not running")
    return False

def test_rag_endpoints():
    """Test RAG-specific API endpoints"""
    base_url = 'http://localhost:8000'
    
    tests = [
        {
            'name': 'List Domains',
            'method': 'GET',
            'endpoint': '/domains',
            'expected_status': 200
        },
        {
            'name': 'Search Chunks',
            'method': 'POST',
            'endpoint': '/rag/chunks/search',
            'data': {
                'query': 'artificial intelligence',
                'top_k': 3
            },
            'expected_status': 200
        },
        {
            'name': 'Generate Content',
            'method': 'POST',
            'endpoint': '/rag/generate',
            'data': {
                'query': 'What is AI?',
                'platform': 'website',
                'tone': 'informative',
                'top_k': 3
            },
            'expected_status': 200
        }
    ]
    
    results = []
    
    for test in tests:
        try:
            if test['method'] == 'GET':
                response = requests.get(f"{base_url}{test['endpoint']}", timeout=10)
            else:
                response = requests.post(
                    f"{base_url}{test['endpoint']}", 
                    json=test['data'],
                    timeout=10
                )
            
            if response.status_code == test['expected_status']:
                print(f"✅ {test['name']}: SUCCESS")
                results.append(True)
                
                # Show sample response for generate content
                if 'generate' in test['endpoint']:
                    data = response.json()
                    text = data.get('text', '')
                    sources = data.get('source_chunks', [])
                    print(f"   📝 Generated: {text[:100]}...")
                    print(f"   📚 Sources: {len(sources)}")
                    
            else:
                print(f"❌ {test['name']}: FAILED (Status: {response.status_code})")
                print(f"   Response: {response.text[:200]}...")
                results.append(False)
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {test['name']}: FAILED (Error: {str(e)})")
            results.append(False)
    
    return all(results)

def test_database_content():
    """Test if there's content in the database for RAG"""
    # Add backend path to Python path
    backend_path = '/Users/andrewbrown/Sites/noosphere/github/voice-forge/backend'
    sys.path.append(backend_path)
    
    try:
        from database.session import get_db_session
        from database.models import Content, ContentChunk
        
        session = get_db_session()
        
        content_count = session.query(Content).count()
        chunk_count = session.query(ContentChunk).count()
        
        chunks_with_embeddings = session.query(ContentChunk).filter(
            ContentChunk.embedding.isnot(None)
        ).count()
        
        session.close()
        
        print(f"📊 Database Status:")
        print(f"   Content items: {content_count}")
        print(f"   Content chunks: {chunk_count}")
        print(f"   Chunks with embeddings: {chunks_with_embeddings}")
        
        if content_count > 0 and chunk_count > 0:
            print("✅ Database has content for RAG")
            return True
        else:
            print("⚠️  Database needs content for RAG")
            return False
            
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False

def main():
    """Run integration tests"""
    print("🔍 VoiceForge RAG Integration Test")
    print("=" * 40)
    print(f"📅 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load environment
    load_env_file()
    
    # Test components
    tests = [
        ("Backend Health", test_backend_health),
        ("Frontend Health", test_frontend_health),
        ("Database Content", test_database_content),
        ("RAG API Endpoints", test_rag_endpoints)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}...")
        result = test_func()
        results.append(result)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n📋 Integration Test Summary:")
    print(f"   Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! Your VoiceForge RAG integration is working!")
        print("\n🔗 URLs:")
        print("   Frontend: http://localhost:5173")
        print("   Backend: http://localhost:8000")
        print("   API Docs: http://localhost:8000/docs")
        print("\n📝 Try the Content Generator:")
        print("   1. Open the frontend URL")
        print("   2. Navigate to 'Content Generator'")
        print("   3. Enter a query and generate content")
        
    else:
        print("\n⚠️  Some tests failed. Check the issues above.")
        print("\n🔧 Troubleshooting:")
        print("   • Make sure both servers are running")
        print("   • Check database has content")
        print("   • Verify API endpoints are working")
        print("   • Run: python scripts/quick_status.py")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
