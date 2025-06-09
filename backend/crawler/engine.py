"""
Crawler engine implementation using Playwright.
"""
import logging
import time
import re
import asyncio
import random
from urllib.parse import urljoin, urlparse
from typing import Set, Dict, List, Optional, Tuple
from datetime import datetime
import playwright
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

from api.models import CrawlConfig, CrawlProgress
from processor.extractor import ContentExtractor

logger = logging.getLogger(__name__)

class UserAgentGenerator:
    """Generates appropriate user agents for different crawling scenarios."""
    
    DEFAULT_VOICEFORGE_UA = "VoiceForge-Crawler/1.0 (+https://voiceforge.ai/bot)"
    
    @staticmethod
    def generate_user_agent(config: CrawlConfig) -> str:
        """Generate user agent based on configuration."""
        
        if config.user_agent_mode == "custom" and config.custom_user_agent:
            return config.custom_user_agent
        
        elif config.user_agent_mode == "stealth":
            return "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        
        elif config.user_agent_mode == "default":
            # Generate professional crawler user agent
            base_ua = "VoiceForge-Crawler/1.0"
            
            # Add organization if provided
            if config.organization_name:
                base_ua += f" ({config.organization_name})"
            
            # Add contact info
            contact_info = []
            if config.contact_email:
                contact_info.append(f"contact:{config.contact_email}")
            
            contact_info.append("info:https://voiceforge.ai/bot")
            
            if contact_info:
                base_ua += f" [{'; '.join(contact_info)}]"
            
            return base_ua
        
        # Fallback to legacy user_agent field or default
        return getattr(config, 'user_agent', UserAgentGenerator.DEFAULT_VOICEFORGE_UA)

