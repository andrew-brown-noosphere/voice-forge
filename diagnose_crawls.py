#!/usr/bin/env python3
"""
VoiceForge Crawl Diagnostic Script - Find out what's actually broken
"""
import requests
import json
import sys
import traceback

def test_api_health():
    """Test if the main API is responding"""
    print("🔍 Testing API Health...")
    try:
        response = requests.get("http://localhost:8000/", timeout=10)
        print(f"✅ API Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ API Health Failed: {e}")
        return False

def test_auth_endpoints():
    """Test authentication endpoints"""
    print("\n🔍 Testing Auth Endpoints...")
    try:
        response = requests.get("http://localhost:8000/auth/health", timeout=10)
        print(f"✅ Auth Health: {response.status_code}")
        
        # Test debug endpoint
        response = requests.get("http://localhost:8000/auth/debug", timeout=10)
        print(f"✅ Auth Debug: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Auth Test Failed: {e}")
        return False

def test_simple_crawl():
    """Test a very simple crawl request"""
    print("\n🔍 Testing Simple Crawl...")
    
    # Test with minimal config
    crawl_data = {
        "domain": "httpbin.org",
        "config": {
            "max_depth": 1,
            "max_pages": 2,
            "delay": 1.0,
            "timeout": 30,
            "respect_robots_txt": True,
            "follow_external_links": False,
            "exclude_patterns": [],
            "include_patterns": [],
            "user_agent": "VoiceForge-Crawler/1.0"
        }
    }
    
    try:
        print(f"📤 Sending crawl request to httpbin.org...")
        print(f"   Config: {json.dumps(crawl_data['config'], indent=2)}")
        
        response = requests.post(
            "http://localhost:8000/crawl", 
            json=crawl_data,
            timeout=15
        )
        
        print(f"📥 Response Status: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200 or response.status_code == 202:
            result = response.json()
            print(f"✅ Crawl Started Successfully!")
            print(f"   Crawl ID: {result.get('crawl_id', 'unknown')}")
            print(f"   State: {result.get('state', 'unknown')}")
            return result.get('crawl_id')
        else:
            print(f"❌ Crawl Failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Crawl Request Failed: {e}")
        traceback.print_exc()
        return None

def test_crawl_with_new_config():
    """Test crawl with the new unlimited config"""
    print("\n🔍 Testing New Unlimited Config...")
    
    crawl_data = {
        "domain": "httpbin.org",
        "config": {
            "max_depth": 1,
            "max_pages": None,  # This is what's new
            "delay": 1.0,
            "timeout": 30,
            "respect_robots_txt": True,
            "follow_external_links": False,
            "exclude_patterns": [],
            "include_patterns": [],
            "user_agent_mode": "default",
            "organization_name": None,
            "contact_email": None,
            "custom_user_agent": None,
            "user_agent": "VoiceForge-Crawler/1.0"
        }
    }
    
    try:
        print(f"📤 Sending crawl with null max_pages...")
        response = requests.post(
            "http://localhost:8000/crawl", 
            json=crawl_data,
            timeout=15
        )
        
        print(f"📥 Response Status: {response.status_code}")
        
        if response.status_code == 200 or response.status_code == 202:
            result = response.json()
            print(f"✅ New Config Works!")
            print(f"   Crawl ID: {result.get('crawl_id', 'unknown')}")
            return result.get('crawl_id')
        else:
            print(f"❌ New Config Failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ New Config Test Failed: {e}")
        return None

def check_crawl_status(crawl_id):
    """Check the status of a crawl"""
    if not crawl_id:
        return
        
    print(f"\n🔍 Checking Crawl Status: {crawl_id}")
    try:
        response = requests.get(f"http://localhost:8000/crawl/{crawl_id}", timeout=10)
        print(f"📥 Status Response: {response.status_code}")
        
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Crawl Status Retrieved:")
            print(f"   State: {status.get('state', 'unknown')}")
            print(f"   Progress: {status.get('progress', {})}")
            print(f"   Error: {status.get('error', 'none')}")
        else:
            print(f"❌ Status Check Failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Status Check Error: {e}")

def main():
    print("🚨 VOICEFORGE CRAWL DIAGNOSTIC")
    print("=" * 50)
    
    # Test 1: Basic API
    if not test_api_health():
        print("\n💥 API is not responding - start the backend first!")
        return
    
    # Test 2: Auth
    if not test_auth_endpoints():
        print("\n⚠️ Auth endpoints have issues but continuing...")
    
    # Test 3: Simple crawl with old config
    print("\n" + "=" * 50)
    print("TESTING CRAWLS")
    print("=" * 50)
    
    crawl_id1 = test_simple_crawl()
    
    # Test 4: New unlimited config
    crawl_id2 = test_crawl_with_new_config()
    
    # Wait a moment then check status
    import time
    time.sleep(3)
    
    if crawl_id1:
        check_crawl_status(crawl_id1)
    
    if crawl_id2:
        check_crawl_status(crawl_id2)
    
    print("\n" + "=" * 50)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 50)
    
    if crawl_id1 or crawl_id2:
        print("✅ Some crawls worked - check specific errors above")
    else:
        print("❌ No crawls worked - check backend logs and auth configuration")

if __name__ == "__main__":
    main()
