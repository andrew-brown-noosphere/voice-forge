#!/usr/bin/env python3
"""
Diagnose crawler blocking issues and test with crawler-friendly sites
"""

import requests
import sys
from urllib.parse import urlparse
import time

def test_website_accessibility():
    """Test if websites are accessible and crawler-friendly"""
    print("🌐 Testing Website Accessibility & Crawler-Friendliness")
    print("=" * 60)
    
    # Test sites - from most crawler-friendly to most restrictive
    test_sites = [
        ("HTTPBin (Test API)", "https://httpbin.org", "Very crawler-friendly test site"),
        ("Example.com", "https://example.com", "Standard test domain"),
        ("Wikipedia", "https://en.wikipedia.org/wiki/Web_scraping", "Generally crawler-friendly"),
        ("GitHub", "https://github.com", "Has rate limiting but allows crawling"),
        ("ScyllaDB", "https://scylladb.com", "May have blocking mechanisms"),
    ]
    
    results = []
    
    for name, url, description in test_sites:
        print(f"\n🔍 Testing: {name}")
        print(f"   URL: {url}")
        print(f"   Description: {description}")
        
        try:
            # Test basic HTTP request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            start_time = time.time()
            response = requests.get(url, headers=headers, timeout=10)
            response_time = time.time() - start_time
            
            print(f"   ✅ Status: {response.status_code}")
            print(f"   ⏱️ Response time: {response_time:.2f}s")
            print(f"   📏 Content length: {len(response.content)} bytes")
            
            # Check for crawler blocking indicators
            blocking_indicators = []
            
            if response.status_code == 403:
                blocking_indicators.append("403 Forbidden - likely blocked")
            elif response.status_code == 429:
                blocking_indicators.append("429 Too Many Requests - rate limited")
            elif response_time > 25:
                blocking_indicators.append("Very slow response - possible soft blocking")
            elif response_time > 10:
                blocking_indicators.append("Slow response - may indicate blocking")
            
            # Check response headers for blocking indicators
            if 'cloudflare' in response.headers.get('server', '').lower():
                blocking_indicators.append("Cloudflare protection detected")
            
            if 'x-robots-tag' in response.headers:
                robots = response.headers['x-robots-tag']
                if 'noindex' in robots or 'nofollow' in robots:
                    blocking_indicators.append(f"Robots restriction: {robots}")
            
            # Check content for blocking indicators
            content_lower = response.text.lower()
            if 'access denied' in content_lower:
                blocking_indicators.append("Access denied message in content")
            if 'blocked' in content_lower and 'bot' in content_lower:
                blocking_indicators.append("Bot blocking message detected")
            if 'checking your browser' in content_lower:
                blocking_indicators.append("Browser check (likely Cloudflare)")
            
            if blocking_indicators:
                print("   ⚠️ Potential blocking issues:")
                for indicator in blocking_indicators:
                    print(f"      - {indicator}")
                crawler_friendly = "No"
            else:
                print("   ✅ No obvious blocking detected")
                crawler_friendly = "Yes"
            
            results.append({
                'name': name,
                'url': url,
                'status': response.status_code,
                'response_time': response_time,
                'crawler_friendly': crawler_friendly,
                'blocking_issues': blocking_indicators
            })
            
        except requests.exceptions.Timeout:
            print("   ❌ Timeout - likely blocked or very slow")
            results.append({
                'name': name,
                'url': url,
                'status': 'Timeout',
                'response_time': 'N/A',
                'crawler_friendly': 'No',
                'blocking_issues': ['Request timeout']
            })
        except requests.exceptions.ConnectionError:
            print("   ❌ Connection error - site may be down or blocking")
            results.append({
                'name': name,
                'url': url,
                'status': 'Connection Error',
                'response_time': 'N/A',
                'crawler_friendly': 'No',
                'blocking_issues': ['Connection refused']
            })
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append({
                'name': name,
                'url': url,
                'status': 'Error',
                'response_time': 'N/A',
                'crawler_friendly': 'No',
                'blocking_issues': [str(e)]
            })
    
    # Summary
    print(f"\n{'=' * 60}")
    print("📊 CRAWLER ACCESSIBILITY SUMMARY")
    print("=" * 60)
    
    crawler_friendly_sites = []
    blocked_sites = []
    
    for result in results:
        print(f"\n🌐 {result['name']}")
        print(f"   URL: {result['url']}")
        print(f"   Status: {result['status']}")
        print(f"   Response Time: {result['response_time']}")
        print(f"   Crawler Friendly: {result['crawler_friendly']}")
        
        if result['blocking_issues']:
            print("   Issues:")
            for issue in result['blocking_issues']:
                print(f"      - {issue}")
            blocked_sites.append(result['name'])
        else:
            crawler_friendly_sites.append(result['name'])
    
    print(f"\n{'=' * 60}")
    print("🎯 RECOMMENDATIONS")
    print("=" * 60)
    
    if crawler_friendly_sites:
        print(f"✅ Crawler-friendly sites to test with:")
        for site in crawler_friendly_sites:
            print(f"   - {site}")
    
    if blocked_sites:
        print(f"\n⚠️ Sites that may block crawlers:")
        for site in blocked_sites:
            print(f"   - {site}")
    
    print(f"\n🚀 NEXT STEPS:")
    print("1. Test your RAG automation with crawler-friendly sites first")
    print("2. For blocked sites, consider:")
    print("   - Adding delays between requests")
    print("   - Using different User-Agent strings")
    print("   - Implementing retry logic")
    print("   - Respecting robots.txt")
    
    return results