class PlaywrightCrawler:
    """Crawler implementation using Playwright for JavaScript rendering."""
    
    def __init__(self, domain: str, config: CrawlConfig, db, crawl_id: str, org_id: str):
        """Initialize the crawler."""
        self.domain = self._normalize_domain(domain)
        self.config = config
        self.db = db
        self.crawl_id = crawl_id
        self.org_id = org_id  # Add org_id for multi-tenant isolation
        
        self.visited_urls = set()
        self.queue = []
        self.discovered_urls = set()
        self.failed_urls = set()
        self.current_depth = 0
        self.content_extracted = 0
        
        self.running = False
        self.playwright = None
        self.browser = None
        self.extractor = ContentExtractor()
    
    def _normalize_domain(self, domain: str) -> str:
        """Normalize domain URL."""
        if not domain.startswith(('http://', 'https://')):
            domain = 'https://' + domain
        return domain.rstrip('/')
    
    def _get_base_domain(self, url: str) -> str:
        """Extract base domain from URL, handling subdomains for crawling."""
        parsed = urlparse(url)
        hostname = parsed.hostname or parsed.netloc
        
        # Remove port number if present
        hostname = hostname.split(':')[0]
        
        # For buf.build and similar domains, we want to normalize subdomains
        # to the root domain for crawling purposes
        parts = hostname.split('.')
        if len(parts) >= 2:
            # Extract root domain (last 2 parts)
            root_domain = '.'.join(parts[-2:])
            return f"{parsed.scheme}://{root_domain}"
        
        return f"{parsed.scheme}://{hostname}"
    
    def _should_crawl_url(self, url: str) -> bool:
        """Determine if a URL should be crawled."""
        # Skip non-HTTP URLs
        if not url.startswith(('http://', 'https://')):
            return False
        
        # Skip already visited URLs
        if url in self.visited_urls or url in self.discovered_urls:
            return False
        
        # Check if URL is from the same domain
        base_domain = self._get_base_domain(self.domain)
        url_domain = self._get_base_domain(url)
        
        if not self.config.follow_external_links and url_domain != base_domain:
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
    
    def _extract_links(self, html: str, base_url: str) -> List[str]:
        """Extract and normalize links from HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            # Normalize URL
            try:
                absolute_url = urljoin(base_url, href)
                # Remove fragments
                absolute_url = absolute_url.split('#')[0]
                # Remove trailing slash for consistency
                absolute_url = absolute_url.rstrip('/')
                
                if self._should_crawl_url(absolute_url):
                    links.append(absolute_url)
                    self.discovered_urls.add(absolute_url)
            except Exception as e:
                logger.warning(f"Failed to process URL {href}: {str(e)}")
        
        return links
    
    def get_progress(self) -> CrawlProgress:
        """Get the current progress of the crawl."""
        return CrawlProgress(
            pages_crawled=len(self.visited_urls),
            pages_discovered=len(self.discovered_urls),
            pages_failed=len(self.failed_urls),
            current_depth=self.current_depth,
            content_extracted=self.content_extracted
        )
    
    def stop(self):
        """Stop the crawler."""
        self.running = False
    
    def crawl(self):
        """Run the crawler with configurable user agent and enhanced capabilities."""
        self.running = True
        
        # Generate appropriate user agent based on configuration
        user_agent = UserAgentGenerator.generate_user_agent(self.config)
        
        # 🔍 DEBUG: Log initial configuration
        logger.warning(f"🚀 VOICEFORGE CRAWLER: Starting crawl for {self.domain}")
        logger.warning(f"  User Agent: {user_agent}")
        logger.warning(f"  User Agent Mode: {self.config.user_agent_mode}")
        logger.warning(f"  max_pages: {self.config.max_pages}")
        logger.warning(f"  max_depth: {self.config.max_depth}")
        logger.warning(f"  delay: {self.config.delay}")
        
        # Start with the domain URL
        self.queue = [(self.domain, 0)]  # (url, depth)
        self.discovered_urls.add(self.domain)
        
        # Add randomized initial delay to avoid detection patterns
        initial_delay = random.uniform(1.0, 3.0)
        logger.info(f"⏳ Initial delay: {initial_delay:.2f}s before starting crawl")
        time.sleep(initial_delay)
        
        with sync_playwright() as self.playwright:
            # Choose browser launch mode based on user agent type
            if self.config.user_agent_mode == "stealth":
                # Use stealth mode for demo/testing purposes
                browser_args = [
                    "--no-first-run",
                    "--no-default-browser-check",
                    "--disable-background-timer-throttling",
                    "--disable-renderer-backgrounding",
                    "--disable-backgrounding-occluded-windows",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-features=TranslateUI",
                    "--disable-extensions",
                    "--no-sandbox",
                    "--disable-setuid-sandbox"
                ]
                
                self.browser = self.playwright.chromium.launch(
                    headless=True,
                    args=browser_args
                )
                
                context = self.browser.new_context(
                    viewport={'width': 1366, 'height': 768},
                    user_agent=user_agent,
                    locale='en-US',
                    timezone_id='America/New_York'
                )
            else:
                # Standard crawler mode for legitimate crawling
                self.browser = self.playwright.chromium.launch(headless=True)
                
                context = self.browser.new_context(
                    user_agent=user_agent
                )
            
            try:
                # Process queue until empty or max pages reached
                while self.queue and self.running:
                    # 🔍 DEBUG: Log progress every 5 pages
                    if len(self.visited_urls) % 5 == 0 and len(self.visited_urls) > 0:
                        logger.warning(f"🔍 CRAWLER: Progress - Visited: {len(self.visited_urls)}, Queue: {len(self.queue)}")
                    
                    # Check if max pages limit reached
                    if (self.config.max_pages is not None and 
                        len(self.visited_urls) >= self.config.max_pages):
                        logger.warning(f"🔍 CRAWLER: STOPPED - Reached max_pages limit!")
                        break
                    
                    # Get next URL from queue
                    url, depth = self.queue.pop(0)
                    
                    # Skip if already visited
                    if url in self.visited_urls:
                        continue
                    
                    # Check depth limit
                    if depth > self.config.max_depth:
                        continue
                    
                    # Update current depth
                    self.current_depth = max(self.current_depth, depth)
                    
                    # Visit URL
                    logger.info(f"📄 Crawling: {url} (depth: {depth})")
                    
                    try:
                        # Create a new page for each request
                        page = context.new_page()
                        
                        # Set appropriate headers based on mode
                        if self.config.user_agent_mode == "stealth":
                            # Stealth mode headers for demo purposes
                            page.set_extra_http_headers({
                                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                                "Accept-Language": "en-US,en;q=0.9",
                                "Accept-Encoding": "gzip, deflate, br",
                                "DNT": "1",
                                "Connection": "keep-alive",
                                "Upgrade-Insecure-Requests": "1",
                                "Sec-Fetch-Dest": "document",
                                "Sec-Fetch-Mode": "navigate",
                                "Sec-Fetch-Site": "none" if depth == 0 else "same-origin",
                                "Sec-Fetch-User": "?1" if depth == 0 else "?0",
                                "Cache-Control": "max-age=0"
                            })
                            
                            # Hide automation for demo purposes
                            page.add_init_script("""
                                // Hide webdriver property
                                Object.defineProperty(navigator, 'webdriver', {
                                    get: () => undefined
                                });
                                
                                // Hide automation indicators
                                delete window.__playwright;
                                delete window.__pwInitScript;
                                
                                // Add realistic chrome object
                                window.chrome = {
                                    runtime: {}
                                };
                                
                                // Realistic plugins
                                Object.defineProperty(navigator, 'plugins', {
                                    get: () => [1, 2, 3, 4, 5]
                                });
                            """)
                        else:
                            # Standard crawler headers for legitimate crawling
                            page.set_extra_http_headers({
                                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                                "Accept-Language": "en-US,en;q=0.5",
                                "Accept-Encoding": "gzip, deflate",
                                "Connection": "keep-alive"
                            })
                        
                        # Set timeout
                        page.set_default_timeout(self.config.timeout * 1000)
                        
                        # Add delay for stealth mode or use configured delay
                        if self.config.user_agent_mode == "stealth":
                            human_delay = random.uniform(2.0, 5.0)
                            time.sleep(human_delay)
                        
                        # Navigate to URL with retry logic for stealth mode
                        response = None
                        max_attempts = 3 if self.config.user_agent_mode == "stealth" else 1
                        
                        for attempt in range(max_attempts):
                            try:
                                wait_until = 'networkidle' if self.config.user_agent_mode == "stealth" else 'load'
                                response = page.goto(url, wait_until=wait_until, timeout=30000)
                                break
                            except Exception as e:
                                if attempt < max_attempts - 1:
                                    logger.warning(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
                                    time.sleep(random.uniform(1, 3))
                                else:
                                    raise e
                        
                        if not response:
                            logger.error(f"Failed to get response for {url}")
                            page.close()
                            continue
                        
                        # Check response status
                        if response.status >= 400:
                            logger.warning(f"HTTP {response.status} for {url}")
                            if response.status == 403 or response.status == 429:
                                logger.warning("🚨 Possible bot detection or rate limiting!")
                                if self.config.user_agent_mode == "stealth":
                                    time.sleep(random.uniform(10, 20))
                            page.close()
                            self.failed_urls.add(url)
                            continue
                        
                        # Skip if not HTML
                        content_type = response.headers.get('content-type', '')
                        if not content_type.startswith('text/html'):
                            page.close()
                            continue
                        
                        # Additional page load handling for stealth mode
                        if self.config.user_agent_mode == "stealth":
                            try:
                                # Simulate human scrolling behavior
                                page.evaluate("""
                                    new Promise((resolve) => {
                                        let totalHeight = 0;
                                        const distance = 100;
                                        const timer = setInterval(() => {
                                            const scrollHeight = document.body.scrollHeight;
                                            window.scrollBy(0, distance);
                                            totalHeight += distance;
                                            
                                            if(totalHeight >= scrollHeight){
                                                clearInterval(timer);
                                                resolve();
                                            }
                                        }, 100);
                                    })
                                """)
                                
                                # Small delay after scrolling
                                time.sleep(random.uniform(0.5, 1.5))
                                
                            except Exception as e:
                                logger.warning(f"Page load timeout for {url}: {str(e)}")
                        else:
                            # Standard page load for legitimate crawling
                            try:
                                page.wait_for_load_state('networkidle', timeout=15000)
                            except:
                                pass  # Continue if timeout
                        
                        # Get HTML content
                        html = page.content()
                        
                        # Mark as visited
                        self.visited_urls.add(url)
                        
                        # Extract content
                        content_data = self.extractor.extract(
                            url=url,
                            html=html,
                            domain=self._get_base_domain(url)
                        )
                        
                        if content_data:
                            # Save content to database with org_id
                            content_data['crawl_id'] = self.crawl_id
                            content_data['org_id'] = self.org_id  # Add org_id for multi-tenant isolation
                            content_data['extracted_at'] = datetime.now()
                            self.db.save_content(content_data, self.org_id)
                            self.content_extracted += 1
                            logger.info(f"✅ Content extracted from {url}")
                        
                        # Extract links for further crawling
                        links = self._extract_links(html, url)
                        
                        # Add links to queue
                        for link in links:
                            if link not in self.visited_urls:
                                self.queue.append((link, depth + 1))
                        
                        # Shuffle queue for stealth mode to avoid predictable patterns
                        if self.config.user_agent_mode == "stealth":
                            random.shuffle(self.queue)
                        
                        # Close page
                        page.close()
                        
                        # Enhanced delay with randomization for all modes
                        base_delay = self.config.delay
                        if self.config.user_agent_mode == "stealth":
                            # More aggressive randomization for stealth mode
                            random_delay = base_delay + random.uniform(0.5, 3.0)
                        else:
                            # Standard randomization for legitimate crawling
                            # Randomize delay between 50% and 150% of base delay
                            min_delay = base_delay * 0.5
                            max_delay = base_delay * 1.5
                            random_delay = random.uniform(min_delay, max_delay)
                        
                        logger.debug(f"⏱️ Waiting {random_delay:.2f}s (base: {base_delay}s)")
                        time.sleep(random_delay)
                        
                    except Exception as e:
                        logger.error(f"❌ Failed to crawl {url}: {str(e)}")
                        self.failed_urls.add(url)
                        
                        try:
                            # Try to close the page in case of error
                            page.close()
                        except:
                            pass
                        
                        # Error delay with randomization
                        if self.config.user_agent_mode == "stealth":
                            error_delay = random.uniform(5.0, 15.0)
                        else:
                            error_delay = random.uniform(1.0, 4.0)
                        
                        logger.debug(f"❌ Error delay: {error_delay:.2f}s")
                        time.sleep(error_delay)
            
            finally:
                # Close context and browser
                context.close()
                self.browser.close()
        
        # 🔍 DEBUG: Final status
        logger.warning(f"🎉 VOICEFORGE CRAWLER: Crawl completed - Final status:")
        logger.warning(f"  Pages crawled: {len(self.visited_urls)}")
        logger.warning(f"  Pages discovered: {len(self.discovered_urls)}")
        logger.warning(f"  Pages failed: {len(self.failed_urls)}")
        logger.warning(f"  Content extracted: {self.content_extracted}")
        logger.warning(f"  User Agent Used: {user_agent}")
        
        logger.info(f"Crawl completed: {len(self.visited_urls)} pages crawled, "
                   f"{len(self.failed_urls)} failed, {self.content_extracted} content extracted")
