#!/usr/bin/env python3
"""
Debug resource exhaustion and session state issues.
"""

import requests
import json
import time

def test_multiple_requests():
    """Test multiple content generation requests to find the issue."""
    
    print("🔄 Testing Multiple Content Generation Requests")
    print("=" * 50)
    
    token = input("🔑 JWT token: ").strip()
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Test payloads
    payloads = [
        {
            "query": "Write a test tweet about AI",
            "platform": "twitter",
            "tone": "professional",
            "top_k": 5
        },
        {
            "query": "Write a professional LinkedIn post",
            "platform": "linkedin", 
            "tone": "professional",
            "top_k": 5
        },
        {
            "query": "Write a casual Facebook post",
            "platform": "facebook",
            "tone": "casual", 
            "top_k": 5
        }
    ]
    
    for i, payload in enumerate(payloads, 1):
        print(f"\n🧪 Request {i}: {payload['platform']} - {payload['tone']}")
        
        try:
            start_time = time.time()
            response = requests.post(
                'http://localhost:8000/rag/generate',
                headers=headers,
                json=payload,
                timeout=30
            )
            end_time = time.time()
            
            print(f"   Time: {end_time - start_time:.2f}s")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if 'text' in data and data['text']:
                    print(f"   ✅ SUCCESS: {data['text'][:50]}...")
                else:
                    print(f"   ❌ Empty response: {data}")
            else:
                print(f"   ❌ FAILED: {response.text[:100]}...")
                
                # If we get an error, stop testing
                print("\n🔧 Error after first success indicates:")
                print("   - Database connection pool exhausted")
                print("   - Memory leak in AI processing")
                print("   - Session state corruption")
                print("   - Backend process stuck")
                break
                
        except requests.exceptions.Timeout:
            print(f"   ❌ TIMEOUT - Backend stuck after request {i-1}")
            print("\n🔧 Timeout indicates backend is stuck/hanging")
            break
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            break
        
        # Small delay between requests
        time.sleep(1)
    
    print("\n" + "=" * 50)
    print("🔧 DIAGNOSIS:")
    print("If first request worked but subsequent ones failed:")
    print("1. Backend is getting stuck after first request")
    print("2. Database connection pool is exhausted") 
    print("3. AI service is hanging")
    print("4. Memory leak in processing")
    print("\n💡 QUICK FIXES:")
    print("1. Restart backend server")
    print("2. Check backend logs for hanging processes")
    print("3. Look for database connection errors")

def test_backend_endpoints():
    """Test if other endpoints still work."""
    print("\n🏥 Testing Other Endpoints...")
    
    token = input("🔑 Same JWT token (Enter to skip): ").strip()
    if not token:
        return
        
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Test different endpoints
    endpoints = [
        ('GET', '/auth/me', 'Authentication'),
        ('GET', '/domains', 'Domains'),
        ('GET', '/crawl?limit=1', 'Crawls'),
    ]
    
    for method, endpoint, name in endpoints:
        try:
            if method == 'GET':
                response = requests.get(f'http://localhost:8000{endpoint}', headers=headers, timeout=5)
            else:
                response = requests.post(f'http://localhost:8000{endpoint}', headers=headers, timeout=5)
                
            if response.status_code == 200:
                print(f"   ✅ {name}: Working")
            else:
                print(f"   ❌ {name}: Failed ({response.status_code})")
        except Exception as e:
            print(f"   ❌ {name}: Error ({e})")

if __name__ == "__main__":
    test_multiple_requests()
    test_backend_endpoints()
