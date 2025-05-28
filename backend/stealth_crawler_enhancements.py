"""
Stealth enhancements for VoiceForge crawler to avoid detection
Add these improvements to your crawler/engine.py
"""

import random
import time
import json
from typing import List, Dict

class StealthCrawlerEnhancer:
    """Enhancements to make your crawler more stealthy"""
    
    # Realistic User-Agent strings (recent browsers)
    USER_AGENTS = [
        # Chrome on macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        # Chrome on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        # Safari on macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",  
        # Firefox on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
        # Edge on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
    ]
    
    # Realistic HTTP headers
    @staticmethod
    def get_realistic_headers() -> Dict[str, str]:
        """Get realistic HTTP headers that mimic a real browser"""
        return {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0"
        }
    
    @staticmethod
    def get_stealth_browser_args() -> List[str]:
        """Get browser arguments to hide automation"""
        return [
            "--disable-blink-features=AutomationControlled",
            "--disable-web-security",
            "--disable-features=VizDisplayCompositor",
            "--disable-extensions",
            "--disable-plugins",
            "--disable-dev-shm-usage",
            "--no-sandbox",
            "--disable-gpu",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding"
        ]
    
    @staticmethod
    def get_stealth_init_scripts() -> List[str]:
        """Get JavaScript to hide automation signatures"""
        return [
            # Hide webdriver property
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})",
            
            # Hide chrome automation
            "window.chrome = {runtime: {}}",
            
            # Hide automation in permissions
            """
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                Promise.resolve({state: Notification.permission}) :
                originalQuery(parameters)
            );
            """,
            
            # Hide headless detection
            """
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            """,
            
            # Mock language detection
            """
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            """
        ]
    
    @staticmethod
    def calculate_human_delay(content_length: int = 0, base_delay: float = 2.0) -> float:
        """Calculate human-like delay based on content length"""
        # Base delay
        delay = base_delay
        
        # Add reading time based on content length
        if content_length > 0:
            # Assume 200 words per minute reading speed
            words = content_length / 5  # Rough estimate
            reading_time = (words / 200) * 60  # Convert to seconds
            delay += min(reading_time * 0.3, 10)  # Cap at 10 seconds
        
        # Add random variation (±50%)
        variation = random.uniform(0.5, 1.5)
        delay *= variation
        
        # Ensure minimum delay
        return max(delay, 1.0)
    
    @staticmethod
    def should_take_break(pages_crawled: int) -> bool:
        """Determine if crawler should take a longer break"""
        # Take break every 10-20 pages
        break_interval = random.randint(10, 20)
        return pages_crawled > 0 and pages_crawled % break_interval == 0
    
    @staticmethod
    def get_break_duration() -> float:
        """Get duration for longer breaks"""
        # 30 seconds to 2 minutes
        return random.uniform(30, 120)

# Enhanced crawler methods to add to your PlaywrightCrawler class

def setup_stealth_browser(self):
    """Enhanced browser setup with stealth features"""
    # Launch browser with stealth args
    self.browser = self.playwright.chromium.launch(
        headless=True,
        args=StealthCrawlerEnhancer.get_stealth_browser_args()
    )
    
    # Create context with realistic settings
    self.context = self.browser.new_context(
        user_agent=random.choice(StealthCrawlerEnhancer.USER_AGENTS),
        viewport={'width': 1920, 'height': 1080},
        locale='en-US',
        timezone_id='America/New_York',
        permissions=['notifications']
    )
    
    return self.context

def setup_stealth_page(self, context):
    """Setup a page with stealth features"""
    page = context.new_page()
    
    # Set realistic headers
    page.set_extra_http_headers(
        StealthCrawlerEnhancer.get_realistic_headers()
    )
    
    # Add stealth scripts
    for script in StealthCrawlerEnhancer.get_stealth_init_scripts():
        page.add_init_script(script)
    
    # Set timeout
    page.set_default_timeout(self.config.timeout * 1000)
    
    return page

