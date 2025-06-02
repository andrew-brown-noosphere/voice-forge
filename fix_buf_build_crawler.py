#!/usr/bin/env python3
"""
Fix for VoiceForge crawler to properly handle buf.build subdomains.
"""
import sys
import os
sys.path.append('/Users/andrewbrown/Sites/noosphere/github/voice-forge/backend')

def create_improved_domain_logic():
    """
    Create improved domain matching logic for buf.build and similar domains.
    """
    improved_code = '''
def _get_root_domain(self, url: str) -> str:
    """Extract root domain from URL (e.g., buf.build from docs.buf.build)."""
    from urllib.parse import urlparse
    import re
    
    parsed = urlparse(url)
    hostname = parsed.hostname or parsed.netloc
    
    # Remove port number if present
    hostname = hostname.split(':')[0]
    
    # For domains like buf.build, we want to extract the root domain
    # This handles cases like docs.buf.build -> buf.build
    parts = hostname.split('.')
    if len(parts) >= 2:
        # For most cases, take the last two parts (domain.tld)
        root_domain = '.'.join(parts[-2:])
        return f"{parsed.scheme}://{root_domain}"
    
    return f"{parsed.scheme}://{hostname}"

def _should_crawl_url(self, url: str) -> bool:
    """Determine if a URL should be crawled - IMPROVED VERSION."""
    # Skip non-HTTP URLs
    if not url.startswith(('http://', 'https://')):
        return False
    
    # Skip already visited URLs
    if url in self.visited_urls or url in self.discovered_urls:
        return False
    
    # IMPROVED: Check if URL is from the same root domain
    base_root_domain = self._get_root_domain(self.domain)
    url_root_domain = self._get_root_domain(url)
    
    # Allow both exact matches and subdomain matches within the same root domain
    if not self.config.follow_external_links:
        # Extract just the domain part for comparison
        base_domain_part = base_root_domain.split('://', 1)[1]  # Remove protocol
        url_domain_part = url_root_domain.split('://', 1)[1]    # Remove protocol
        
        # Allow if the domains match (buf.build == buf.build)
        # OR if one is a subdomain of the other (docs.buf.build contains buf.build)
        if not (base_domain_part == url_domain_part or 
                base_domain_part in url_domain_part or 
                url_domain_part in base_domain_part):
            return False
    
    # Apply exclude patterns
    for pattern in self.config.exclude_patterns:
        if re.search(pattern, url):
            return False
    
    # Apply include patterns if any
    if self.config.include_patterns:
        for pattern in self.config.include_patterns:
            if re.search(pattern, url):
                return True
        return False
    
    return True
'''
    return improved_code

def analyze_buf_build_issue():
    """Analyze the specific buf.build crawling issue."""
    
    print("🔍 BUF.BUILD CRAWLER ISSUE ANALYSIS")
    print("=" * 60)
    print()
    
    print("❌ CURRENT ISSUE:")
    print("  - buf.build domain gets normalized to: https://buf.build")
    print("  - Subdomains like docs.buf.build, api.buf.build are rejected as 'external'")
    print("  - This severely limits crawling since many modern sites use subdomains")
    print()
    
    print("🔧 ROOT CAUSE:")
    print("  - The _get_base_domain() method in crawler/engine.py is too strict")
    print("  - It uses urlparse(url).netloc which includes subdomains")
    print("  - No logic to handle subdomain relationships")
    print()
    
    print("✅ RECOMMENDED FIX:")
    print("  1. Add a _get_root_domain() method to extract the main domain")
    print("  2. Modify _should_crawl_url() to allow subdomains of the target domain")
    print("  3. Add configuration option for subdomain crawling")
    print()
    
    print("🎯 SPECIFIC CHANGES NEEDED:")
    print("  File: /Users/andrewbrown/Sites/noosphere/github/voice-forge/backend/crawler/engine.py")
    print("  - Replace or enhance the domain matching logic")
    print("  - Test with buf.build, docs.buf.build, api.buf.build")
    print()
    
    print("⚙️ CONFIGURATION OPTIONS TO ADD:")
    print("  - allow_subdomains: bool = True  # Allow subdomains of target domain")
    print("  - subdomain_patterns: List[str]  # Specific subdomain patterns to allow/deny")
    print()

def main():
    analyze_buf_build_issue()
    
    print("💡 IMPROVED CODE:")
    print("=" * 60)
    print(create_improved_domain_logic())

if __name__ == "__main__":
    main()
