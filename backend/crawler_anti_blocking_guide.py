"""
Enhanced crawler configuration to handle website blocking
Add these improvements to your crawler to reduce blocking
"""

# Enhanced User-Agent rotation
USER_AGENTS = [
    # Standard browsers
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    
    # Search engine bots (usually allowed)
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
    
    # Custom bot (be respectful)
    "Mozilla/5.0 (compatible; VoiceForge-Bot/1.0; +https://your-domain.com/bot)"
]

# Enhanced request headers to appear more human-like
ENHANCED_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Cache-Control": "max-age=0"
}

# Crawler-friendly test sites for RAG automation testing
CRAWLER_FRIENDLY_TEST_SITES = [
    {
        "name": "HTTPBin Test API",
        "url": "https://httpbin.org",
        "description": "Reliable test service with multiple endpoints",
        "expected_pages": 3,
        "max_depth": 1
    },
    {
        "name": "Example.com",
        "url": "https://example.com",
        "description": "Standard test domain",
        "expected_pages": 1,
        "max_depth": 0
    },
    {
        "name": "W3C HTML Validator",
        "url": "https://validator.w3.org",
        "description": "W3C service, crawler-friendly",
        "expected_pages": 5,
        "max_depth": 2
    },
    {
        "name": "JSON Placeholder",
        "url": "https://jsonplaceholder.typicode.com",
        "description": "Fake REST API for testing",
        "expected_pages": 3,
        "max_depth": 1
    }
]

# Enhanced crawl configuration for avoiding blocks
ANTI_BLOCKING_CONFIG = {
    "delay": 3,  # 3 seconds between requests
    "timeout": 20,  # 20 second timeout
    "max_pages": 5,  # Limit pages for testing
    "max_depth": 2,  # Reasonable depth
    "follow_external_links": False,  # Stay on same domain
    "respect_robots_txt": True,  # Check robots.txt
    "retry_attempts": 3,  # Retry failed requests
    "retry_delay": 5,  # Wait 5 seconds between retries
    "concurrent_requests": 1,  # No parallel requests
    "session_rotation": True,  # Rotate sessions
}

def get_anti_blocking_config():
    """Get configuration designed to avoid crawler blocking"""
    return ANTI_BLOCKING_CONFIG.copy()

def get_test_site_config(site_name="HTTPBin Test API"):
    """Get configuration for a specific test site"""
    site = next((s for s in CRAWLER_FRIENDLY_TEST_SITES if s["name"] == site_name), None)
    if not site:
        site = CRAWLER_FRIENDLY_TEST_SITES[0]  # Default to first
    
    config = get_anti_blocking_config()
    config.update({
        "max_pages": site["expected_pages"],
        "max_depth": site["max_depth"]
    })
    
    return {
        "domain": site["url"],
        "config": config,
        "description": site["description"]
    }

def print_crawler_tips():
    """Print tips for avoiding crawler blocking"""
    tips = [
        "🤖 Use realistic User-Agent strings",
        "⏱️ Add delays between requests (2-5 seconds)",
        "🔄 Implement retry logic with exponential backoff",
        "📏 Limit concurrent requests (1-2 max)",
        "🤝 Respect robots.txt files",
        "🔍 Monitor response codes and adjust behavior",
        "📝 Use custom headers to appear more human-like",
        "🎯 Start with crawler-friendly sites for testing",
        "⚡ Avoid rapid-fire requests",
        "🔀 Rotate User-Agents and IP addresses if possible"
    ]
    
    print("🛡️ CRAWLER ANTI-BLOCKING TIPS:")
    for tip in tips:
        print(f"   {tip}")

def check_robots_txt(domain):
    """Check if a domain has robots.txt restrictions"""
    import requests
    
    try:
        robots_url = f"{domain.rstrip('/')}/robots.txt"
        response = requests.get(robots_url, timeout=5)
        
        if response.status_code == 200:
            robots_content = response.text.lower()
            
            # Check for bot restrictions
            if "user-agent: *" in robots_content and "disallow:" in robots_content:
                print(f"⚠️ {domain} has robots.txt restrictions")
                return False
            else:
                print(f"✅ {domain} robots.txt allows crawling")
                return True
        else:
            print(f"📝 {domain} has no robots.txt file")
            return True
            
    except Exception as e:
        print(f"❌ Could not check robots.txt for {domain}: {e}")
        return True  # Assume allowed if can't check

# Example usage for your VoiceForge system
def get_recommended_test_crawl():
    """Get the most recommended crawl configuration for testing RAG automation"""
    return {
        "domain": "https://httpbin.org",
        "config": {
            "max_pages": 3,
            "max_depth": 1,
            "delay": 2,
            "timeout": 15,
            "follow_external_links": False,
            "user_agent": "Mozilla/5.0 (compatible; VoiceForge-Bot/1.0; +https://your-domain.com/bot)"
        },
        "why_this_works": [
            "HTTPBin is designed for testing HTTP clients",
            "No anti-bot protection",
            "Fast and reliable responses",
            "Multiple pages to test pagination",
            "Perfect for testing RAG automation"
        ]
    }

if __name__ == "__main__":
    print("🕷️ VoiceForge Crawler Anti-Blocking Guide")
    print("=" * 50)
    
    print_crawler_tips()
    
    print(f"\n{'=' * 50}")
    print("🧪 RECOMMENDED TEST CONFIGURATION")
    
    test_config = get_recommended_test_crawl()
    print(f"Domain: {test_config['domain']}")
    print("Configuration:")
    for key, value in test_config['config'].items():
        print(f"  {key}: {value}")
    
    print(f"\n✅ Why this works:")
    for reason in test_config['why_this_works']:
        print(f"  - {reason}")
    
    print(f"\n🚀 Next step: Test your RAG automation with this configuration!")
