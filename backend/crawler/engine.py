"""
Crawler engine implementation using Playwright.
"""
import logging
import time
import re
import asyncio
from urllib.parse import urljoin, urlparse
from typing import Set, Dict, List, Optional, Tuple
from datetime import datetime
import playwright
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

from api.models import CrawlConfig, CrawlProgress
from processor.extractor import ContentExtractor

logger = logging.getLogger(__name__)

class PlaywrightCrawler:
    """Crawler implementation using Playwright for JavaScript rendering."""
    
    def __init__(self, domain: str, config: CrawlConfig, db, crawl_id: str):
        """Initialize the crawler."""
        self.domain = self._normalize_domain(domain)
        self.config = config
        self.db = db
        self.crawl_id = crawl_id
        
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
        """Extract base domain from URL."""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
    
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
        """Run the crawler."""
        self.running = True
        
        # Start with the domain URL
        self.queue = [(self.domain, 0)]  # (url, depth)
        self.discovered_urls.add(self.domain)
        
        with sync_playwright() as self.playwright:
            # Launch browser
            self.browser = self.playwright.chromium.launch(
                headless=True
            )
            
            try:
                # Process queue until empty or max pages reached
                while self.queue and self.running:
                    # Check if max pages limit reached
                    if (self.config.max_pages is not None and 
                        len(self.visited_urls) >= self.config.max_pages):
                        logger.info(f"Reached max pages limit: {self.config.max_pages}")
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
                    logger.info(f"Crawling: {url} (depth: {depth})")
                    
                    try:
                        # Create a new page for each request
                        page = self.browser.new_page(
                            user_agent=self.config.user_agent
                        )
                        
                        # Set timeout
                        page.set_default_timeout(self.config.timeout * 1000)
                        
                        # Go to URL
                        response = page.goto(url)
                        
                        # Skip if not HTML
                        content_type = response.headers.get('content-type', '')
                        if not content_type.startswith('text/html'):
                            page.close()
                            continue
                        
                        # Wait for page to load
                        page.wait_for_load_state('networkidle')
                        
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
                            # Save content to database
                            content_data['crawl_id'] = self.crawl_id
                            content_data['extracted_at'] = datetime.now()
                            self.db.save_content(content_data)
                            self.content_extracted += 1
                        
                        # Extract links for further crawling
                        links = self._extract_links(html, url)
                        
                        # Add links to queue
                        for link in links:
                            if link not in self.visited_urls:
                                self.queue.append((link, depth + 1))
                        
                        # Close page
                        page.close()
                        
                        # Respect delay setting
                        time.sleep(self.config.delay)
                        
                    except Exception as e:
                        logger.error(f"Failed to crawl {url}: {str(e)}")
                        self.failed_urls.add(url)
                        
                        try:
                            # Try to close the page in case of error
                            page.close()
                        except:
                            pass
            
            finally:
                # Close browser
                self.browser.close()
        
        logger.info(f"Crawl completed: {len(self.visited_urls)} pages crawled, "
                   f"{len(self.failed_urls)} failed, {self.content_extracted} content extracted")
