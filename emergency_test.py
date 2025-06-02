#!/usr/bin/env python3
"""
Emergency diagnostic for broken content generation.
"""

import requests
import json

def emergency_content_test():
    """Test content generation with maximum debugging."""
    
    print("🚨 EMERGENCY CONTENT GENERATION TEST")
    print("=" * 40)
    
    # Get token quickly
    token = input("🔑 Quick - paste JWT token: ").strip()
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Minimal test payload
    payload = {
        "query": "test post",
        "platform": "twitter", 
        "tone": "professional",
        "top_k": 5
    }
    
    print(f"\n🧪 Testing: {json.dumps(payload)}")
    
    try:
        print("\n📡 Making request to /rag/generate...")
        response = requests.post(
            'http://localhost:8000/rag/generate',
            headers=headers,
            json=payload,
            timeout=15
        )
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ SUCCESS!")
            data = response.json()
            print(f"Keys in response: {list(data.keys())}")
            if 'text' in data:
                print(f"Generated text: {data['text'][:100]}...")
            else:
                print("❌ No 'text' key in response!")
                print(f"Full response: {data}")
        else:
            print(f"❌ FAILED - Status {response.status_code}")
            print(f"Error response: {response.text}")
            
            # Quick diagnosis
            if response.status_code == 401:
                print("🔧 AUTH ISSUE - refresh browser and get new token")
            elif response.status_code == 404:
                print("🔧 ENDPOINT MISSING - check backend startup logs")
            elif response.status_code == 500:
                print("🔧 SERVER ERROR - check backend terminal for error details")
                
    except requests.exceptions.ConnectionError:
        print("❌ CAN'T CONNECT TO BACKEND")
        print("🔧 Is backend running on localhost:8000?")
    except requests.exceptions.Timeout:
        print("❌ REQUEST TIMED OUT")
        print("🔧 Backend taking too long - check for infinite loops")
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")

def quick_backend_check():
    """Quick check if backend is alive."""
    print("\n🏥 Quick backend health check...")
    try:
        response = requests.get('http://localhost:8000', timeout=3)
        print(f"✅ Backend responding - Status {response.status_code}")
        return True
    except:
        print("❌ Backend not responding")
        return False

if __name__ == "__main__":
    if quick_backend_check():
        emergency_content_test()
    else:
        print("\n🔧 BACKEND IS DOWN!")
        print("1. Check if uvicorn process is running")
        print("2. Look at backend terminal for error messages")
        print("3. Restart: cd backend && python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")
