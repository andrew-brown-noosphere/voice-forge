#!/usr/bin/env python3
"""
Quick diagnostic script to test if your IP is banned by buf.build/Cloudflare.
"""
import requests
import time
from urllib.parse import urlparse

def test_ip_ban_status():
    """Test if current IP is banned by buf.build."""
    
    print("🔍 TESTING IP BAN STATUS FOR BUF.BUILD")
    print("=" * 50)
    
    # Test sites to check
    test_sites = [
        ("Your IP", "https://httpbin.org/ip"),
        ("buf.build main", "https://buf.build"),
        ("buf.build docs", "https://docs.buf.build"),
        ("Cloudflare test", "https://www.cloudflare.com"),
        ("Normal site", "https://httpbin.org/get")
    ]
    
    for name, url in test_sites:
        print(f"\n🧪 Testing {name}: {url}")
        try:
            response = requests.get(
                url, 
                timeout=15,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                }
            )
            
            print(f"  ✅ Status: {response.status_code}")
            print(f"  📊 Response size: {len(response.content)} bytes")
            
            # Check for Cloudflare indicators
            content_lower = response.text.lower()
            cloudflare_indicators = [
                'cloudflare',
                'cf-ray',
                'ddos protection',
                'checking your browser',
                'access denied',
                'blocked',
                'bot',
                'captcha'
            ]
            
            found_indicators = [ind for ind in cloudflare_indicators if ind in content_lower]
            if found_indicators:
                print(f"  ⚠️  Cloudflare indicators found: {found_indicators}")
            else:
                print(f"  ✅ No obvious blocking detected")
                
            # Check response headers
            suspicious_headers = ['cf-ray', 'server']
            for header in suspicious_headers:
                if header in response.headers:
                    print(f"  🔍 {header}: {response.headers[header]}")
                    
        except requests.exceptions.Timeout:
            print(f"  ❌ TIMEOUT - Possible blocking")
        except requests.exceptions.ConnectionError:
            print(f"  ❌ CONNECTION ERROR - Possible blocking") 
        except Exception as e:
            print(f"  ❌ ERROR: {str(e)}")
        
        # Small delay between requests
        time.sleep(2)
    
    print(f"\n" + "=" * 50)
    print("🔍 DIAGNOSIS:")
    print("- If buf.build shows errors but other sites work → IP likely banned")
    print("- If you see 'cloudflare' or 'checking browser' → Cloudflare protection active")
    print("- If timeouts on buf.build → Possible IP blocking")
    print("- If 403/429 errors → Rate limiting or ban")

def test_with_different_approaches():
    """Test buf.build with different request approaches."""
    
    print(f"\n🧪 TESTING DIFFERENT APPROACHES")
    print("=" * 50)
    
    approaches = [
        ("Basic requests", lambda: requests.get("https://buf.build", timeout=10)),
        ("With session", lambda: requests.Session().get("https://buf.build", timeout=10)),
        ("Chrome headers", lambda: requests.get(
            "https://buf.build", 
            timeout=10,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
        ))
    ]
    
    for name, request_func in approaches:
        print(f"\n📡 Trying {name}:")
        try:
            response = request_func()
            print(f"  ✅ Success: {response.status_code}")
            
            if response.status_code == 200:
                # Check for actual content vs. Cloudflare page
                if "buf" in response.text.lower() and "protocol" in response.text.lower():
                    print(f"  🎉 Got real buf.build content!")
                elif "cloudflare" in response.text.lower():
                    print(f"  ⚠️  Got Cloudflare protection page")
                else:
                    print(f"  ❓ Got response but unclear if real content")
            
        except Exception as e:
            print(f"  ❌ Failed: {str(e)}")

if __name__ == "__main__":
    test_ip_ban_status()
    test_with_different_approaches()
    
    print(f"\n💡 NEXT STEPS IF BANNED:")
    print("1. Try from different network (mobile hotspot)")
    print("2. Use VPN or proxy service")
    print("3. Deploy crawler to different IP/cloud region")
    print("4. Use professional scraping service (ScrapingBee, etc.)")
    print("5. Contact Cloudflare if legitimate use case")
