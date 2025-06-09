#!/usr/bin/env python3
"""
Discover buf.build's specific product pages like /product/bufstream
"""

import requests
import re
from urllib.parse import urljoin

def discover_buf_products():
    """Discover specific buf.build product pages like /product/bufstream"""
    
    print("🔍 DISCOVERING BUF.BUILD SPECIFIC PRODUCTS")
    print("=" * 60)
    
    # Known/potential product names based on buf.build's offerings
    potential_products = [
        "bufstream",    # Known product
        "buf-cli",      # CLI tool
        "buf-lint",     # Linting
        "buf-breaking", # Breaking change detection
        "buf-generate", # Code generation
        "buf-registry", # Schema registry
        "buf-push",     # Publishing
        "buf-build",    # Build system
        "buf-mod",      # Module management
        "buf-format",   # Formatting
        "buf-ls",       # Listing
        "buf-export",   # Export functionality
        "bsr",          # Buf Schema Registry
        "protobuf",     # Protocol buffers
        "grpc",         # gRPC related
        "connect",      # Connect protocol
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    found_products = []
    
    # Test each potential product page
    for product in potential_products:
        url = f"https://buf.build/product/{product}"
        print(f"\n📋 Testing: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ FOUND! Product page exists")
                found_products.append(url)
                
                # Extract title and description
                title_match = re.search(r'<title[^>]*>(.*?)</title>', response.text, re.IGNORECASE | re.DOTALL)
                if title_match:
                    title = title_match.group(1).strip()
                    print(f"   📄 Title: {title}")
                
                # Look for product description
                desc_patterns = [
                    r'<meta name="description" content="([^"]+)"',
                    r'<meta property="og:description" content="([^"]+)"'
                ]
                
                for pattern in desc_patterns:
                    desc_match = re.search(pattern, response.text, re.IGNORECASE)
                    if desc_match:
                        description = desc_match.group(1).strip()
                        print(f"   📝 Description: {description[:100]}...")
                        break
                
            elif response.status_code == 404:
                print(f"   ❌ Not found")
            else:
                print(f"   ⚠️ Status: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return found_products

def discover_from_main_product_page():
    """Discover product links from the main /product page"""
    
    print(f"\n🔍 SCANNING MAIN PRODUCT PAGE FOR LINKS")
    print("=" * 60)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    discovered_products = []
    
    try:
        response = requests.get("https://buf.build/product", headers=headers, timeout=10)
        
        if response.status_code == 200:
            content = response.text
            print("✅ Main product page accessible")
            
            # Find all links to /product/* pages
            product_links = re.findall(r'href=["\']([^"\']*\/product\/[^"\']*)["\']', content)
            
            # Clean and deduplicate links
            unique_links = set()
            for link in product_links:
                if link.startswith('/'):
                    full_url = f"https://buf.build{link}"
                elif link.startswith('http'):
                    full_url = link
                else:
                    continue
                
                # Only include actual product pages (not just /product)
                if '/product/' in full_url and full_url != "https://buf.build/product":
                    unique_links.add(full_url)
            
            discovered_products = list(unique_links)
            
            print(f"🎯 Found {len(discovered_products)} product links:")
            for i, link in enumerate(discovered_products):
                print(f"   {i+1}. {link}")
            
            # Also look for product names in text content
            print(f"\n🔍 Looking for product mentions in content...")
            
            # Common patterns for product names
            product_patterns = [
                r'buf\.build/([a-zA-Z-]+)',
                r'/product/([a-zA-Z-]+)',
                r'buf-([a-zA-Z-]+)',
                r'Buf ([A-Z][a-zA-Z]+)'
            ]
            
            mentioned_products = set()
            for pattern in product_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                mentioned_products.update(matches)
            
            if mentioned_products:
                print(f"📝 Product names mentioned: {', '.join(mentioned_products)}")
            
        else:
            print(f"❌ Main product page status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error scanning main product page: {e}")
    
    return discovered_products

def check_additional_buf_urls():
    """Check additional buf.build URL patterns"""
    
    print(f"\n🔍 CHECKING ADDITIONAL BUF.BUILD PATTERNS")
    print("=" * 60)
    
    additional_urls = [
        "https://buf.build/products",      # Plural form
        "https://buf.build/solutions",     # Solutions page
        "https://buf.build/tools",         # Tools page
        "https://buf.build/platform",      # Platform page
        "https://buf.build/features",      # Features page
        "https://buf.build/docs/bsr",      # BSR documentation
        "https://buf.build/studio",        # Buf Studio
        "https://buf.build/registry",      # Registry
        "https://buf.build/cli",           # CLI page
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    accessible_urls = []
    
    for url in additional_urls:
        print(f"\n📋 Testing: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ Accessible")
                accessible_urls.append(url)
                
                # Extract title
                title_match = re.search(r'<title[^>]*>(.*?)</title>', response.text, re.IGNORECASE | re.DOTALL)
                if title_match:
                    title = title_match.group(1).strip()
                    print(f"   📄 Title: {title}")
                
            else:
                print(f"   ❌ Status: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return accessible_urls

def generate_optimized_crawl_targets(found_products, discovered_products, additional_urls):
    """Generate optimal crawl targets based on discovered URLs"""
    
    print(f"\n🎯 OPTIMIZED CRAWL STRATEGY")
    print("=" * 60)
    
    # Combine all discovered URLs
    all_urls = set()
    all_urls.update(found_products)
    all_urls.update(discovered_products)
    all_urls.update(additional_urls)
    
    # Categorize URLs
    product_specific = [url for url in all_urls if '/product/' in url]
    platform_pages = [url for url in all_urls if any(kw in url for kw in ['platform', 'solutions', 'features'])]
    tool_pages = [url for url in all_urls if any(kw in url for kw in ['cli', 'tools', 'studio', 'registry'])]
    
    print(f"📊 DISCOVERED CONTENT:")
    print(f"   🏢 Specific product pages: {len(product_specific)}")
    print(f"   🚀 Platform/solutions: {len(platform_pages)}")
    print(f"   🔧 Tools/CLI: {len(tool_pages)}")
    print(f"   📄 Total URLs: {len(all_urls)}")
    
    # Generate crawl strategies
    strategies = [
        {
            "name": "Product Deep-Dive Demo",
            "description": "Focus on specific buf.build products",
            "urls": product_specific,
            "settings": {
                "max_pages": 30,
                "max_depth": 2,
                "delay": 2000
            },
            "demo_value": "Show detailed product feature extraction"
        },
        {
            "name": "Platform Overview Demo", 
            "description": "Broad platform and solutions content",
            "urls": platform_pages + tool_pages,
            "settings": {
                "max_pages": 25,
                "max_depth": 2,
                "delay": 2000
            },
            "demo_value": "Show comprehensive platform understanding"
        },
        {
            "name": "Complete buf.build Demo",
            "description": "All discovered high-value pages",
            "urls": list(all_urls),
            "settings": {
                "max_pages": 50,
                "max_depth": 3,
                "delay": 2500
            },
            "demo_value": "Maximum content variety and depth"
        }
    ]
    
    for strategy in strategies:
        print(f"\n🎛️ {strategy['name']}")
        print(f"   Description: {strategy['description']}")
        print(f"   URLs: {len(strategy['urls'])}")
        print(f"   Settings: {strategy['settings']}")
        print(f"   Demo value: {strategy['demo_value']}")
        print(f"   Sample URLs:")
        
        for i, url in enumerate(strategy['urls'][:5]):
            print(f"      {i+1}. {url}")
        
        if len(strategy['urls']) > 5:
            print(f"      ... and {len(strategy['urls']) - 5} more")
    
    return list(all_urls)

def main():
    print("🎯 BUF.BUILD SPECIFIC PRODUCT DISCOVERY")
    print("Finding product pages like /product/bufstream for optimal demo")
    print("=" * 60)
    
    # Step 1: Test known/potential products
    found_products = discover_buf_products()
    
    # Step 2: Scan main product page for links
    discovered_products = discover_from_main_product_page()
    
    # Step 3: Check additional URL patterns
    additional_urls = check_additional_buf_urls()
    
    # Step 4: Generate optimal strategy
    all_urls = generate_optimized_crawl_targets(found_products, discovered_products, additional_urls)
    
    print(f"\n💡 DEMO RECOMMENDATIONS:")
    if len(found_products) > 0:
        print(f"   ✅ Found specific product pages! Use 'Product Deep-Dive Demo'")
        print(f"   🎯 Start with: {found_products[0] if found_products else 'https://buf.build/product'}")
        print(f"   📈 Expected: 15-30 high-quality product pages")
    else:
        print(f"   📋 No specific products found, use platform strategy")
        print(f"   🎯 Start with: https://buf.build/platform")
        print(f"   📈 Expected: 10-20 platform overview pages")
    
    print(f"\n🚀 QUICK START:")
    print(f"   1. Use the discovered URLs as your crawl targets")
    print(f"   2. Focus on specific product features and capabilities")  
    print(f"   3. Great demo content for enterprise sales!")

if __name__ == "__main__":
    main()
