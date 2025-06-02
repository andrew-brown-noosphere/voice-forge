#!/usr/bin/env python3
"""
Debug the actual backend response to see what's causing empty errors.
"""

import requests
import json

def debug_backend_response():
    """Debug what the backend is actually returning."""
    
    print("🔍 DEBUGGING BACKEND RESPONSE")
    print("=" * 35)
    
    token = input("🔑 JWT token: ").strip()
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "query": "Write a test tweet",
        "platform": "twitter",
        "tone": "professional",
        "top_k": 5
    }
    
    print(f"\n📡 Making request to /rag/generate...")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            'http://localhost:8000/rag/generate',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"\n📊 RESPONSE DETAILS:")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
        print(f"Content-Length: {response.headers.get('content-length', 'Unknown')}")
        
        # Check raw response
        raw_content = response.content
        print(f"Raw content length: {len(raw_content)} bytes")
        print(f"Raw content (first 200 chars): {raw_content[:200]}")
        
        # Try to get text
        response_text = response.text
        print(f"Response text length: {len(response_text)} characters")
        print(f"Response text: '{response_text}'")
        
        # Try to parse JSON
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ JSON parsed successfully")
                print(f"JSON keys: {list(data.keys())}")
                print(f"Full JSON: {json.dumps(data, indent=2)}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON parse error: {e}")
                print("Raw response is not valid JSON")
        else:
            print(f"❌ HTTP Error {response.status_code}")
            if response_text:
                print(f"Error message: {response_text}")
            else:
                print("Empty error response - this is the problem!")
                
        # Check if it's a 500 error with empty body
        if response.status_code == 500 and not response_text.strip():
            print("\n🚨 FOUND THE ISSUE!")
            print("Backend is returning HTTP 500 with empty body")
            print("This means there's an unhandled exception in the backend")
            print("Check your backend terminal for Python tracebacks!")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out - backend is stuck")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - backend not responding")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def check_backend_logs():
    """Instructions for checking backend logs."""
    print("\n" + "=" * 50)
    print("🔍 NEXT STEPS - CHECK BACKEND LOGS:")
    print("=" * 50)
    print("1. Look at your backend terminal where uvicorn is running")
    print("2. Look for Python error tracebacks when you make the request")
    print("3. Common issues to look for:")
    print("   - ImportError (missing dependencies)")
    print("   - AttributeError (code bugs)")
    print("   - DatabaseError (connection issues)")
    print("   - AI service errors (OpenAI API, etc.)")
    print("   - Memory errors")
    print("\n4. If you see errors, copy them and we can fix them!")
    print("5. If no errors appear, the backend might be silently crashing")

if __name__ == "__main__":
    debug_backend_response()
    check_backend_logs()
