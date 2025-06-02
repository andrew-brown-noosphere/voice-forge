#!/usr/bin/env python3
"""
Debug connectivity issues between frontend and backend.
"""

import requests
import json
from datetime import datetime

def test_backend_connectivity():
    """Test if backend is accessible and responding."""
    
    print("🔗 VoiceForge Backend Connectivity Test")
    print("=" * 40)
    print(f"Time: {datetime.now().isoformat()}")
    print("")
    
    # Test basic backend connectivity
    print("1️⃣ Testing basic backend connectivity...")
    try:
        response = requests.get('http://localhost:8000', timeout=5)
        print(f"✅ Backend accessible - Status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend on localhost:8000")
        print("🔧 Check if backend is running with the right host/port")
        return False
    except requests.exceptions.Timeout:
        print("❌ Backend timeout - server too slow")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    # Test health endpoint
    print("\n2️⃣ Testing health endpoint...")
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"⚠️ Health endpoint returned {response.status_code}")
    except Exception as e:
        print(f"⚠️ Health endpoint failed: {e}")
    
    # Test with authentication
    print("\n3️⃣ Testing with authentication...")
    token = input("🔑 Paste your JWT token: ").strip()
    
    if not token:
        print("⚠️ No token provided - skipping auth tests")
        return True
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Test auth endpoint
    try:
        response = requests.get('http://localhost:8000/auth/me', headers=headers, timeout=5)
        if response.status_code == 200:
            print("✅ Authentication working")
            user_data = response.json()
            print(f"   User: {user_data.get('user_id', 'Unknown')}")
            print(f"   Org: {user_data.get('org_id', 'Unknown')}")
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Auth test failed: {e}")
        return False
    
    # Test crawls endpoint
    print("\n4️⃣ Testing crawls endpoint...")
    try:
        response = requests.get('http://localhost:8000/crawl?limit=5&offset=0', headers=headers, timeout=10)
        if response.status_code == 200:
            crawls = response.json()
            print(f"✅ Crawls endpoint working - Found {len(crawls)} crawls")
            if crawls:
                print(f"   Latest crawl: {crawls[0].get('domain', 'Unknown domain')}")
        else:
            print(f"❌ Crawls endpoint failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
    except Exception as e:
        print(f"❌ Crawls test failed: {e}")
        return False
    
    print("\n✅ All connectivity tests passed!")
    return True

def check_cors_headers():
    """Check if CORS headers are properly configured."""
    print("\n5️⃣ Testing CORS configuration...")
    
    try:
        # Test preflight request
        response = requests.options('http://localhost:8000/crawl', 
                                  headers={'Origin': 'http://localhost:5173'})
        
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
        }
        
        print("CORS Headers:")
        for header, value in cors_headers.items():
            if value:
                print(f"  ✅ {header}: {value}")
            else:
                print(f"  ⚠️ {header}: Not set")
        
        # Check if localhost:5173 is allowed
        origin_header = cors_headers.get('Access-Control-Allow-Origin', '')
        if 'localhost:5173' in origin_header or origin_header == '*':
            print("✅ Frontend origin allowed")
        else:
            print("❌ Frontend origin not allowed - CORS issue!")
            print("🔧 Backend needs to allow localhost:5173")
            
    except Exception as e:
        print(f"⚠️ CORS test failed: {e}")

def main():
    """Main test function."""
    success = test_backend_connectivity()
    check_cors_headers()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 Backend connectivity is working!")
        print("\n🔧 If frontend still shows 'Failed to fetch':")
        print("1. Check browser console for detailed errors")
        print("2. Try refreshing the page")
        print("3. Check if frontend is running on localhost:5173")
        print("4. Verify no browser extensions are blocking requests")
    else:
        print("❌ Backend connectivity issues found")
        print("\n🔧 Troubleshooting steps:")
        print("1. Ensure backend is running on localhost:8000")
        print("2. Check backend logs for errors")
        print("3. Verify authentication is working")
        print("4. Restart backend if needed")

if __name__ == "__main__":
    main()
