#!/usr/bin/env python3
import requests
import json

def quick_ip_test():
    print("🔍 QUICK IP & ACCESS TEST")
    print("=" * 30)
    
    # Test 1: Get current IP
    try:
        response = requests.get("https://httpbin.org/ip", timeout=10)
        ip_info = response.json()
        print(f"📍 Your IP: {ip_info['origin']}")
    except Exception as e:
        print(f"❌ Can't get IP: {e}")
    
    # Test 2: Test buf.build access
    try:
        print("\n🧪 Testing buf.build access...")
        response = requests.get("https://buf.build", timeout=15)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text.lower()
            if "cloudflare" in content:
                print("⚠️  CLOUDFLARE PROTECTION DETECTED")
            elif "buf" in content and "protocol" in content:
                print("✅ REAL BUF.BUILD CONTENT ACCESSED")
            else:
                print("❓ Got response but content unclear")
        else:
            print(f"❌ Bad status code: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT - Likely blocked")
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR - Likely blocked")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    quick_ip_test()
