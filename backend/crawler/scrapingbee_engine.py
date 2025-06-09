"""
ScrapingBee integration for VoiceForge web crawling.
Alternative to Firecrawl with excellent bot detection bypass.
"""
import os
import logging
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from api.models import CrawlConfig, CrawlProgress
from processor.extractor import ContentExtractor

logger = logging.getLogger(__name__)

class ScrapingBeeCrawler:
    """ScrapingBee-based crawler for VoiceForge."""
    
    def __init__(self, domain: str, config: CrawlConfig, db, crawl_id: str, org_id: str):
        """Initialize the ScrapingBee crawler."""
        self.domain = self._normalize_domain(domain)
        self.config = config
        self.db = db
        self.crawl_id = crawl_id
        self.org_id = org_id
        
        # Initialize ScrapingBee
        self.api_key = os.getenv('SCRAPINGBEE_API_KEY')
        if not self.api_key:
            raise ValueError("SCRAPINGBEE_API_KEY environment variable is required")
        
        self.base_url = "https://app.scrapingbee.com/api/v1/"
        self.extractor = ContentExtractor()
        
        # Progress tracking
        self.pages_crawled = 0
        self.pages_discovered = 0
        self.pages_failed = 0
        self.content_extracted = 0
        self.current_depth = 0
        self.visited_urls = set()
        self.queue = []
        
        logger.info(f"🐝 ScrapingBee crawler initialized for {domain}")
    
    def _normalize_domain(self, domain: str) -> str:
        """Normalize domain URL."""
        if not domain.startswith(('http://', 'https://')):
            domain = 'https://' + domain
        return domain.rstrip('/')
    
    def get_progress(self) -> CrawlProgress:
        """Get the current progress of the crawl."""
        return CrawlProgress(
            pages_crawled=self.pages_crawled,
            pages_discovered=self.pages_discovered,
            pages_failed=self.pages_failed,
            current_depth=self.current_depth,
            content_extracted=self.content_extracted
        )
    
    def _scrape_page(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrape a single page using ScrapingBee."""
        try:
            params = {
                'api_key': self.api_key,
                'url': url,
                'render_js': 'true',  # Enable JavaScript rendering
                'premium_proxy': 'true',  # Use premium proxies for better success rate
                'stealth_proxy': 'true',  # Enable stealth mode
                'session_id': f'voiceforge_{self.crawl_id}',  # Session for consistent crawling
                'wait': '2000',  # Wait 2 seconds for page load
                'wait_for': 'networkidle',  # Wait for network to be idle
                'extract_rules': {
                    'title': 'title',
                    'description': 'meta[name="description"]@content',
                    'keywords': 'meta[name="keywords"]@content',
                    'h1': 'h1',
                    'h2': 'h2',
                    'links': 'a@href'
                }
            }
            
            response = requests.get(self.base_url, params=params, timeout=60)
            
            if response.status_code == 200:
                return {
                    'html': response.text,
                    'url': url,
                    'success': True
                }
            else:
                logger.warning(f"ScrapingBee API error {response.status_code} for {url}: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return None
    
    def _extract_links(self, html: str, base_url: str) -> List[str]:
        """Extract links from HTML."""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            links = []
            
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                try:
                    absolute_url = urljoin(base_url, href)
                    # Remove fragments and normalize
                    absolute_url = absolute_url.split('#')[0].rstrip('/')
                    
                    if self._should_crawl_url(absolute_url):
                        links.append(absolute_url)
                        
                except Exception as e:
                    logger.debug(f"Failed to process URL {href}: {str(e)}")
            
            return links
            
        except Exception as e:
            logger.error(f"Error extracting links from {base_url}: {str(e)}")
            return []
    
    def _should_crawl_url(self, url: str) -> bool:
        """Determine if a URL should be crawled."""
        # Skip non-HTTP URLs
        if not url.startswith(('http://', 'https://')):
            return False
        
        # Skip already visited URLs
        if url in self.visited_urls:
            return False
        
        # Check domain restrictions
        if not self.config.follow_external_links:
            url_domain = urlparse(url).netloc.lower()
            base_domain = urlparse(self.domain).netloc.lower()
            if url_domain != base_domain:
                return False
        
        # Apply exclude patterns
        for pattern in self.config.exclude_patterns:
            import re
            if re.search(pattern, url):
                return False
        
        # Apply include patterns if specified
        if self.config.include_patterns:
            for pattern in self.config.include_patterns:
                import re
                if re.search(pattern, url):
                    return True
            return False
        
        return True
    
    def crawl(self):
        """Run the ScrapingBee crawler."""
        logger.info(f"🚀 Starting ScrapingBee crawl for {self.domain}")
        logger.info(f"📋 Config: max_pages={self.config.max_pages}, max_depth={self.config.max_depth}")
        
        try:
            # Initialize queue with starting URL
            self.queue = [(self.domain, 0)]  # (url, depth)
            
            while self.queue and len(self.visited_urls) < self.config.max_pages:
                # Get next URL
                url, depth = self.queue.pop(0)
                
                # Check depth limit
                if depth > self.config.max_depth:
                    continue
                
                # Skip if already visited
                if url in self.visited_urls:
                    continue
                
                logger.info(f"📝 Scraping {len(self.visited_urls) + 1}/{self.config.max_pages}: {url} (depth: {depth})")
                
                # Scrape the page
                result = self._scrape_page(url)
                
                if not result or not result['success']:
                    self.pages_failed += 1
                    logger.warning(f"❌ Failed to scrape {url}")
                    continue
                
                # Mark as visited
                self.visited_urls.add(url)
                self.pages_crawled += 1
                self.current_depth = max(self.current_depth, depth)
                
                # Extract content
                html = result['html']
                content_data = self.extractor.extract(
                    url=url,
                    html=html,
                    domain=self._get_domain_from_url(url)
                )
                
                if content_data:
                    # Save content to database
                    content_data['crawl_id'] = self.crawl_id
                    content_data['org_id'] = self.org_id
                    content_data['extracted_at'] = datetime.utcnow()
                    
                    self.db.save_content(content_data, self.org_id)
                    self.content_extracted += 1
                    logger.info(f"✅ Saved content from {url}")
                
                # Extract links for next depth level
                if depth < self.config.max_depth:
                    links = self._extract_links(html, url)
                    for link in links:
                        if link not in self.visited_urls:
                            self.queue.append((link, depth + 1))
                            self.pages_discovered += 1
                
                # Rate limiting delay
                import time
                time.sleep(self.config.delay)
            
            logger.info(f"🎉 ScrapingBee crawl completed!")
            logger.info(f"📊 Results: {self.pages_crawled} crawled, {self.content_extracted} extracted, {self.pages_failed} failed")
            
        except Exception as e:
            logger.error(f"❌ ScrapingBee crawl failed: {str(e)}")
            raise
    
    def _get_domain_from_url(self, url: str) -> str:
        """Extract domain from URL."""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
    
    def _determine_content_type(self, url: str, title: str) -> str:
        """Determine content type based on URL and title."""
        url_lower = url.lower()
        title_lower = (title or '').lower()
        
        if any(pattern in url_lower for pattern in ['/blog/', '/news/', '/article/']):
            return 'article'
        elif any(pattern in url_lower for pattern in ['/docs/', '/documentation/', '/guide/']):
            return 'documentation'
        elif any(pattern in url_lower for pattern in ['/about', '/company', '/team']):
            return 'about_page'
        elif any(pattern in title_lower for pattern in ['tutorial', 'guide', 'how to']):
            return 'tutorial'
        elif any(pattern in title_lower for pattern in ['api', 'reference']):
            return 'api_documentation'
        else:
            return 'webpage'
    
    def stop(self):
        """Stop the crawler."""
        logger.info("🛑 ScrapingBee crawl stop requested")
