#!/usr/bin/env python3
"""
Quick setup script to get VoiceForge working with sample content.
"""

import requests
import json
import time

# Configuration
API_BASE = "http://localhost:8000"

def test_with_token(token):
    """Test API endpoints with a token."""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print("🧪 Testing API with your token...")
    
    # Test 1: Check domains
    print("\n1. Checking domains...")
    try:
        response = requests.get(f"{API_BASE}/domains", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            domains = response.json()
            print(f"   Domains found: {domains}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Start a sample crawl
    print("\n2. Starting a sample crawl...")
    try:
        crawl_data = {
            "domain": "https://example.com",
            "config": {
                "max_depth": 1,
                "max_pages": 3,
                "delay": 1.0
            }
        }
        
        response = requests.post(f"{API_BASE}/crawl", headers=headers, json=crawl_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 202:
            crawl_result = response.json()
            print(f"   Crawl started: {crawl_result}")
            return crawl_result.get('crawl_id')
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    return None

def check_crawl_status(crawl_id, token):
    """Check the status of a crawl."""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print(f"\n3. Checking crawl status for {crawl_id}...")
    try:
        response = requests.get(f"{API_BASE}/crawl/{crawl_id}", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            status = response.json()
            print(f"   Crawl status: {status.get('status')}")
            print(f"   Progress: {status.get('progress', 0) * 100:.1f}%")
            print(f"   Pages crawled: {status.get('pages_crawled', 0)}")
            return status
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    return None

def main():
    print("🚀 VoiceForge Quick Setup")
    print("=" * 50)
    
    # Get token from user
    print("\n📝 You need a JWT token from your frontend.")
    print("   1. Go to your VoiceForge app in the browser")
    print("   2. Open Developer Tools (F12)")
    print("   3. Go to Console tab")
    print("   4. Paste this and press Enter:")
    print("      useAuth().getToken({ skipCache: true }).then(console.log)")
    print("   5. Copy the token that appears")
    
    token = input("\n🔑 Paste your JWT token here: ").strip()
    
    if not token:
        print("❌ No token provided. Exiting.")
        return
    
    # Test API
    crawl_id = test_with_token(token)
    
    if crawl_id:
        print(f"\n⏱️  Waiting for crawl to complete...")
        for i in range(30):  # Wait up to 30 seconds
            time.sleep(1)
            status = check_crawl_status(crawl_id, token)
            if status and status.get('status') in ['completed', 'failed']:
                break
            print(f"   ... waiting ({i+1}/30)")
        
        # Check domains again
        print("\n4. Checking domains after crawl...")
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        try:
            response = requests.get(f"{API_BASE}/domains", headers=headers)
            if response.status_code == 200:
                domains = response.json()
                print(f"   Domains now: {domains}")
            else:
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"   Error: {e}")
    
    print("\n✅ Setup complete!")
    print("   You should now be able to generate content in the frontend.")

if __name__ == "__main__":
    main()
