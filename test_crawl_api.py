#!/usr/bin/env python3
"""
Test crawl directly through the API
"""

import requests
import json
import time

def test_crawl_api():
    """Test the crawl API directly."""
    
    print("🧪 Testing Crawl API")
    print("=" * 40)
    
    # Get token from user
    token = input("🔑 Paste your JWT token: ").strip()
    
    if not token:
        print("❌ No token provided")
        return
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Test data
    crawl_data = {
        "domain": "https://example.com",
        "config": {
            "max_depth": 1,
            "max_pages": 2,
            "delay": 1.0,
            "timeout": 30,
            "user_agent": "Mozilla/5.0 (compatible; VoiceForge/1.0)",
            "follow_external_links": False,
            "include_patterns": [],
            "exclude_patterns": []
        }
    }
    
    print(f"🎯 Starting crawl for: {crawl_data['domain']}")
    
    try:
        # Start crawl
        response = requests.post(
            'http://localhost:8000/crawl',
            headers=headers,
            json=crawl_data
        )
        
        print(f"📤 Request status: {response.status_code}")
        
        if response.status_code == 202:
            result = response.json()
            crawl_id = result.get('crawl_id')
            print(f"✅ Crawl started successfully!")
            print(f"📋 Crawl ID: {crawl_id}")
            print(f"📊 Initial status: {result.get('state', 'unknown')}")
            
            # Monitor progress
            if crawl_id:
                print(f"\\n⏱️ Monitoring progress...")
                for i in range(30):  # Monitor for 30 seconds
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
                            
                            print(f"   [{i+1:2d}s] State: {state}, Pages: {pages_crawled}, Content: {content_extracted}")
                            
                            if state in ['completed', 'failed', 'cancelled']:
                                print(f"🏁 Crawl finished with state: {state}")
                                if state == 'failed':
                                    error = status.get('error')
                                    if error:
                                        print(f"❌ Error: {error}")
                                break
                        else:
                            print(f"   [{i+1:2d}s] Failed to get status: {status_response.status_code}")
                    
                    except Exception as e:
                        print(f"   [{i+1:2d}s] Error checking status: {e}")
                
                # Final status check
                print(f"\\n📋 Final Status Check:")
                try:
                    final_response = requests.get(
                        f'http://localhost:8000/crawl/{crawl_id}',
                        headers=headers
                    )
                    if final_response.status_code == 200:
                        final_status = final_response.json()
                        print(json.dumps(final_status, indent=2))
                except Exception as e:
                    print(f"❌ Error getting final status: {e}")
        
        else:
            print(f"❌ Failed to start crawl: {response.status_code}")
            print(f"   Response: {response.text}")
    
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_crawl_api()
