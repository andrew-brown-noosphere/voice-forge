#!/usr/bin/env python3
"""
Prioritized buf.build crawling strategy - targeting product pages and blogs for demo.
"""

import requests
import re
from urllib.parse import urljoin, urlparse

def find_product_and_blog_urls():
    """Find product pages and blog content on buf.build"""
    
    print("🎯 FINDING PRODUCT PAGES & BLOGS ON BUF.BUILD")
    print("=" * 60)
    
    # High-priority URLs to check for product/blog content
    priority_urls = [
        "https://buf.build",
        "https://buf.build/blog",
        "https://buf.build/product", 
        "https://buf.build/features",
        "https://buf.build/solutions",
        "https://buf.build/pricing",
        "https://buf.build/platform",
        "https://buf.build/use-cases",
        "https://blog.buf.build",  # Potential blog subdomain
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    found_urls = []
    product_urls = []
    blog_urls = []
    
    for url in priority_urls:
        print(f"\n📋 Checking: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ Accessible ({response.status_code})")
                found_urls.append(url)
                
                # Categorize by URL type
                if any(keyword in url.lower() for keyword in ['blog', 'news', 'article']):
                    blog_urls.append(url)
                    print("   📝 BLOG CONTENT")
                elif any(keyword in url.lower() for keyword in ['product', 'feature', 'solution', 'platform', 'pricing', 'use-case']):
                    product_urls.append(url)
                    print("   🏢 PRODUCT PAGE")
                else:
                    print("   🏠 HOMEPAGE/OTHER")
                
                # Extract title for context
                title_match = re.search(r'<title[^>]*>(.*?)</title>', response.text, re.IGNORECASE | re.DOTALL)
                if title_match:
                    title = title_match.group(1).strip()[:80]
                    print(f"   📄 Title: {title}")
                
            elif response.status_code == 404:
                print(f"   ❌ Not found (404)")
            else:
                print(f"   ⚠️ Status: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return found_urls, product_urls, blog_urls

def discover_additional_pages(base_urls):
    """Discover additional product/blog pages from the accessible pages"""
    
    print(f"\n🔍 DISCOVERING ADDITIONAL PAGES FROM {len(base_urls)} BASE URLS")
    print("=" * 60)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    discovered_urls = set()
    
    for base_url in base_urls:
        print(f"\n📖 Scanning: {base_url}")
        
        try:
            response = requests.get(base_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                content = response.text
                
                # Find all internal links
                link_pattern = r'href=["\']([^"\']+)["\']'
                links = re.findall(link_pattern, content)
                
                relevant_links = []
                
                for link in links:
                    # Convert relative URLs to absolute
                    if link.startswith('/'):
                        full_url = f"https://buf.build{link}"
                    elif link.startswith('http'):
                        full_url = link
                    else:
                        continue
                    
                    # Only include buf.build URLs
                    if 'buf.build' not in full_url:
                        continue
                    
                    # Prioritize product and blog URLs
                    if any(keyword in full_url.lower() for keyword in [
                        'product', 'feature', 'solution', 'platform', 'pricing',
                        'blog', 'news', 'article', 'post', 'announcement',
                        'use-case', 'case-study', 'customer', 'story'
                    ]):
                        relevant_links.append(full_url)
                        discovered_urls.add(full_url)
                
                if relevant_links:
                    print(f"   🎯 Found {len(relevant_links)} relevant links:")
                    for i, link in enumerate(relevant_links[:8]):  # Show first 8
                        link_type = "📝 BLOG" if any(kw in link.lower() for kw in ['blog', 'news', 'article', 'post']) else "🏢 PRODUCT"
                        print(f"      {link_type} {link}")
                    
                    if len(relevant_links) > 8:
                        print(f"      ... and {len(relevant_links) - 8} more")
                else:
                    print("   ⚠️ No relevant links found")
                    
        except Exception as e:
            print(f"   ❌ Error scanning {base_url}: {e}")
    
    return list(discovered_urls)

def check_sitemap_for_priority_content():
    """Check sitemap specifically for product and blog content"""
    
    print(f"\n🗺️ CHECKING SITEMAP FOR PRODUCT/BLOG CONTENT")
    print("=" * 60)
    
    sitemap_urls = [
        "https://buf.build/sitemap.xml",
        "https://blog.buf.build/sitemap.xml"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    priority_sitemap_urls = []
    
    for sitemap_url in sitemap_urls:
        print(f"\n📋 Checking: {sitemap_url}")
        
        try:
            response = requests.get(sitemap_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                content = response.text
                print(f"   ✅ Found sitemap ({len(content)} chars)")
                
                # Extract URLs from sitemap
                urls = re.findall(r'<loc>(.*?)</loc>', content)
                
                if urls:
                    # Filter for product and blog URLs
                    product_blog_urls = [
                        url for url in urls
                        if any(keyword in url.lower() for keyword in [
                            'product', 'feature', 'solution', 'platform', 'pricing',
                            'blog', 'news', 'article', 'post', 'announcement',
                            'use-case', 'case-study', 'customer'
                        ])
                    ]
                    
                    print(f"   📊 Total URLs in sitemap: {len(urls)}")
                    print(f"   🎯 Product/Blog URLs: {len(product_blog_urls)}")
                    
                    if product_blog_urls:
                        print("   💎 Priority URLs found:")
                        for i, url in enumerate(product_blog_urls[:10]):
                            url_type = "📝" if any(kw in url.lower() for kw in ['blog', 'news', 'article', 'post']) else "🏢"
                            print(f"      {url_type} {url}")
                        
                        if len(product_blog_urls) > 10:
                            print(f"      ... and {len(product_blog_urls) - 10} more")
                        
                        priority_sitemap_urls.extend(product_blog_urls)
                
            else:
                print(f"   ❌ Status: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return priority_sitemap_urls

def generate_optimized_crawl_strategy(product_urls, blog_urls, discovered_urls, sitemap_urls):
    """Generate the optimal crawling strategy prioritizing product and blog content"""
    
    print(f"\n🚀 OPTIMIZED CRAWL STRATEGY FOR BUF.BUILD DEMO")
    print("=" * 60)
    
    # Combine and deduplicate all URLs
    all_priority_urls = set()
    all_priority_urls.update(product_urls)
    all_priority_urls.update(blog_urls) 
    all_priority_urls.update(discovered_urls)
    all_priority_urls.update(sitemap_urls)
    
    # Categorize final URLs
    final_product_urls = [url for url in all_priority_urls if any(kw in url.lower() for kw in ['product', 'feature', 'solution', 'platform', 'pricing', 'use-case', 'customer'])]
    final_blog_urls = [url for url in all_priority_urls if any(kw in url.lower() for kw in ['blog', 'news', 'article', 'post', 'announcement'])]
    
    print(f"📊 DISCOVERED CONTENT:")
    print(f"   🏢 Product pages: {len(final_product_urls)}")
    print(f"   📝 Blog/News pages: {len(final_blog_urls)}")
    print(f"   📄 Total priority URLs: {len(all_priority_urls)}")
    
    # Generate crawl configurations
    strategies = [
        {
            "name": "Product-First Strategy",
            "description": "Focus on product pages for feature/solution content",
            "urls": final_product_urls[:20],  # Top 20 product URLs
            "settings": {
                "max_pages": 25,
                "max_depth": 2,
                "delay": 2000
            }
        },
        {
            "name": "Blog-First Strategy", 
            "description": "Focus on blog content for thought leadership",
            "urls": final_blog_urls[:20],  # Top 20 blog URLs
            "settings": {
                "max_pages": 25,
                "max_depth": 2,
                "delay": 2000
            }
        },
        {
            "name": "Combined Strategy",
            "description": "Mix of product and blog content",
            "urls": (final_product_urls[:15] + final_blog_urls[:15]),
            "settings": {
                "max_pages": 50,
                "max_depth": 3,
                "delay": 2500
            }
        }
    ]
    
    for strategy in strategies:
        print(f"\n🎯 {strategy['name']}")
        print(f"   Description: {strategy['description']}")
        print(f"   URLs to crawl: {len(strategy['urls'])}")
        print(f"   Settings: {strategy['settings']}")
        print(f"   Sample URLs:")
        
        for i, url in enumerate(strategy['urls'][:5]):
            url_type = "📝" if any(kw in url.lower() for kw in ['blog', 'news', 'article']) else "🏢"
            print(f"      {url_type} {url}")
        
        if len(strategy['urls']) > 5:
            print(f"      ... and {len(strategy['urls']) - 5} more")
    
    return all_priority_urls

def main():
    print("🎬 BUF.BUILD DEMO - PRODUCT & BLOG PRIORITIZATION")
    print("Finding the best content for your demonstration")
    print("=" * 60)
    
    # Step 1: Find direct product/blog URLs
    found_urls, product_urls, blog_urls = find_product_and_blog_urls()
    
    # Step 2: Discover additional pages
    discovered_urls = discover_additional_pages(found_urls)
    
    # Step 3: Check sitemap for priority content
    sitemap_urls = check_sitemap_for_priority_content()
    
    # Step 4: Generate optimal strategy
    all_urls = generate_optimized_crawl_strategy(product_urls, blog_urls, discovered_urls, sitemap_urls)
    
    print(f"\n💡 DEMO RECOMMENDATIONS:")
    print(f"   1. Use 'Combined Strategy' for best demo variety")
    print(f"   2. Expected result: 20-40 pages of high-value content")
    print(f"   3. Focus on product features + thought leadership")
    print(f"   4. Perfect for showcasing business content extraction")

if __name__ == "__main__":
    main()
