#!/usr/bin/env python3
"""
Optimize buf.build crawling for demo purposes.
Get maximum pages from buf.build despite bot protection.
"""

import logging
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_buf_build_structure():
    """Analyze buf.build to find the best crawling strategy."""
    
    logger.info("🔍 ANALYZING BUF.BUILD FOR OPTIMAL CRAWLING")
    logger.info("=" * 60)
    
    urls_to_analyze = [
        "https://buf.build",
        "https://buf.build/docs",
        "https://docs.buf.build", 
        "https://buf.build/blog",
        "https://buf.build/product",
        "https://buf.build/pricing"
    ]
    
    results = {}
    
    for url in urls_to_analyze:
        logger.info(f"\n📋 Analyzing: {url}")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find all internal links
                links = soup.find_all('a', href=True)
                internal_links = []
                
                for link in links:
                    href = link.get('href')
                    if href:
                        # Normalize the href
                        if href.startswith('/'):
                            full_url = f"https://buf.build{href}"
                            internal_links.append(full_url)
                        elif 'buf.build' in href:
                            internal_links.append(href)
                
                # Remove duplicates and filter out unwanted paths
                unique_links = list(set(internal_links))
                filtered_links = [
                    link for link in unique_links 
                    if not any(exclude in link.lower() for exclude in [
                        'mailto:', 'tel:', 'javascript:', '#',
                        '.pdf', '.jpg', '.png', '.gif', '.css', '.js'
                    ])
                ]
                
                results[url] = {
                    'status': response.status_code,
                    'title': soup.title.string if soup.title else 'No title',
                    'total_links': len(links),
                    'internal_links': len(unique_links),
                    'crawlable_links': len(filtered_links),
                    'sample_links': filtered_links[:10]
                }
                
                logger.info(f"   ✅ Status: {response.status_code}")
                logger.info(f"   📄 Title: {results[url]['title']}")
                logger.info(f"   🔗 Total links: {results[url]['total_links']}")
                logger.info(f"   🏠 Internal links: {results[url]['internal_links']}")
                logger.info(f"   🎯 Crawlable links: {results[url]['crawlable_links']}")
                
            else:
                logger.info(f"   ❌ Status: {response.status_code}")
                results[url] = {'status': response.status_code, 'error': True}
                
        except Exception as e:
            logger.info(f"   ❌ Error: {str(e)}")
            results[url] = {'error': str(e)}
    
    return results

def recommend_optimal_strategy(analysis_results):
    """Recommend the best crawling strategy based on analysis."""
    
    logger.info("\n🎯 OPTIMAL CRAWLING STRATEGY FOR BUF.BUILD")
    logger.info("=" * 60)
    
    # Find the URL with most crawlable links
    best_entry_point = None
    max_links = 0
    
    for url, data in analysis_results.items():
        if not data.get('error') and data.get('crawlable_links', 0) > max_links:
            max_links = data['crawlable_links']
            best_entry_point = url
    
    if best_entry_point:
        logger.info(f"🏆 BEST ENTRY POINT: {best_entry_point}")
        logger.info(f"   Discoverable pages: {analysis_results[best_entry_point]['crawlable_links']}")
        logger.info(f"   Sample URLs found:")
        for link in analysis_results[best_entry_point]['sample_links']:
            logger.info(f"     • {link}")
    
    # Strategy recommendations
    strategies = [
        {
            "name": "Multi-Entry Point Strategy",
            "description": "Crawl multiple starting points separately",
            "implementation": [
                "Crawl docs.buf.build (if accessible)",
                "Crawl buf.build/docs", 
                "Crawl buf.build/blog",
                "Combine results for total page count"
            ],
            "expected_pages": "10-30 pages"
        },
        {
            "name": "Enhanced Fallback Strategy", 
            "description": "Improve the HTTP fallback to discover more links",
            "implementation": [
                "Extract all internal links from homepage",
                "Crawl each discovered link individually",
                "Use delays to avoid rate limiting"
            ],
            "expected_pages": "5-15 pages"
        },
        {
            "name": "Sitemap Strategy",
            "description": "Check for sitemap.xml or robots.txt",
            "implementation": [
                "Check buf.build/sitemap.xml",
                "Check buf.build/robots.txt", 
                "Extract URLs from sitemap if available"
            ],
            "expected_pages": "20-50 pages (if sitemap exists)"
        }
    ]
    
    for strategy in strategies:
        logger.info(f"\n🔧 {strategy['name']}")
        logger.info(f"   Description: {strategy['description']}")
        logger.info(f"   Expected pages: {strategy['expected_pages']}")
        logger.info("   Implementation:")
        for step in strategy['implementation']:
            logger.info(f"     • {step}")

