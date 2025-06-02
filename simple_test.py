#!/usr/bin/env python3
"""
Quick test to isolate the content generation issue.
"""

import requests
import json

def test_content_generation():
    """Test the exact API call the frontend is making."""
    
    print("🧪 Quick Content Generation Test")
    print("=" * 35)
    
    # Get token
    token = input("🔑 JWT token: ").strip()
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Test the exact payload structure
    payload = {
        "query": "Write a test tweet about AI",
        "platform": "twitter",
        "tone": "professional",
        "top_k": 5
    }
    
    print(f"\nTesting payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            'http://localhost:8000/rag/generate',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS!")
            print(f"Response keys: {list(data.keys())}")
            if 'text' in data:
                print(f"Generated: {data['text']}")
            else:
                print("❌ No 'text' in response")
                print(f"Full response: {data}")
        else:
            print(f"❌ FAILED: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_backend_health():
    """Quick backend health check."""
    try:
        response = requests.get('http://localhost:8000', timeout=5)
        print(f"✅ Backend alive: {response.status_code}")
        return True
    except:
        print("❌ Backend not responding")
        return False

if __name__ == "__main__":
    if test_backend_health():
        test_content_generation()
    else:
        print("Fix backend first!")
