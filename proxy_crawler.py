#!/usr/bin/env python3
"""
Proxy-enabled crawler implementation to bypass IP bans.
"""
import sys
import os
import random
import itertools
import logging
import time
sys.path.append('/Users/andrewbrown/Sites/noosphere/github/voice-forge/backend')

from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

class ProxyRotator:
    """Manages proxy rotation for the crawler."""
    
    def __init__(self, proxies=None):
        """Initialize with list of proxy URLs."""
        self.proxies = proxies or self.get_free_proxies()
        self.proxy_cycle = itertools.cycle(self.proxies) if self.proxies else None
        self.failed_proxies = set()
        
    def get_free_proxies(self):
        """Get list of free proxy servers (replace with your preferred service)."""
        # Note: Free proxies are unreliable. For production, use paid services.
        return [
            # Add your proxy servers here
            # "http://proxy1.example.com:8080",
            # "http://proxy2.example.com:8080",
        ]
    
    def get_next_proxy(self):
        """Get next working proxy from the rotation."""
        if not self.proxy_cycle:
            return None
            
        for _ in range(len(self.proxies)):
            proxy = next(self.proxy_cycle)
            if proxy not in self.failed_proxies:
                return proxy
        
        # All proxies failed, reset and try again
        self.failed_proxies.clear()
        return next(self.proxy_cycle) if self.proxy_cycle else None
    
    def mark_proxy_failed(self, proxy):
        """Mark a proxy as failed."""
        if proxy:
            self.failed_proxies.add(proxy)
            logger.warning(f"Marked proxy as failed: {proxy}")

class ProxyEnabledCrawler:
    """Crawler with proxy rotation to bypass IP bans."""
    
    def __init__(self, proxies=None):
        self.proxy_rotator = ProxyRotator(proxies)
        self.visited_urls = set()
        self.failed_urls = set()
        
    def test_proxy(self, proxy):
        """Test if a proxy is working."""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    proxy={"server": proxy} if proxy else None
                )
                page = browser.new_page()
                
                # Test with a simple site first
                response = page.goto("https://httpbin.org/ip", timeout=15000)
                
                if response.status == 200:
                    content = page.content()
                    browser.close()
                    return True
                else:
                    browser.close()
                    return False
                    
        except Exception as e:
            logger.error(f"Proxy test failed for {proxy}: {str(e)}")
            return False
    
    def crawl_with_proxy_rotation(self, urls):
        """Crawl URLs using proxy rotation."""
        results = []
        
        for url in urls:
            success = False
            attempts = 0
            max_attempts = 3
            
            while not success and attempts < max_attempts:
                current_proxy = self.proxy_rotator.get_next_proxy()
                attempts += 1
                
                logger.info(f"Attempt {attempts} for {url} using proxy: {current_proxy or 'Direct'}")
                
                try:
                    result = self.crawl_single_url(url, current_proxy)
                    if result:
                        results.append(result)
                        success = True
                        logger.info(f"✅ Successfully crawled {url}")
                    else:
                        self.proxy_rotator.mark_proxy_failed(current_proxy)
                        
                except Exception as e:
                    logger.error(f"❌ Failed to crawl {url} with proxy {current_proxy}: {str(e)}")
                    self.proxy_rotator.mark_proxy_failed(current_proxy)
                
                # Delay between attempts
                if not success and attempts < max_attempts:
                    delay = random.uniform(5, 15)
                    logger.info(f"Waiting {delay:.1f}s before retry...")
                    time.sleep(delay)
            
            if not success:
                logger.error(f"❌ Failed to crawl {url} after {max_attempts} attempts")
                self.failed_urls.add(url)
            
            # Delay between URLs
            time.sleep(random.uniform(2, 8))
        
        return results
    
    def crawl_single_url(self, url, proxy=None):
        """Crawl a single URL with optional proxy."""
        try:
            with sync_playwright() as p:
                # Browser arguments for stealth
                browser_args = [
                    "--no-first-run",
                    "--no-default-browser-check",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-features=TranslateUI",
                    "--disable-extensions"
                ]
                
                # Launch with or without proxy
                browser_config = {
                    "headless": True,
                    "args": browser_args
                }
                
                if proxy:
                    browser_config["proxy"] = {"server": proxy}
                
                browser = p.chromium.launch(**browser_config)
                
                context = browser.new_context(
                    viewport={'width': 1366, 'height': 768},
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                
                page = context.new_page()
                
                # Set realistic headers
                page.set_extra_http_headers({
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate, br",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1"
                })
                
                # Hide automation
                page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    delete window.__playwright;
                """)
                
                # Navigate with timeout
                response = page.goto(url, wait_until='networkidle', timeout=30000)
                
                if response.status >= 400:
                    logger.warning(f"HTTP {response.status} for {url}")
                    browser.close()
                    return None
                
                # Get content
                html = page.content()
                
                # Check for Cloudflare protection
                if "cloudflare" in html.lower() or "checking your browser" in html.lower():
                    logger.warning(f"Cloudflare protection detected for {url}")
                    browser.close()
                    return None
                
                # Success!
                result = {
                    "url": url,
                    "status": response.status,
                    "content_length": len(html),
                    "proxy_used": proxy,
                    "title": self.extract_title(html)
                }
                
                browser.close()
                return result
                
        except Exception as e:
            logger.error(f"Error crawling {url}: {str(e)}")
            return None
    
    def extract_title(self, html):
        """Extract page title from HTML."""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            title_tag = soup.find('title')
            return title_tag.text.strip() if title_tag else "No title"
        except:
            return "Title extraction failed"

def test_buf_build_with_proxies():
    """Test crawling buf.build with proxy rotation."""
    
    print("🚀 TESTING BUF.BUILD WITH PROXY ROTATION")
    print("=" * 50)
    
    # URLs to test
    test_urls = [
        "https://buf.build",
        "https://docs.buf.build"
    ]
    
    # Initialize crawler (add your proxies here)
    proxies = [
        # Add your proxy servers here
        # "http://proxy1.example.com:8080",
        # "http://username:password@proxy2.example.com:8080",
    ]
    
    if not proxies:
        print("⚠️  No proxies configured. Testing direct connection only.")
        proxies = [None]  # Direct connection
    
    crawler = ProxyEnabledCrawler(proxies)
    
    # Test crawling
    results = crawler.crawl_with_proxy_rotation(test_urls)
    
    print(f"\n📊 RESULTS:")
    print(f"  Successful: {len(results)}")
    print(f"  Failed: {len(crawler.failed_urls)}")
    
    for result in results:
        print(f"  ✅ {result['url']} - {result['title'][:50]}...")
    
    for failed_url in crawler.failed_urls:
        print(f"  ❌ {failed_url}")

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    test_buf_build_with_proxies()
    
    print(f"\n💡 TO USE PROXIES:")
    print("1. Get proxy servers from services like:")
    print("   - Bright Data (residential proxies)")
    print("   - SmartProxy")
    print("   - ProxyMesh")
    print("   - Or use VPN services with API")
    print("2. Add proxy URLs to the proxies list in the code")
    print("3. Run the crawler with proxy rotation")
