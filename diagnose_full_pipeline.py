#!/usr/bin/env python3
"""
Complete pipeline diagnostic to identify what's working and what needs fixing.
"""

import os
import sys
import requests
import json
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

def check_database():
    """Check database contents"""
    print("📊 STEP 1: Database Content Check")
    print("-" * 40)
    
    try:
        from database.session import get_db_session
        from database.models import Content, ContentChunk, Crawl
        
        session = get_db_session()
        
        # Basic counts
        crawl_count = session.query(Crawl).count()
        content_count = session.query(Content).count()
        chunk_count = session.query(ContentChunk).count()
        
        print(f"   Crawls: {crawl_count}")
        print(f"   Content items: {content_count}")
        print(f"   Content chunks: {chunk_count}")
        
        if content_count > 0:
            print("\n   📄 Sample Content:")
            contents = session.query(Content).limit(2).all()
            for content in contents:
                print(f"      • {content.title or 'No title'}")
                print(f"        URL: {content.url}")
                print(f"        Domain: {content.domain}")
                print(f"        Text length: {len(content.text or '')} chars")
                print(f"        Org ID: {content.org_id}")
                print()
        
        if chunk_count > 0:
            chunks_with_embeddings = session.query(ContentChunk).filter(
                ContentChunk.embedding.isnot(None)
            ).count()
            print(f"   Chunks with embeddings: {chunks_with_embeddings}")
        
        session.close()
        
        return {
            'crawls': crawl_count,
            'content': content_count,
            'chunks': chunk_count,
            'embeddings': chunks_with_embeddings if chunk_count > 0 else 0
        }
        
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return None

def test_api_endpoints():
    """Test key API endpoints"""
    print("\n🌐 STEP 2: API Endpoints Test")
    print("-" * 40)
    
    base_url = "http://localhost:8000"
    
    # Test basic health
    try:
        response = requests.get(f"{base_url}/")
        print(f"   Root endpoint: ✅ {response.status_code}")
    except Exception as e:
        print(f"   Root endpoint: ❌ {e}")
        return False
    
    # Get JWT token for authenticated requests
    token = input("   🔑 Paste your JWT token (or press Enter to skip auth tests): ").strip()
    
    if not token:
        print("   Skipping authenticated endpoint tests")
        return True
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Test domains endpoint
    try:
        response = requests.get(f"{base_url}/domains", headers=headers)
        if response.status_code == 200:
            domains = response.json()
            print(f"   Domains endpoint: ✅ Found {len(domains)} domains")
            if domains:
                for domain in domains[:3]:
                    print(f"      • {domain}")
        else:
            print(f"   Domains endpoint: ❌ {response.status_code}")
    except Exception as e:
        print(f"   Domains endpoint: ❌ {e}")
    
    # Test content search
    try:
        search_data = {
            "query": "example",
            "limit": 5
        }
        response = requests.post(f"{base_url}/content/search", 
                               headers=headers, json=search_data)
        if response.status_code == 200:
            results = response.json()
            print(f"   Content search: ✅ Found {len(results)} results")
        else:
            print(f"   Content search: ❌ {response.status_code}")
    except Exception as e:
        print(f"   Content search: ❌ {e}")
    
    # Test RAG generation
    try:
        gen_data = {
            "query": "Tell me about this website",
            "platform": "twitter",
            "tone": "professional"
        }
        response = requests.post(f"{base_url}/rag/generate", 
                               headers=headers, json=gen_data)
        if response.status_code == 200:
            result = response.json()
            print(f"   RAG generation: ✅ Generated content")
            print(f"      Preview: {result.get('content', 'No content')[:100]}...")
        else:
            print(f"   RAG generation: ❌ {response.status_code}")
            if response.text:
                error_detail = response.json().get('detail', response.text)
                print(f"      Error: {error_detail}")
    except Exception as e:
        print(f"   RAG generation: ❌ {e}")
    
    return True

