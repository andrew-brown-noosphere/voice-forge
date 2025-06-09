#!/usr/bin/env python3
"""
Test script to verify the new platform configuration endpoints are working.
Run this after starting the backend server to test the implementation.
"""

import requests
import json
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"  # Adjust if your backend runs on a different port
SIGNALS_ENDPOINT = f"{BASE_URL}/signals"

# Test credentials (use dummy data for testing)
TEST_CONFIG = {
    "reddit": {
        "client_id": "test_client_id",
        "client_secret": "test_client_secret", 
        "user_agent": "VoiceForge Test Bot v1.0"
    },
    "twitter": {
        "api_key": "test_api_key",
        "api_secret": "test_api_secret",
        "access_token": "test_access_token"
    },
    "github": {
        "access_token": "test_github_token"
    },
    "linkedin": {
        "client_id": "test_linkedin_client_id",
        "client_secret": "test_linkedin_client_secret",
        "access_token": "test_linkedin_token"
    }
}

def test_platform_endpoints():
    """Test all the new platform configuration endpoints"""
    
    # You'll need to add proper authentication headers here
    headers = {
        "Content-Type": "application/json",
        # TODO: Add your authentication headers:
        # "Authorization": "Bearer your_token_here"
        # For now, we'll test without auth to check if endpoints exist
    }
    
    # Skip authentication for testing - update this with real auth later
    print("⚠️  Note: Testing without authentication - add real auth tokens for production")
    
    platforms = ["reddit", "twitter", "github", "linkedin"]
    
    print("🧪 Testing Voice Forge Platform Configuration Endpoints")
    print("=" * 60)
    
    for platform in platforms:
        print(f"\n🔧 Testing {platform.title()} Platform:")
        
        # Test 1: Get platform status (should show not_configured initially)
        print(f"  📊 Getting {platform} status...")
        try:
            response = requests.get(
                f"{SIGNALS_ENDPOINT}/platforms/{platform}/status",
                headers=headers
            )
            print(f"     Status: {response.status_code}")
            if response.status_code == 200:
                status_data = response.json()
                print(f"     Connection: {status_data.get('connection_status')}")
                print(f"     Config: {status_data.get('config_status')}")
            else:
                print(f"     Error: {response.text}")
        except Exception as e:
            print(f"     Error: {str(e)}")
        
        # Test 2: Configure platform
        print(f"  ⚙️  Configuring {platform}...")
        try:
            response = requests.post(
                f"{SIGNALS_ENDPOINT}/platforms/{platform}/configure",
                headers=headers,
                json=TEST_CONFIG[platform]
            )
            print(f"     Status: {response.status_code}")
            if response.status_code == 200:
                config_data = response.json()
                print(f"     Message: {config_data.get('message')}")
                print(f"     Next Steps: {len(config_data.get('next_steps', []))} items")
            else:
                print(f"     Error: {response.text}")
        except Exception as e:
            print(f"     Error: {str(e)}")
        
        # Test 3: Test platform connection
        print(f"  🔌 Testing {platform} connection...")
        try:
            response = requests.post(
                f"{SIGNALS_ENDPOINT}/platforms/{platform}/test-connection",
                headers=headers
            )
            print(f"     Status: {response.status_code}")
            if response.status_code == 200:
                test_data = response.json()
                print(f"     Test Result: {test_data.get('test_status')}")
                if test_data.get('error_details'):
                    print(f"     Error: {test_data.get('error_details')}")
                print(f"     Recommendations: {len(test_data.get('recommendations', []))} items")
            else:
                print(f"     Error: {response.text}")
        except Exception as e:
            print(f"     Error: {str(e)}")
        
        # Test 4: Get updated status
        print(f"  📊 Getting updated {platform} status...")
        try:
            response = requests.get(
                f"{SIGNALS_ENDPOINT}/platforms/{platform}/status",
                headers=headers
            )
            print(f"     Status: {response.status_code}")
            if response.status_code == 200:
                status_data = response.json()
                print(f"     Connection: {status_data.get('connection_status')}")
                print(f"     Config: {status_data.get('config_status')}")
                features = status_data.get('available_features', [])
                print(f"     Features: {len(features)} available")
            else:
                print(f"     Error: {response.text}")
        except Exception as e:
            print(f"     Error: {str(e)}")
    
    print(f"\n✅ Platform configuration testing completed!")
    print(f"\nNext steps:")
    print(f"  1. Check the backend logs for any errors")
    print(f"  2. Test the frontend platform configuration interface")
    print(f"  3. Run the database migration if needed:")
    print(f"     psql -d voiceforge -f backend/database/migrations/add_platform_configurations.sql")

if __name__ == "__main__":
    test_platform_endpoints()
