#!/usr/bin/env python3
"""
Debug script for VoiceForge content generation issues.
"""

import requests
import json
from datetime import datetime

def test_content_generation():
    """Test the content generation endpoint to identify issues."""
    
    print("🤖 Testing Content Generation Endpoint")
    print("=" * 40)
    
    # Get token from user
    token = input("🔑 Paste your JWT token: ").strip()
    
    if not token:
        print("❌ No token provided")
        return False
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Test data
    test_payload = {
        "query": "Write a test post about our company",
        "platform": "twitter",
        "tone": "professional",
        "top_k": 5
    }
    
    print(f"🧪 Testing with payload: {json.dumps(test_payload, indent=2)}")
    print("")
    
    try:
        # Test the RAG generate endpoint
        print("1️⃣ Testing /rag/generate endpoint...")
        response = requests.post(
            'http://localhost:8000/rag/generate', 
            headers=headers,
            json=test_payload,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ Content generation successful!")
                print(f"Response keys: {list(data.keys())}")
                
                if 'text' in data:
                    print(f"Generated text length: {len(data['text'])} characters")
                    print(f"Generated text preview: {data['text'][:100]}...")
                else:
                    print("⚠️ No 'text' field in response")
                
                if 'source_chunks' in data:
                    print(f"Source chunks: {len(data.get('source_chunks', []))}")
                    
                return True
                
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON response: {e}")
                print(f"Raw response: {response.text[:500]}...")
                return False
                
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Error response: {response.text}")
            
            # Check for common issues
            if response.status_code == 401:
                print("\n🔧 Authentication issue:")
                print("- Token might be expired")
                print("- Organization not selected")
                print("- Try refreshing your browser and getting a new token")
            elif response.status_code == 404:
                print("\n🔧 Endpoint not found:")
                print("- Backend might not be running")
                print("- RAG endpoint might not be available")
            elif response.status_code == 500:
                print("\n🔧 Server error:")
                print("- Check backend logs for errors")
                print("- AI service might be unavailable")
                print("- Database connection issues")
            
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (30 seconds)")
        print("🔧 This might indicate:")
        print("- AI processing is taking too long")
        print("- Backend is overwhelmed")
        print("- Network connectivity issues")
        return False
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection error")
        print("🔧 Check if backend is running on http://localhost:8000")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_prerequisites():
    """Test prerequisites for content generation."""
    print("\n2️⃣ Testing prerequisites...")
    
    token = input("🔑 Use the same JWT token (press Enter): ").strip()
    if not token:
        token = input("🔑 Paste your JWT token again: ").strip()
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Test auth
    try:
        auth_response = requests.get('http://localhost:8000/auth/me', headers=headers)
        if auth_response.status_code == 200:
            print("✅ Authentication working")
        else:
            print(f"❌ Auth issue: {auth_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Auth test failed: {e}")
        return False
    
    # Test domains
    try:
        domains_response = requests.get('http://localhost:8000/domains', headers=headers)
        if domains_response.status_code == 200:
            domains = domains_response.json()
            print(f"✅ Domains endpoint working ({len(domains)} domains)")
        else:
            print(f"⚠️ Domains issue: {domains_response.status_code} (non-critical)")
    except Exception as e:
        print(f"⚠️ Domains test failed: {e} (non-critical)")
    
    return True

def main():
    """Main diagnostic function."""
    print("🔍 VoiceForge Content Generation Diagnostics")
    print("=" * 45)
    print(f"Time: {datetime.now().isoformat()}")
    print("")
    
    # Test content generation
    success = test_content_generation()
    
    if not success:
        # Test prerequisites if main test failed
        prereq_success = test_prerequisites()
        
        if not prereq_success:
            print("\n❌ Prerequisites failed - fix authentication first")
        else:
            print("\n❌ Content generation failed despite good prerequisites")
    
    print("\n" + "=" * 45)
    if success:
        print("🎉 Content generation is working!")
        print("The issue might be intermittent or browser-specific.")
        print("Try refreshing your browser and testing again.")
    else:
        print("🔧 Troubleshooting steps:")
        print("1. Ensure backend is running on http://localhost:8000")
        print("2. Check backend logs for errors")
        print("3. Verify AI services are configured")
        print("4. Try a different browser or incognito mode")
        print("5. Check network connectivity")
    
    return success

if __name__ == "__main__":
    main()
