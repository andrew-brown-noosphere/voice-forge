#!/usr/bin/env python3
"""
VoiceForge Auth Test - Get crawls working with proper authentication
"""
import requests
import json
import os

def test_with_auth_bypass():
    """Test if we can temporarily bypass auth for debugging"""
    print("🔍 Testing crawl with auth bypass...")
    
    # Test if there's a debug/test endpoint that bypasses auth
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
    
    # Try with basic auth headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer test-token",
        "X-Test-Mode": "true"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/crawl", 
            json=crawl_data,
            headers=headers,
            timeout=15
        )
        
        print(f"📥 Response Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code in [200, 202]:
            print("✅ Crawl worked with auth headers!")
            return True
        else:
            print("❌ Still need proper auth")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def check_auth_config():
    """Check what auth is configured"""
    print("🔍 Checking auth configuration...")
    
    try:
        response = requests.get("http://localhost:8000/auth/debug")
        if response.status_code == 200:
            debug_info = response.json()
            print("📋 Auth Debug Info:")
            print(f"   Headers present: {list(debug_info.get('headers', {}).keys())}")
            print(f"   Auth credentials: {debug_info.get('auth_credentials', 'None')}")
            print(f"   Clerk verification: {debug_info.get('clerk_verification', 'None')}")
        
    except Exception as e:
        print(f"❌ Auth debug failed: {e}")

def suggest_auth_solutions():
    """Suggest ways to fix the auth issue"""
    print("\n🛠️ AUTH SOLUTIONS:")
    print("=" * 50)
    
    print("OPTION 1: Temporarily Disable Auth (Quick Fix)")
    print("✏️ Edit backend/api/main.py and comment out the auth dependency:")
    print("   # Change: current_user: AuthUser = Depends(get_current_user_with_org)")
    print("   # To:     current_user: AuthUser = None  # Temporary bypass")
    print()
    
    print("OPTION 2: Use Frontend Auth Token")
    print("✏️ If frontend is logged in, copy the auth token:")
    print("   1. Open browser dev tools on VoiceForge frontend")
    print("   2. Go to Network tab")
    print("   3. Try to start a crawl and capture the Authorization header")
    print("   4. Use that token for API testing")
    print()
    
    print("OPTION 3: Create Test Auth Endpoint")
    print("✏️ Add a test endpoint in backend/api/main.py:")
    print("   @app.post('/crawl-test')")
    print("   async def test_crawl(request: CrawlRequest):")
    print("       # No auth required for testing")
    print()
    
    print("OPTION 4: Check Clerk Configuration")
    print("✏️ Ensure Clerk auth service is properly configured")
    print("   - Check environment variables")
    print("   - Verify Clerk JWT tokens are valid")

def main():
    print("🔑 VOICEFORGE AUTH DIAGNOSTIC")
    print("=" * 50)
    
    check_auth_config()
    test_with_auth_bypass()
    suggest_auth_solutions()
    
    print("\n🎯 IMMEDIATE ACTION:")
    print("The simplest fix is to temporarily disable auth for testing.")
    print("Edit the /crawl endpoint in api/main.py and remove the auth dependency.")

if __name__ == "__main__":
    main()