def check_content_processing():
    """Check if content is properly processed for RAG"""
    print("\n🔧 STEP 3: Content Processing Check")
    print("-" * 40)
    
    try:
        from database.session import get_db_session
        from database.models import Content, ContentChunk
        
        session = get_db_session()
        
        # Find content without chunks
        content_without_chunks = session.query(Content).outerjoin(ContentChunk).filter(
            ContentChunk.id.is_(None)
        ).count()
        
        print(f"   Content items without chunks: {content_without_chunks}")
        
        if content_without_chunks > 0:
            print("   ⚠️ Some content needs processing into chunks")
            print("   💡 Solution: Run content processing script")
        
        # Check for chunks without embeddings
        chunks_without_embeddings = session.query(ContentChunk).filter(
            ContentChunk.embedding.is_(None)
        ).count()
        
        print(f"   Chunks without embeddings: {chunks_without_embeddings}")
        
        if chunks_without_embeddings > 0:
            print("   ⚠️ Some chunks need embedding generation")
            print("   💡 Solution: Run embedding generation script")
        
        session.close()
        
        return {
            'unprocessed_content': content_without_chunks,
            'chunks_no_embeddings': chunks_without_embeddings
        }
        
    except Exception as e:
        print(f"   ❌ Processing check error: {e}")
        return None

def check_openai_config():
    """Check OpenAI configuration"""
    print("\n🤖 STEP 4: AI Configuration Check")
    print("-" * 40)
    
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print(f"   OpenAI API Key: ✅ Configured ({api_key[:8]}...)")
        
        # Test OpenAI connection
        try:
            import openai
            openai.api_key = api_key
            
            # Simple test call
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            print("   OpenAI connection: ✅ Working")
            
        except Exception as e:
            print(f"   OpenAI connection: ❌ {e}")
    else:
        print("   OpenAI API Key: ❌ Not configured")
    
    return bool(api_key)

def main():
    """Run complete diagnostic"""
    print("🔍 VoiceForge Complete Pipeline Diagnostic")
    print("=" * 50)
    print(f"Time: {datetime.now().isoformat()}")
    print()
    
    # Step 1: Database
    db_stats = check_database()
    
    # Step 2: API endpoints
    api_ok = test_api_endpoints()
    
    # Step 3: Content processing
    processing_stats = check_content_processing()
    
    # Step 4: AI configuration
    ai_ok = check_openai_config()
    
    # Summary and recommendations
    print("\n🎯 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    if db_stats:
        if db_stats['content'] == 0:
            print("❌ ISSUE: No content in database")
            print("   💡 FIX: Run a crawl to get some content")
            print("   📝 Command: python test_crawl_api.py")
        elif db_stats['chunks'] == 0:
            print("❌ ISSUE: Content not processed into chunks")
            print("   💡 FIX: Process content for RAG")
            print("   📝 Command: python process_simple.py")
        elif db_stats['embeddings'] == 0:
            print("❌ ISSUE: No embeddings generated")
            print("   💡 FIX: Generate embeddings for chunks")
            print("   📝 Command: python process_simple.py")
        else:
            print("✅ DATABASE: Content and embeddings ready")
    
    if not ai_ok:
        print("❌ ISSUE: OpenAI not configured")
        print("   💡 FIX: Set OPENAI_API_KEY in .env file")
    
    print("\n🚀 NEXT STEPS:")
    if db_stats and db_stats['content'] > 0:
        print("1. ✅ Crawling is working")
        print("2. Try crawling a real website:")
        print("   python test_crawl_api.py")
        print("   # Use a domain like https://python.org")
        print("3. Process content if needed:")
        print("   python process_simple.py")
        print("4. Test content generation in the frontend")
    else:
        print("1. Start with a test crawl:")
        print("   python test_crawl_api.py")
        print("2. Check results with:")
        print("   python quick_check.py")

if __name__ == "__main__":
    main()
