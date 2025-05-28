#!/usr/bin/env python3
"""
Configure VoiceForge crawler to target specific paths only
"""

import json

def get_targeted_crawl_config(domain, target_paths=["/product", "/blog"]):
    """
    Get crawler configuration that targets only specific paths
    """
    
    # Build include patterns for your target paths
    include_patterns = []
    for path in target_paths:
        # Match exact path and subpaths
        include_patterns.extend([
            f".*{path}/?$",           # Exact path: /product or /product/
            f".*{path}/.*",           # Subpaths: /product/anything
        ])
    
    return {
        "domain": domain,
        "config": {
            "max_pages": 20,  # Allow more pages since we're being selective
            "max_depth": 3,   # Go deeper into product/blog sections
            "delay": 2,       # 2 seconds between requests
            "timeout": 15,    # 15 second timeout per page
            "follow_external_links": False,
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            
            # 🎯 KEY: Only crawl pages matching these patterns
            "include_patterns": include_patterns,
            
            # Exclude common problematic pages
            "exclude_patterns": [
                ".*/contact.*",      # Skip contact pages (slow)
                ".*/login.*",        # Skip login pages
                ".*/register.*",     # Skip registration
                ".*/checkout.*",     # Skip checkout flows
                ".*/cart.*",         # Skip shopping cart
                ".*/admin.*",        # Skip admin areas
                ".*\\.pdf$",         # Skip PDF files
                ".*\\.jpg$",         # Skip images
                ".*\\.png$",
                ".*\\.css$",         # Skip stylesheets
                ".*\\.js$",          # Skip JavaScript files
            ]
        }
    }

def get_signpath_config():
    """
    Specific configuration for SignPath focusing on product and blog
    """
    return get_targeted_crawl_config("https://signpath.io", ["/product", "/blog"])

def get_test_configs():
    """
    Get test configurations for different scenarios
    """
    return {
        "signpath_targeted": {
            "name": "SignPath - Product & Blog Only",
            "config": get_signpath_config(),
            "expected_behavior": "Will crawl product pages and blog posts, skip contact/slow pages"
        },
        
        "httpbin_test": {
            "name": "HTTPBin - Full Test",
            "config": get_targeted_crawl_config("https://httpbin.org", ["/", "/json", "/html"]),
            "expected_behavior": "Fast, reliable test to verify crawler works"
        },
        
        "example_targeted": {
            "name": "Example.com - Simple Test", 
            "config": get_targeted_crawl_config("https://example.com", ["/"]),
            "expected_behavior": "Single page test, very fast"
        }
    }

def show_curl_commands():
    """
    Show curl commands to test the targeted crawling
    """
    configs = get_test_configs()
    
    print("🚀 CURL COMMANDS TO TEST TARGETED CRAWLING")
    print("=" * 60)
    
    for key, test_config in configs.items():
        print(f"\n📋 {test_config['name']}")
        print(f"Expected: {test_config['expected_behavior']}")
        print(f"\nCurl command:")
        
        curl_cmd = f"""curl -X POST "http://localhost:8000/crawl" \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -d '{json.dumps(test_config['config'], indent=0)}'"""
        
        print(curl_cmd)
        print()

def explain_include_patterns():
    """
    Explain how the include patterns work
    """
    print("🎯 HOW INCLUDE PATTERNS WORK")  
    print("=" * 40)
    
    examples = [
        {
            "pattern": ".*/product/?$",
            "matches": [
                "https://signpath.io/product",
                "https://signpath.io/product/",
            ],
            "skips": [
                "https://signpath.io/contact",
                "https://signpath.io/about"
            ]
        },
        {
            "pattern": ".*/product/.*", 
            "matches": [
                "https://signpath.io/product/features",
                "https://signpath.io/product/pricing",
                "https://signpath.io/product/documentation"
            ],
            "skips": [
                "https://signpath.io/blog",
                "https://signpath.io/contact"
            ]
        },
        {
            "pattern": ".*/blog/.*",
            "matches": [
                "https://signpath.io/blog/post-1", 
                "https://signpath.io/blog/category/security",
                "https://signpath.io/blog/2024/01/article"
            ],
            "skips": [
                "https://signpath.io/product",
                "https://signpath.io/contact"
            ]
        }
    ]
    
    for example in examples:
        print(f"\n📝 Pattern: {example['pattern']}")
        print("   ✅ Matches:")
        for match in example['matches']:
            print(f"      {match}")
        print("   ❌ Skips:")
        for skip in example['skips']:
            print(f"      {skip}")

def test_targeted_crawling():
    """
    Show how to test the targeted crawling configuration
    """
    print(f"\n{'=' * 60}")
    print("🧪 TESTING YOUR TARGETED CRAWLING")
    print("=" * 60)
    
    print("1. 🎯 Start with SignPath product/blog only:")
    config = get_signpath_config()
    print(json.dumps(config, indent=2))
    
    print(f"\n2. 📊 What this will do:")
    print("   ✅ Crawl: https://signpath.io/product/*")
    print("   ✅ Crawl: https://signpath.io/blog/*") 
    print("   ❌ Skip: https://signpath.io/contact (the slow page!)")
    print("   ❌ Skip: https://signpath.io/login")
    print("   ❌ Skip: https://signpath.io/register")
    
    print(f"\n3. 🚀 Expected results:")
    print("   • Much faster crawling (skips slow pages)")
    print("   • Only relevant content (product + blog)")
    print("   • RAG optimization will trigger with focused content")
    print("   • Perfect for your use case!")
    
    print(f"\n4. 📋 Monitor with:")
    print("   curl http://localhost:8000/crawl/YOUR_CRAWL_ID")

def main():
    """
    Main function showing targeted crawling configuration
    """
    print("🎯 VOICEFORGE TARGETED CRAWLING CONFIGURATION")
    print("=" * 50)
    
    print("You want to crawl only /product and /blog paths.")
    print("This is perfect! It will:")
    print("✅ Skip slow pages like /contact")
    print("✅ Focus on relevant content")
    print("✅ Trigger RAG automation faster")
    print("✅ Be much more efficient")
    
    explain_include_patterns()
    
    print(f"\n{'=' * 50}")
    print("⚡ READY-TO-USE CONFIGURATION")
    print("=" * 50)
    
    config = get_signpath_config()
    print("SignPath Product + Blog Configuration:")
    print(json.dumps(config, indent=2))
    
    show_curl_commands()
    
    print(f"\n{'=' * 50}")
    print("🎉 RESULT")
    print("=" * 50)
    print("With this configuration:")
    print("• No more contact page timeouts")
    print("• Fast, focused crawling")  
    print("• Only product and blog content")
    print("• RAG automation will work perfectly")
    print("• Much better content quality for RAG")
    
    test_targeted_crawling()
    
    return 0

if __name__ == "__main__":
    exit(main())
