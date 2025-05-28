#!/usr/bin/env python3
"""
Test the auth fix and run a new crawl with the updated system.
"""

import requests
import json
import time
from datetime import datetime

def test_auth_fix():
    """Test that the auth system is working with the timezone fix."""
    
    print("🔧 Testing Auth Fix & Crawl System")
    print("=" * 45)
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
    
    # Test 1: Check auth health
    print("\\n1️⃣ Testing Authentication Health...")
    try:
        response = requests.get('http://localhost:8000/auth/me', headers=headers)
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ Auth working! User: {user_info.get('name', 'Unknown')}")
            print(f"   Organization: {user_info.get('org_id', 'None')}")
        else:
            print(f"❌ Auth failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Auth request failed: {e}")
        return False
    
    # Test 2: Check domains endpoint (should work now)
    print("\\n2️⃣ Testing Domains Endpoint...")
    try:
        response = requests.get('http://localhost:8000/domains', headers=headers)
        if response.status_code == 200:
            domains = response.json()
            print(f"✅ Domains endpoint working! Found {len(domains)} domains")
            for domain in domains[:5]:
                print(f"   • {domain}")
        else:
            print(f"❌ Domains failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Domains request failed: {e}")
    
    # Test 3: Start a new crawl with a real website
    print("\\n3️⃣ Testing New Crawl...")
    
    # Choose a good test domain
    test_domain = "https://fastapi.tiangolo.com"
    print(f"🎯 Target: {test_domain}")
    
    crawl_data = {
        "domain": test_domain,
        "config": {
            "max_depth": 2,
            "max_pages": 5,
            "delay": 1.0,
            "timeout": 30,
            "user_agent": "Mozilla/5.0 (compatible; VoiceForge/1.0)",
            "follow_external_links": False,
            "include_patterns": [],
            "exclude_patterns": ["\.pdf$", "\.jpg$", "\.png$", "\.gif$"]
        }
    }
    
    try:
        # Start crawl
        response = requests.post(
            'http://localhost:8000/crawl',
            headers=headers,
            json=crawl_data
        )
        
        if response.status_code == 202:
            result = response.json()
            crawl_id = result.get('crawl_id')
            print(f"✅ Crawl started successfully!")
            print(f"📋 Crawl ID: {crawl_id}")
            
            # Monitor progress for 2 minutes
            if crawl_id:
                print("\\n⏱️ Monitoring progress...")
                for i in range(120):  # 2 minutes
                    time.sleep(1)
                    
                    try:
                        status_response = requests.get(
                            f'http://localhost:8000/crawl/{crawl_id}',
                            headers=headers
                        )
                        
                        if status_response.status_code == 200:
                            status = status_response.json()
                            state = status.get('state', 'unknown')
                            progress = status.get('progress', {})
                            
                            pages_crawled = progress.get('pages_crawled', 0)
                            content_extracted = progress.get('content_extracted', 0)
                            
                            print(f"   [{i+1:3d}s] State: {state}, Pages: {pages_crawled}, Content: {content_extracted}")
                            
                            if state in ['completed', 'failed', 'cancelled']:
                                print(f"🏁 Crawl finished with state: {state}")
                                if state == 'failed':
                                    error = status.get('error')
                                    if error:
                                        print(f"❌ Error: {error}")
                                break
                        else:
                            if status_response.status_code == 401:
                                print(f"   [{i+1:3d}s] ❌ Auth failed - token may have expired")
                                break
                            else:
                                print(f"   [{i+1:3d}s] ⚠️ Status check failed: {status_response.status_code}")
                    
                    except Exception as e:
                        print(f"   [{i+1:3d}s] ⚠️ Error checking status: {e}")
                
                # Final status check
                print("\\n📋 Final Status Check:")
                try:
                    final_response = requests.get(
                        f'http://localhost:8000/crawl/{crawl_id}',
                        headers=headers
                    )
                    if final_response.status_code == 200:
                        final_status = final_response.json()
                        print(json.dumps(final_status, indent=2))
                        
                        # Check if we got content
                        progress = final_status.get('progress', {})
                        if progress.get('content_extracted', 0) > 0:
                            print("\\n✅ SUCCESS: Content was extracted!")
                            return True
                        else:
                            print("\\n⚠️ Crawl completed but no content extracted")
                    else:
                        print(f"❌ Final status check failed: {final_response.status_code}")
                except Exception as e:
                    print(f"❌ Error getting final status: {e}")
        
        else:
            print(f"❌ Failed to start crawl: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Crawl request failed: {e}")
        return False
    
    return False

def main():
    """Main test function."""
    print("🚀 VoiceForge Auth Fix & Crawl Test")
    print("=" * 40)
    
    success = test_auth_fix()
    
    if success:
        print("\\n🎉 ALL TESTS PASSED!")
        print("\\n🎯 Next Steps:")
        print("   1. Check domains list in frontend")
        print("   2. Test content generation")
        print("   3. Run: python process_simple.py (if needed)")
    else:
        print("\\n⚠️ Some tests failed, but auth should be fixed")
        print("\\n🔧 Troubleshooting:")
        print("   • Restart backend if auth was just fixed")
        print("   • Get a fresh token from the frontend")
        print("   • Check backend logs for errors")
    
    return success

if __name__ == "__main__":
    main()