def enhanced_crawl_with_stealth(self):
    """Enhanced crawl method with stealth features"""
    self.running = True
    
    # Start with the domain URL
    self.queue = [(self.domain, 0)]
    self.discovered_urls.add(self.domain)
    
    with sync_playwright() as self.playwright:
        # Setup stealth browser
        context = setup_stealth_browser(self)
        
        try:
            page = setup_stealth_page(self, context)
            
            while self.queue and self.running:
                # Check limits
                if (self.config.max_pages is not None and 
                    len(self.visited_urls) >= self.config.max_pages):
                    break
                
                # Take break if needed
                if StealthCrawlerEnhancer.should_take_break(len(self.visited_urls)):
                    break_time = StealthCrawlerEnhancer.get_break_duration()
                    logger.info(f"Taking a break for {break_time:.1f} seconds...")
                    time.sleep(break_time)
                
                url, depth = self.queue.pop(0)
                
                if url in self.visited_urls or depth > self.config.max_depth:
                    continue
                
                logger.info(f"Crawling: {url} (depth: {depth})")
                
                try:
                    # Navigate to URL
                    response = page.goto(url, wait_until='networkidle')
                    
                    # Check content type
                    content_type = response.headers.get('content-type', '')
                    if not content_type.startswith('text/html'):
                        continue
                    
                    # Get content
                    html = page.content()
                    content_length = len(html)
                    
                    # Mark as visited
                    self.visited_urls.add(url)
                    
                    # Extract and save content
                    content_data = self.extractor.extract(
                        url=url, html=html, domain=self._get_base_domain(url)
                    )
                    
                    if content_data:
                        content_data.update({
                            'crawl_id': self.crawl_id,
                            'org_id': self.org_id,
                            'extracted_at': datetime.now()
                        })
                        self.db.save_content(content_data, self.org_id)
                        self.content_extracted += 1
                    
                    # Extract links
                    links = self._extract_links(html, url)
                    for link in links:
                        if link not in self.visited_urls:
                            self.queue.append((link, depth + 1))
                    
                    # Human-like delay
                    delay = StealthCrawlerEnhancer.calculate_human_delay(
                        content_length, self.config.delay
                    )
                    logger.debug(f"Waiting {delay:.1f} seconds...")
                    time.sleep(delay)
                    
                except Exception as e:
                    logger.error(f"Failed to crawl {url}: {str(e)}")
                    self.failed_urls.add(url)
                    
                    # Random delay even on failure
                    time.sleep(random.uniform(1, 3))
        
        finally:
            context.close()
            self.browser.close()

# Simple integration guide
INTEGRATION_GUIDE = """
🛠️ HOW TO INTEGRATE STEALTH FEATURES:

1. Add to your crawler/engine.py:
   - Import StealthCrawlerEnhancer
   - Replace browser.launch() with setup_stealth_browser()
   - Replace page creation with setup_stealth_page()
   - Use enhanced_crawl_with_stealth() method

2. Update your config defaults:
   - delay: 3 (minimum 3 seconds)
   - timeout: 20 (allow more time)
   - max_pages: 10 (be conservative)

3. Test with crawler-friendly sites first:
   - https://httpbin.org
   - https://example.com
   - https://jsonplaceholder.typicode.com

4. Monitor success rates:
   - Log successful vs failed requests
   - Adjust delays if seeing blocks
   - Rotate User-Agents more frequently if needed

5. For production:
   - Implement IP rotation if possible
   - Add proxy support
   - Respect robots.txt
   - Monitor rate limits
"""

def print_integration_guide():
    """Print the integration guide"""
    print(INTEGRATION_GUIDE)

if __name__ == "__main__":
    print("🥷 VoiceForge Stealth Crawler Enhancements")
    print("=" * 50)
    
    print("🎯 Key improvements:")
    print("   • Realistic User-Agent rotation")
    print("   • Human-like timing patterns") 
    print("   • Browser fingerprint masking")
    print("   • Complete HTTP headers")
    print("   • Anti-detection JavaScript")
    print("   • Session management")
    
    print_integration_guide()
    
    print("\n🚀 Result: Your crawler will be much harder to detect!")
    print("Your RAG automation will work smoothly with these enhancements.")
