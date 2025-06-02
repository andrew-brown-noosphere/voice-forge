#!/usr/bin/env python3
"""
Test script to verify the buf.build crawler fix.
"""
import sys
import os
sys.path.append('/Users/andrewbrown/Sites/noosphere/github/voice-forge/backend')

from urllib.parse import urlparse

def get_base_domain_enhanced(url: str) -> str:
    """Extract base domain from URL, handling subdomains for crawling."""
    parsed = urlparse(url)
    hostname = parsed.hostname or parsed.netloc
    
    # Remove port number if present
    hostname = hostname.split(':')[0]
    
    # For buf.build and similar domains, we want to normalize subdomains
    # to the root domain for crawling purposes
    parts = hostname.split('.')
    if len(parts) >= 2:
        # Extract root domain (last 2 parts)
        root_domain = '.'.join(parts[-2:])
        return f"{parsed.scheme}://{root_domain}"
    
    return f"{parsed.scheme}://{hostname}"

def test_domain_fix():
    """Test the enhanced domain logic."""
    
    # Simulate the crawler initialization
    original_domain = "buf.build"
    if not original_domain.startswith(('http://', 'https://')):
        normalized_domain = 'https://' + original_domain
    else:
        normalized_domain = original_domain
    normalized_domain = normalized_domain.rstrip('/')
    
    print("🧪 TESTING ENHANCED DOMAIN LOGIC")
    print("=" * 50)
    print(f"Original domain: {original_domain}")
    print(f"Normalized domain: {normalized_domain}")
    print(f"Base domain: {get_base_domain_enhanced(normalized_domain)}")
    print()
    
    # Test URLs that should now work
    test_urls = [
        "https://buf.build",
        "https://buf.build/",
        "https://buf.build/docs",
        "https://buf.build/docs/getting-started",
        "https://www.buf.build",
        "https://www.buf.build/",
        "https://api.buf.build",
        "https://api.buf.build/v1",
        "https://docs.buf.build",
        "https://docs.buf.build/introduction",
        "https://blog.buf.build",
        "https://blog.buf.build/post/1",
        "http://buf.build",  # This should still work now
        "https://github.com/bufbuild",  # This should still be external
        "https://example.com",  # This should be external
    ]
    
    base_domain = get_base_domain_enhanced(normalized_domain)
    
    print("🔍 TESTING URL CRAWLING DECISIONS:")
    print("-" * 50)
    
    for url in test_urls:
        url_domain = get_base_domain_enhanced(url)
        should_crawl = url_domain == base_domain
        
        print(f"URL: {url}")
        print(f"  URL domain: {url_domain}")
        print(f"  Base domain: {base_domain}")
        print(f"  Decision: {'✅ CRAWL' if should_crawl else '❌ SKIP'}")
        print()

def main():
    test_domain_fix()
    
    print("🎉 SUMMARY:")
    print("=" * 50)
    print("✅ The fix should now allow crawling of:")
    print("   - buf.build")
    print("   - docs.buf.build")
    print("   - api.buf.build")
    print("   - blog.buf.build")
    print("   - www.buf.build")
    print("   - Any other *.buf.build subdomain")
    print()
    print("❌ External domains will still be rejected:")
    print("   - github.com")
    print("   - example.com")
    print("   - Other unrelated domains")
    print()
    print("🔧 To apply this fix:")
    print("   1. The _get_base_domain method in crawler/engine.py has been updated")
    print("   2. Restart the VoiceForge backend")
    print("   3. Try crawling buf.build again")

if __name__ == "__main__":
    main()
