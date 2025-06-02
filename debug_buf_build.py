#!/usr/bin/env python3
"""
Debug script to test buf.build domain handling in VoiceForge crawler.
"""
import sys
import os
sys.path.append('/Users/andrewbrown/Sites/noosphere/github/voice-forge/backend')

from urllib.parse import urlparse, urljoin
import re

class DomainDebugger:
    """Debug domain handling logic."""
    
    def __init__(self, domain: str):
        self.original_domain = domain
        self.normalized_domain = self._normalize_domain(domain)
        
    def _normalize_domain(self, domain: str) -> str:
        """Normalize domain URL (same as crawler)."""
        if not domain.startswith(('http://', 'https://')):
            domain = 'https://' + domain
        return domain.rstrip('/')
    
    def _get_base_domain(self, url: str) -> str:
        """Extract base domain from URL (same as crawler)."""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
    
    def _should_crawl_url(self, url: str, follow_external_links: bool = False) -> bool:
        """Determine if a URL should be crawled (same as crawler)."""
        # Skip non-HTTP URLs
        if not url.startswith(('http://', 'https://')):
            print(f"❌ Rejecting {url}: Not HTTP/HTTPS")
            return False
        
        # Check if URL is from the same domain
        base_domain = self._get_base_domain(self.normalized_domain)
        url_domain = self._get_base_domain(url)
        
        print(f"🔍 Domain comparison:")
        print(f"   Base domain: {base_domain}")
        print(f"   URL domain:  {url_domain}")
        print(f"   Match: {url_domain == base_domain}")
        
        if not follow_external_links and url_domain != base_domain:
            print(f"❌ Rejecting {url}: External domain")
            return False
        
        print(f"✅ Accepting {url}")
        return True
    
    def test_urls(self, test_urls: list, follow_external_links: bool = False):
        """Test a list of URLs."""
        print(f"🚀 Testing domain: {self.original_domain}")
        print(f"   Normalized to: {self.normalized_domain}")
        print(f"   Base domain: {self._get_base_domain(self.normalized_domain)}")
        print(f"   Follow external links: {follow_external_links}")
        print()
        
        for url in test_urls:
            print(f"Testing URL: {url}")
            result = self._should_crawl_url(url, follow_external_links)
            print(f"Result: {'✅ ACCEPT' if result else '❌ REJECT'}")
            print()

def main():
    # Test buf.build domain handling
    debugger = DomainDebugger("buf.build")
    
    test_urls = [
        "https://buf.build",
        "https://buf.build/",
        "https://buf.build/docs",
        "https://buf.build/docs/getting-started",
        "https://www.buf.build",
        "https://www.buf.build/",
        "https://api.buf.build",
        "https://api.buf.build/v1",
        "http://buf.build",
        "https://github.com/bufbuild",
        "https://docs.buf.build",
        "https://blog.buf.build",
        "https://buf.build:443",
        "https://buf.build:80"
    ]
    
    print("=" * 80)
    print("BUF.BUILD DOMAIN CRAWLING DEBUG")
    print("=" * 80)
    
    # Test with external links disabled (default)
    debugger.test_urls(test_urls, follow_external_links=False)
    
    print("=" * 80)
    print("WITH EXTERNAL LINKS ENABLED")
    print("=" * 80)
    
    # Test with external links enabled
    debugger.test_urls(test_urls, follow_external_links=True)

if __name__ == "__main__":
    main()
