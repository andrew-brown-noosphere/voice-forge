#!/usr/bin/env python3
"""
Debug script for testing Firecrawl issues with specific websites.
Run this to test different approaches before running the full crawler.
"""

import os
import logging
import requests
from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_direct_access(url: str):
    """Test direct HTTP access to the URL."""
    logger.info(f"🔍 Testing direct access to: {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        logger.info(f"   Status Code: {response.status_code}")
        logger.info(f"   Content Length: {len(response.content)}")
        logger.info(f"   Content Type: {response.headers.get('content-type', 'unknown')}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.title.string if soup.title else "No title"
            logger.info(f"   Page Title: {title}")
            
            # Check for common content areas
            main = soup.find('main')
            article = soup.find('article')
            content_div = soup.find('div', class_='content')
            
            if main:
                logger.info(f"   Found <main> tag with {len(main.get_text(strip=True))} chars")
            if article:
                logger.info(f"   Found <article> tag with {len(article.get_text(strip=True))} chars")
            if content_div:
                logger.info(f"   Found content div with {len(content_div.get_text(strip=True))} chars")
                
            # Check for bot detection indicators
            if "cloudflare" in response.text.lower():
                logger.warning("   ⚠️ Cloudflare detected")
            if "captcha" in response.text.lower():
                logger.warning("   ⚠️ CAPTCHA detected")
            if "rate limit" in response.text.lower():
                logger.warning("   ⚠️ Rate limiting detected")
                
            return True
        else:
            logger.error(f"   ❌ HTTP {response.status_code}: {response.reason}")
            return False
            
    except Exception as e:
        logger.error(f"   ❌ Request failed: {str(e)}")
        return False

def test_firecrawl_scrape(url: str):
    """Test Firecrawl single page scraping."""
    logger.info(f"🔥 Testing Firecrawl scrape of: {url}")
    
    api_key = os.getenv('FIRECRAWL_API_KEY')
    if not api_key:
        logger.error("   ❌ FIRECRAWL_API_KEY not set")
        return False
    
    try:
        from firecrawl import FirecrawlApp
        
        firecrawl = FirecrawlApp(api_key=api_key)
        
        result = firecrawl.scrape_url(
            url=url,
            params={
                "extractorOptions": {"mode": "markdown"},
                "includeHtml": True,
                "waitFor": 3000,
                "timeout": 30000
            }
        )
        
        if result and hasattr(result, 'content') and result.content:
            logger.info(f"   ✅ Scrape successful: {len(result.content)} chars")
            if hasattr(result, 'title') and result.title:
                logger.info(f"   Title: {result.title}")
            return True
        else:
            logger.error("   ❌ Scrape returned no content")
            logger.info(f"   Result type: {type(result)}")
            logger.info(f"   Result attributes: {dir(result) if result else 'None'}")
            return False
            
    except Exception as e:
        logger.error(f"   ❌ Firecrawl scrape failed: {str(e)}")
        return False

def test_firecrawl_crawl(url: str):
    """Test Firecrawl crawling."""
    logger.info(f"🕷️ Testing Firecrawl crawl of: {url}")
    
    api_key = os.getenv('FIRECRAWL_API_KEY')
    if not api_key:
        logger.error("   ❌ FIRECRAWL_API_KEY not set")
        return False
    
    try:
        from firecrawl import FirecrawlApp
        
        firecrawl = FirecrawlApp(api_key=api_key)
        
        crawl_options = {
            "crawlerOptions": {
                "maxDepth": 1,  # Very shallow for testing
                "limit": 5,     # Small limit for testing
                "allowBackwardCrawling": False,
                "allowExternalContentLinks": False,
                "excludePaths": [
                    ".*\\.pdf$", ".*\\.jpg$", ".*\\.png$", 
                    ".*\\.css$", ".*\\.js$"
                ]
            },
            "pageOptions": {
                "extractorOptions": {"mode": "markdown"},
                "includeHtml": True,
                "waitFor": 3000,
                "timeout": 30000
            }
        }
        
        result = firecrawl.crawl_url(url, params=crawl_options)
        
        logger.info(f"   Crawl completed")
        logger.info(f"   Success: {getattr(result, 'success', 'unknown')}")
        logger.info(f"   Status: {getattr(result, 'status', 'unknown')}")
        logger.info(f"   Total: {getattr(result, 'total', 0)}")
        logger.info(f"   Completed: {getattr(result, 'completed', 0)}")
        
        if hasattr(result, 'data') and result.data:
            logger.info(f"   ✅ Found {len(result.data)} pages")
            for i, page in enumerate(result.data[:3]):  # Show first 3
                page_url = getattr(page, 'url', 'no-url')
                logger.info(f"   Page {i+1}: {page_url}")
            return True
        else:
            logger.error("   ❌ No pages found")
            return False
            
    except Exception as e:
        logger.error(f"   ❌ Firecrawl crawl failed: {str(e)}")
        return False

def main():
    """Run debug tests for buf.build and similar sites."""
    
    # URLs to test
    test_urls = [
        "https://buf.build",
        "https://buf.build/docs",
        "https://docs.buf.build",
        "https://buf.build/blog"
    ]
    
    logger.info("🚀 Starting Firecrawl debug tests")
    logger.info("=" * 60)
    
    results = {}
    
    for url in test_urls:
        logger.info(f"\n📋 Testing: {url}")
        logger.info("-" * 40)
        
        # Test direct access
        direct_ok = test_direct_access(url)
        
        # Test Firecrawl scrape
        scrape_ok = test_firecrawl_scrape(url)
        
        # Test Firecrawl crawl (only if scrape works)
        crawl_ok = False
        if scrape_ok:
            crawl_ok = test_firecrawl_crawl(url)
        else:
            logger.info("🔥 Skipping crawl test (scrape failed)")
        
        results[url] = {
            'direct': direct_ok,
            'scrape': scrape_ok,
            'crawl': crawl_ok
        }
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 SUMMARY")
    logger.info("=" * 60)
    
    for url, result in results.items():
        status = "✅" if any(result.values()) else "❌"
        logger.info(f"{status} {url}")
        logger.info(f"   Direct: {'✅' if result['direct'] else '❌'}")
        logger.info(f"   Scrape: {'✅' if result['scrape'] else '❌'}")
        logger.info(f"   Crawl:  {'✅' if result['crawl'] else '❌'}")
    
    # Recommendations
    logger.info("\n🎯 RECOMMENDATIONS:")
    
    working_urls = [url for url, result in results.items() if any(result.values())]
    if working_urls:
        logger.info(f"✅ Try these URLs first: {working_urls}")
    
    scrape_working = [url for url, result in results.items() if result['scrape']]
    if scrape_working:
        logger.info(f"🔥 Firecrawl scrape works for: {scrape_working}")
    
    crawl_working = [url for url, result in results.items() if result['crawl']]
    if crawl_working:
        logger.info(f"🕷️ Firecrawl crawl works for: {crawl_working}")
    else:
        logger.info("❌ No URLs work with Firecrawl crawl - consider using scrape mode or direct HTTP")

if __name__ == "__main__":
    main()