def check_sitemap_and_robots():
    """Check if buf.build has sitemap or robots.txt with URLs."""
    
    logger.info("\n🗺️ CHECKING SITEMAP AND ROBOTS.TXT")
    logger.info("=" * 60)
    
    urls_to_check = [
        "https://buf.build/sitemap.xml",
        "https://buf.build/robots.txt",
        "https://buf.build/sitemap_index.xml"
    ]
    
    for url in urls_to_check:
        logger.info(f"\n📋 Checking: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                content = response.text
                logger.info(f"   ✅ Found! Size: {len(content)} characters")
                
                # Extract URLs from content
                if 'sitemap' in url.lower():
                    # Look for URLs in sitemap
                    import re
                    urls = re.findall(r'<loc>(.*?)</loc>', content)
                    if urls:
                        logger.info(f"   🎯 Found {len(urls)} URLs in sitemap:")
                        for i, found_url in enumerate(urls[:10]):
                            logger.info(f"     {i+1}. {found_url}")
                        if len(urls) > 10:
                            logger.info(f"     ... and {len(urls) - 10} more")
                    else:
                        logger.info("   ⚠️ No URLs found in sitemap format")
                
                elif 'robots' in url.lower():
                    # Look for sitemap references in robots.txt
                    lines = content.split('\n')
                    sitemap_refs = [line for line in lines if 'sitemap:' in line.lower()]
                    if sitemap_refs:
                        logger.info("   🗺️ Sitemap references found:")
                        for ref in sitemap_refs:
                            logger.info(f"     • {ref.strip()}")
                    else:
                        logger.info("   ℹ️ No sitemap references in robots.txt")
                        
            else:
                logger.info(f"   ❌ Status: {response.status_code}")
                
        except Exception as e:
            logger.info(f"   ❌ Error: {str(e)}")

def generate_enhanced_crawler_config():
    """Generate optimized crawler configuration for buf.build demo."""
    
    logger.info("\n⚙️ ENHANCED CRAWLER CONFIGURATION")
    logger.info("=" * 60)
    
    configs = [
        {
            "name": "Maximum Discovery Config",
            "settings": {
                "max_pages": 50,
                "max_depth": 4,  # Go deeper
                "delay": 2000,   # Slower to avoid blocks
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "timeout": 60000,  # Longer timeout
                "wait_for": 5000   # Wait for JS to load
            },
            "target_urls": [
                "https://docs.buf.build",
                "https://buf.build/docs", 
                "https://buf.build"
            ],
            "strategy": "Try each URL separately, combine results"
        },
        {
            "name": "Stealth Demo Config",
            "settings": {
                "max_pages": 30,
                "max_depth": 3,
                "delay": 3000,   # Very slow, human-like
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "exclude_patterns": [".*\\.pdf$", ".*\\.(jpg|png|gif)$", ".*\\.css$"],  # Minimal excludes
                "include_fragments": True  # Don't exclude fragment URLs
            },
            "target_urls": ["https://buf.build"],
            "strategy": "Single entry point, maximum stealth"
        }
    ]
    
    for config in configs:
        logger.info(f"\n🎛️ {config['name']}")
        logger.info(f"   Strategy: {config['strategy']}")
        logger.info("   Settings:")
        for key, value in config['settings'].items():
            logger.info(f"     {key}: {value}")
        logger.info("   Target URLs:")
        for url in config['target_urls']:
            logger.info(f"     • {url}")

def demo_preparation_checklist():
    """Checklist for preparing the buf.build demo."""
    
    logger.info("\n✅ DEMO PREPARATION CHECKLIST")
    logger.info("=" * 60)
    
    checklist = [
        "Test crawler with docs.buf.build (subdomain)",
        "Test crawler with buf.build/docs (path)",
        "Increase max_depth to 4",
        "Set delay to 2-3 seconds between requests",
        "Use realistic browser User-Agent",
        "Have backup talking points if only 1-5 pages crawled",
        "Test the enhanced fallback crawler",
        "Check if sitemap.xml provides more URLs",
        "Prepare multi-entry-point strategy (crawl 3 URLs separately)"
    ]
    
    for i, item in enumerate(checklist, 1):
        logger.info(f"{i:2d}. {item}")
    
    logger.info("\n💡 DEMO TALKING POINTS IF LOW PAGE COUNT:")
    talking_points = [
        "buf.build has aggressive bot protection (shows the challenge)",
        "In production, customer whitelists our crawler = full access",
        "This demonstrates the fallback capability when sites are protected",
        "Real customer sites don't have these restrictions",
        "Quality of extraction is more important than quantity for demo"
    ]
    
    for point in talking_points:
        logger.info(f"   • {point}")

if __name__ == "__main__":
    logger.info("🎬 BUF.BUILD DEMO OPTIMIZATION")
    logger.info("Maximizing crawl results for your buf.build demonstration")
    
    # Analyze the site structure
    analysis = analyze_buf_build_structure()
    
    # Recommend optimal strategy
    recommend_optimal_strategy(analysis)
    
    # Check for sitemaps
    check_sitemap_and_robots()
    
    # Generate configurations
    generate_enhanced_crawler_config()
    
    # Preparation checklist
    demo_preparation_checklist()
    
    logger.info("\n" + "=" * 60)
    logger.info("🎯 RECOMMENDED DEMO APPROACH:")
    logger.info("1. Try docs.buf.build first (likely to get 10-20 pages)")
    logger.info("2. If that fails, use buf.build with max_depth=4, delay=3000ms")
    logger.info("3. Have talking points ready about production whitelisting")
    logger.info("4. Emphasize content quality over quantity")