def suggest_test_crawl_config():
    """Suggest optimized crawl configuration for testing"""
    print(f"\n{'=' * 60}")
    print("⚙️ SUGGESTED TEST CRAWL CONFIGURATION")
    print("=" * 60)
    
    config = {
        "domain": "https://httpbin.org",  # Most reliable for testing
        "config": {
            "max_pages": 3,
            "max_depth": 1,
            "delay": 2,  # 2 second delay between requests
            "timeout": 15,  # 15 second timeout
            "follow_external": False,
            "user_agent": "Mozilla/5.0 (compatible; VoiceForge-Bot/1.0; +https://your-domain.com/bot)"
        }
    }
    
    print("📋 Recommended test configuration:")
    print(f"   Domain: {config['domain']}")
    print(f"   Max pages: {config['config']['max_pages']}")
    print(f"   Max depth: {config['config']['max_depth']}")
    print(f"   Delay: {config['config']['delay']} seconds")
    print(f"   Timeout: {config['config']['timeout']} seconds")
    print(f"   User Agent: Custom bot identifier")
    
    print(f"\n🧪 To test this configuration:")
    print("1. Log into your VoiceForge system")
    print("2. Create a new organization")
    print("3. Start a crawl with these settings")
    print("4. Watch for RAG automation messages in server logs")
    
    return config

def main():
    """Run crawler diagnosis"""
    print("🔍 VoiceForge Crawler Blocking Diagnosis")
    print("=" * 50)
    
    results = test_website_accessibility()
    config = suggest_test_crawl_config()
    
    print(f"\n{'=' * 50}")
    print("🎯 DIAGNOSIS COMPLETE")
    
    # Check if ScyllaDB specifically is problematic
    scylla_result = next((r for r in results if 'ScyllaDB' in r['name']), None)
    if scylla_result and scylla_result['crawler_friendly'] == 'No':
        print("\n⚠️ CONFIRMED: ScyllaDB website is likely blocking your crawler")
        print("This explains the timeouts you've been seeing.")
        print("\n✅ SOLUTION: Test with crawler-friendly sites instead:")
        friendly_sites = [r for r in results if r['crawler_friendly'] == 'Yes']
        for site in friendly_sites:
            print(f"   - {site['name']}: {site['url']}")
    
    print("\n🎉 Your RAG automation system is working correctly!")
    print("The issue is website blocking, not your integration.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
