#!/usr/bin/env python3
"""
Quick debug script to test what's happening with SignPath crawling
"""

import requests
import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

def test_signpath_access():
    """Test basic access to SignPath.io"""
    
    print("🔍 TESTING SIGNPATH.IO ACCESS")
    print("=" * 50)
    
    url = "https://signpath.io"
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    
    try:
        print(f"1. 🌐 Testing GET request to {url}")
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
        print(f"   Content Length: {len(response.text)} characters")
        
        if response.status_code == 200:
            print("   ✅ Basic access successful!")
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check for basic content
            title = soup.title.get_text() if soup.title else "No title"
            print(f"   Page Title: {title}")
            
            # Count links
            links = soup.find_all('a', href=True)
            print(f"   Found {len(links)} links")
            
            # Test include patterns against found links
            include_patterns = [
                r".*/product/?$",
                r".*/product/.*",
                r".*/blog/?$", 
                r".*/blog/.*"
            ]
            
            print(f"\n2. 🔍 Testing include patterns against found links:")
            matching_links = []
            
            for a_tag in links[:20]:  # Test first 20 links
                href = a_tag['href']
                try:
                    absolute_url = urljoin(url, href)
                    absolute_url = absolute_url.split('#')[0].rstrip('/')
                    
                    for pattern in include_patterns:
                        if re.search(pattern, absolute_url):
                            matching_links.append(absolute_url)
                            print(f"   ✅ MATCH: {absolute_url} (pattern: {pattern})")
                            break
                except:
                    pass
            
            print(f"\n   Found {len(matching_links)} matching links out of {len(links)} total")
            
            if len(matching_links) == 0:
                print("   ❌ NO LINKS MATCH INCLUDE PATTERNS!")
                print("   This confirms the include pattern is too restrictive.")
                print("\n   Sample links found:")
                for a_tag in links[:10]:
                    href = a_tag['href']
                    try:
                        absolute_url = urljoin(url, href)
                        absolute_url = absolute_url.split('#')[0].rstrip('/')
                        print(f"     {absolute_url}")
                    except:
                        pass
            
            # Test content extraction
            print(f"\n3. 🔍 Testing content extraction:")
            
            # Remove scripts, styles, etc.
            for script in soup(["script", "style", "iframe", "noscript"]):
                script.decompose()
            
            # Try to find main content
            main_content = None
            for selector in ["article", "main", "#content", ".content", ".post"]:
                element = soup.select_one(selector)
                if element:
                    main_content = element
                    print(f"   Found main content using selector: {selector}")
                    break
            
            if main_content:
                text = main_content.get_text()
                text = re.sub(r'\s+', ' ', text).strip()
                print(f"   Content length: {len(text)} characters")
                print(f"   Content preview: {text[:200]}...")
                
                if len(text) >= 100:
                    print("   ✅ Content is long enough for extraction")
                else:
                    print("   ❌ Content too short (< 100 chars)")
            else:
                # Fallback to body
                body_text = soup.body.get_text() if soup.body else ""
                body_text = re.sub(r'\s+', ' ', body_text).strip()
                print(f"   Using body text: {len(body_text)} characters")
                print(f"   Body preview: {body_text[:200]}...")
        
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("   ❌ Request timed out")
    except requests.exceptions.ConnectionError:
        print("   ❌ Connection error")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")

def test_include_patterns():
    """Test include patterns against common URLs"""
    
    print(f"\n🔍 TESTING INCLUDE PATTERNS")
    print("=" * 50)
    
    test_urls = [
        "https://signpath.io",
        "https://signpath.io/",
        "https://signpath.io/about",
        "https://signpath.io/contact",
        "https://signpath.io/product",
        "https://signpath.io/product/",
        "https://signpath.io/product/features",
        "https://signpath.io/blog",
        "https://signpath.io/blog/",
        "https://signpath.io/blog/some-post",
        "https://signpath.io/docs",
        "https://signpath.io/pricing",
    ]
    
    include_patterns = [
        r".*/product/?$",
        r".*/product/.*",
        r".*/blog/?$", 
        r".*/blog/.*"
    ]
    
    print("Include patterns:")
    for pattern in include_patterns:
        print(f"  {pattern}")
    
    print(f"\nTesting URLs:")
    for url in test_urls:
        matches = False
        matching_pattern = None
        
        for pattern in include_patterns:
            if re.search(pattern, url):
                matches = True
                matching_pattern = pattern
                break
        
        status = "✅ INCLUDED" if matches else "❌ EXCLUDED"
        pattern_info = f" (matches: {matching_pattern})" if matches else ""
        print(f"  {status} {url}{pattern_info}")

if __name__ == "__main__":
    test_signpath_access()
    test_include_patterns()
    
    print(f"\n🎯 SUMMARY:")
    print("=" * 50)
    print("Run this script to diagnose the crawling issues:")
    print(f"  cd /Users/andrewbrown/Sites/noosphere/github/voice-forge")
    print(f"  python debug_signpath_crawl.py")
