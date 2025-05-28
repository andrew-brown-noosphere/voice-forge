#!/usr/bin/env python3
"""
Quick test to verify automated RAG integration is working
"""

import requests
import json
import sys
import time

def test_rag_health():
    """Test RAG health endpoint"""
    print("🩺 Testing RAG health endpoint...")
    
    try:
        response = requests.get("http://localhost:8000/api/rag/health")
        
        if response.status_code == 200:
            health_data = response.json()
            print("✅ RAG health endpoint working!")
            print(f"   Status: {health_data.get('status')}")
            print(f"   Background processing: {health_data.get('background_processing')}")
            print(f"   Auto-optimize enabled: {health_data.get('auto_optimize_enabled')}")
            return True
        else:
            print(f"❌ Health endpoint returned status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.ConnectionError:
        print("❌ Could not connect to server. Is it running?")
        print("   Start with: uvicorn api.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Error testing health endpoint: {e}")
        return False

def test_rag_readiness():
    """Test RAG readiness endpoint with a dummy org"""
    print("\n🔍 Testing RAG readiness endpoint...")
    
    try:
        response = requests.get("http://localhost:8000/api/rag/readiness/test-org-123")
        
        if response.status_code == 200:
            readiness_data = response.json()
            print("✅ RAG readiness endpoint working!")
            print(f"   Org ID: {readiness_data.get('org_id')}")
            print(f"   Ready: {readiness_data.get('ready')}")
            print(f"   Reason: {readiness_data.get('reason')}")
            if readiness_data.get('recommendations'):
                print(f"   Recommendations: {readiness_data.get('recommendations')}")
            return True
        else:
            print(f"❌ Readiness endpoint returned status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing readiness endpoint: {e}")
        return False

def test_rag_status():
    """Test RAG status endpoint with a dummy org"""
    print("\n📊 Testing RAG status endpoint...")
    
    try:
        response = requests.get("http://localhost:8000/api/rag/status/test-org-123")
        
        if response.status_code == 200:
            status_data = response.json()
            print("✅ RAG status endpoint working!")
            print(f"   Org ID: {status_data.get('org_id')}")
            print(f"   Status: {status_data.get('status')}")
            return True
        else:
            print(f"❌ Status endpoint returned status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing status endpoint: {e}")
        return False

def test_main_api():
    """Test main API is working"""
    print("\n🌍 Testing main API...")
    
    try:
        response = requests.get("http://localhost:8000/")
        
        if response.status_code == 200:
            api_data = response.json()
            print("✅ Main API working!")
            print(f"   Status: {api_data.get('status')}")
            print(f"   Version: {api_data.get('version')}")
            return True
        else:
            print(f"❌ Main API returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing main API: {e}")
        return False

def main():
    """Run quick integration tests"""
    print("🚀 Quick RAG Integration Test")
    print("=" * 40)
    
    tests = [
        ("Main API", test_main_api),
        ("RAG Health", test_rag_health),
        ("RAG Readiness", test_rag_readiness),
        ("RAG Status", test_rag_status),
    ]
    
    passed = 0
    for name, test_func in tests:
        if test_func():
            passed += 1
        else:
            print(f"❌ {name} test failed")
    
    print(f"\n{'=' * 40}")
    print(f"🎯 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! RAG integration is working!")
        print("\n📋 Try creating a new org and crawling content to see automatic optimization!")
    elif passed >= 2:
        print("⚠️  Most tests passed - server is running but some endpoints may need fixes")
    else:
        print("❌ Tests failed - check if server is running and endpoints are configured")
    
    return 0 if passed == len(tests) else 1

if __name__ == "__main__":
    sys.exit(main())
