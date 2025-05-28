#!/usr/bin/env python3
"""
Final system test - verify the complete VoiceForge pipeline is working.
"""

import requests
import json
import time
from datetime import datetime

def test_complete_system():
    """Test the complete VoiceForge system end-to-end."""
    
    print("🎯 VoiceForge Complete System Test")
    print("=" * 40)
    print(f"Time: {datetime.now().isoformat()}")
    
    # Get token from user
    token = input("🔑 Paste your JWT token: ").strip()
    
    if not token:
        print("❌ No token provided")
        return False
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    success_count = 0
    total_tests = 5
    
    # Test 1: Authentication
    print("\\n1️⃣ Testing Authentication...")
    try:
        response = requests.get('http://localhost:8000/auth/me', headers=headers)
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ Authentication working")
            print(f"   User: {user_info.get('name', 'Unknown')}")
            print(f"   Org: {user_info.get('org_id', 'None')}")
            success_count += 1
        else:
            print(f"❌ Auth failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Auth error: {e}")
    
    # Test 2: Domains List
    print("\\n2️⃣ Testing Domains List...")
    try:
        response = requests.get('http://localhost:8000/domains', headers=headers)
        if response.status_code == 200:
            domains = response.json()
            print(f"✅ Domains working: {len(domains)} domains found")
            for domain in domains:
                print(f"   • {domain}")
            if len(domains) > 1:  # Should have more than just example.com now
                success_count += 1
            else:
                print("⚠️ Only example.com found - may need more crawls")
        else:
            print(f"❌ Domains failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Domains error: {e}")
    
    # Test 3: Crawl List
    print("\\n3️⃣ Testing Crawl History...")
    try:
        response = requests.get('http://localhost:8000/crawl?limit=5&offset=0', headers=headers)
        if response.status_code == 200:
            crawls = response.json()
            print(f"✅ Crawl history working: {len(crawls)} crawls found")
            for crawl in crawls:
                progress = crawl.get('progress', {})
                print(f"   • {crawl.get('domain', 'Unknown')}: {crawl.get('state', 'Unknown')} - {progress.get('pages_crawled', 0)} pages")
            success_count += 1
        else:
            print(f"❌ Crawl list failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Crawl list error: {e}")
    
    # Test 4: Content Search
    print("\\n4️⃣ Testing Content Search...")
    try:
        search_data = {
            "query": "FastAPI",
            "limit": 3
        }
        response = requests.post('http://localhost:8000/content/search', 
                               headers=headers, json=search_data)
        if response.status_code == 200:
            results = response.json()
            print(f"✅ Content search working: {len(results)} results")
            for result in results[:2]:
                title = result.get('title', 'No title')[:50]
                print(f"   • {title}...")
            success_count += 1
        else:
            print(f"❌ Content search failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Content search error: {e}")
    
    # Test 5: RAG Content Generation
    print("\\n5️⃣ Testing Content Generation...")
    try:
        gen_data = {
            "query": "What is FastAPI and why should I use it?",
            "platform": "twitter",
            "tone": "professional"
        }
        response = requests.post('http://localhost:8000/rag/generate', 
                               headers=headers, json=gen_data)
        if response.status_code == 200:
            result = response.json()
            generated_content = result.get('content', '')
            print(f"✅ Content generation working!")
            print(f"   Generated: {generated_content[:100]}...")
            success_count += 1
        else:
            print(f"❌ Content generation failed: {response.status_code}")
            if response.text:
                try:
                    error_detail = response.json().get('detail', response.text)
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Content generation error: {e}")
    
    # Summary
    print(f"\\n🏆 TEST RESULTS")
    print("=" * 25)
    print(f"Passed: {success_count}/{total_tests} tests")
    
    if success_count == total_tests:
        print("🎉 ALL SYSTEMS OPERATIONAL!")
        print("\\n✅ Your VoiceForge system is fully working:")
        print("   • Authentication ✅")
        print("   • Crawling ✅") 
        print("   • Content indexing ✅")
        print("   • Search ✅")
        print("   • AI content generation ✅")
        print("\\n🚀 Ready for production use!")
        
    elif success_count >= 3:
        print("🟡 MOSTLY WORKING - Minor issues")
        if success_count < 5:
            print("\\n🔧 To fix remaining issues:")
            print("   • Run: python process_simple.py")
            print("   • Check OpenAI API key in .env")
            print("   • Crawl more websites for better content")
        
    else:
        print("🔴 SYSTEM NEEDS ATTENTION")
        print("\\n🔧 Troubleshooting steps:")
        print("   1. Check backend is running: python -m uvicorn api.main:app --reload")
        print("   2. Verify token is fresh (refresh browser)")
        print("   3. Check database connection")
        print("   4. Run diagnostics: python diagnose_full_pipeline.py")
    
    return success_count >= 4

def main():
    """Main test function."""
    success = test_complete_system()
    
    print("\\n" + "=" * 50)
    if success:
        print("🎊 CONGRATULATIONS!")
        print("Your VoiceForge system is ready to use!")
        print("\\n📱 Frontend: http://localhost:5173")
        print("🔗 API: http://localhost:8000")
    else:
        print("⚙️ System needs some adjustments")
        print("Follow the troubleshooting steps above")
    
    return success

if __name__ == "__main__":
    main()
