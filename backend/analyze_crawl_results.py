#!/usr/bin/env python3
"""
Analyze and optimize crawl configuration for better page discovery.
"""

import os
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_crawl_results():
    """Analyze why only 1 page was crawled instead of 50."""
    
    logger.info("🔍 Analyzing crawl results: 1 page vs 50 requested")
    logger.info("=" * 60)
    
    # Possible reasons for low page count
    reasons = [
        {
            "reason": "Fallback HTTP Scraping",
            "description": "If Firecrawl failed and fallback HTTP scraping was used, it only scrapes the single page",
            "indicator": "Look for '📦 Processing fallback content' in logs",
            "solution": "Configure Firecrawl to work properly, or enhance fallback to discover links"
        },
        {
            "reason": "Site Structure",
            "description": "buf.build might not have many discoverable internal links from the homepage",
            "indicator": "Check if buf.build homepage has navigation links to other pages",
            "solution": "Start crawl from a different URL like /docs or /blog"
        },
        {
            "reason": "Crawler Configuration",
            "description": "maxDepth might be set too low, or excludePaths too restrictive",
            "indicator": "Check config.max_depth and exclude patterns",
            "solution": "Increase maxDepth and reduce exclude patterns"
        },
        {
            "reason": "Bot Protection",
            "description": "buf.build might be blocking the crawler after the first page",
            "indicator": "Subsequent pages return 403/429 or block responses", 
            "solution": "Use stealth techniques or different user agents"
        },
        {
            "reason": "JavaScript Navigation",
            "description": "buf.build might use JavaScript for navigation that crawlers can't follow",
            "indicator": "Manual inspection of buf.build shows JS-only navigation",
            "solution": "Use Firecrawl with longer wait times or different extraction modes"
        }
    ]
    
    for i, reason in enumerate(reasons, 1):
        logger.info(f"\n{i}. {reason['reason']}")
        logger.info(f"   Description: {reason['description']}")
        logger.info(f"   Check: {reason['indicator']}")
        logger.info(f"   Solution: {reason['solution']}")
    
    logger.info("\n" + "=" * 60)
    logger.info("🎯 RECOMMENDED ACTIONS:")
    
    actions = [
        "1. Check the crawl logs for 'fallback content' messages",
        "2. Try crawling buf.build/docs instead of buf.build",
        "3. Increase maxDepth in crawl configuration",
        "4. Test Firecrawl API directly to see if it can discover multiple pages",
        "5. Manually inspect buf.build to see how pages are linked"
    ]
    
    for action in actions:
        logger.info(f"   {action}")

def suggest_optimized_configs():
    """Suggest different crawl configurations for better results."""
    
    logger.info("\n🚀 OPTIMIZED CRAWL CONFIGURATIONS")
    logger.info("=" * 60)
    
    configs = [
        {
            "name": "Documentation-Focused",
            "url": "https://docs.buf.build",
            "max_pages": 50,
            "max_depth": 3,
            "description": "Start from docs subdomain for better content discovery"
        },
        {
            "name": "Multi-Entry Point",
            "urls": [
                "https://buf.build/docs",
                "https://buf.build/blog", 
                "https://buf.build/community"
            ],
            "max_pages": 20,
            "max_depth": 2,
            "description": "Crawl multiple sections separately"
        },
        {
            "name": "Deep Documentation",
            "url": "https://buf.build/docs",
            "max_pages": 100,
            "max_depth": 4,
            "description": "Deep crawl of documentation section"
        },
        {
            "name": "Stealth Configuration",
            "url": "https://buf.build",
            "max_pages": 50,
            "max_depth": 3,
            "special_options": {
                "delay": 2000,
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
                "wait_for": 5000
            },
            "description": "Slower crawl with stealth techniques"
        }
    ]
    
    for i, config in enumerate(configs, 1):
        logger.info(f"\n{i}. {config['name']}")
        logger.info(f"   Description: {config['description']}")
        if 'url' in config:
            logger.info(f"   URL: {config['url']}")
        if 'urls' in config:
            logger.info(f"   URLs: {', '.join(config['urls'])}")
        logger.info(f"   Max Pages: {config.get('max_pages', 'N/A')}")
        logger.info(f"   Max Depth: {config.get('max_depth', 'N/A')}")
        if 'special_options' in config:
            logger.info(f"   Special Options: {config['special_options']}")

def check_buf_build_structure():
    """Check buf.build structure to understand crawling opportunities."""
    
    logger.info("\n🔍 ANALYZING BUF.BUILD STRUCTURE")
    logger.info("=" * 60)
    
    try:
        import requests
        from bs4 import BeautifulSoup
        
        urls_to_check = [
            "https://buf.build",
            "https://buf.build/docs", 
            "https://docs.buf.build",
            "https://buf.build/blog"
        ]
        
        for url in urls_to_check:
            logger.info(f"\n📋 Checking: {url}")
            
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Count different types of links
                    all_links = soup.find_all('a', href=True)
                    internal_links = [link for link in all_links if 'buf.build' in str(link.get('href', '')) or link.get('href', '').startswith('/')]
                    external_links = [link for link in all_links if link.get('href', '').startswith('http') and 'buf.build' not in str(link.get('href', ''))]
                    
                    logger.info(f"   ✅ Status: {response.status_code}")
                    logger.info(f"   📄 Title: {soup.title.string if soup.title else 'No title'}")
                    logger.info(f"   🔗 Total links: {len(all_links)}")
                    logger.info(f"   🏠 Internal links: {len(internal_links)}")
                    logger.info(f"   🌐 External links: {len(external_links)}")
                    
                    # Sample internal links
                    if internal_links:
                        sample_links = [link.get('href') for link in internal_links[:5]]
                        logger.info(f"   📝 Sample internal links: {sample_links}")
                    
                else:
                    logger.info(f"   ❌ Status: {response.status_code}")
                    
            except Exception as e:
                logger.info(f"   ❌ Error: {str(e)}")
    
    except ImportError:
        logger.info("   ⚠️ requests/BeautifulSoup not available for structure analysis")

def generate_test_commands():
    """Generate commands to test different crawl configurations."""
    
    logger.info("\n🧪 TEST COMMANDS")
    logger.info("=" * 60)
    
    commands = [
        {
            "description": "Test Firecrawl API directly",
            "command": "python test_firecrawl_api_formats.py"
        },
        {
            "description": "Test docs.buf.build (subdomain)",
            "note": "Change domain in your crawler UI to: docs.buf.build"
        },
        {
            "description": "Test buf.build/docs (path)",
            "note": "Change domain in your crawler UI to: buf.build/docs"
        },
        {
            "description": "Increase max_depth",
            "note": "Set max_depth to 4 or 5 in crawler configuration"
        },
        {
            "description": "Check current crawl logs",
            "command": "tail -f logs/crawler.log | grep -E '(fallback|Success|Failed|pages)'"
        }
    ]
    
    for i, cmd in enumerate(commands, 1):
        logger.info(f"\n{i}. {cmd['description']}")
        if 'command' in cmd:
            logger.info(f"   Command: {cmd['command']}")
        if 'note' in cmd:
            logger.info(f"   Action: {cmd['note']}")

if __name__ == "__main__":
    logger.info("🔍 Crawl Results Analysis")
    logger.info("Results: 1 page crawled out of 50 requested")
    
    analyze_crawl_results()
    suggest_optimized_configs() 
    check_buf_build_structure()
    generate_test_commands()
    
    logger.info("\n" + "=" * 60)
    logger.info("💡 QUICK WIN: Try crawling 'docs.buf.build' instead of 'buf.build'")
    logger.info("This subdomain likely has more discoverable internal links.")
