"""
Firecrawl integration for VoiceForge web crawling.
Replaces the complex Playwright crawler with a simple API service.
"""
import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

from api.models import CrawlConfig, CrawlProgress
from processor.extractor import ContentExtractor

logger = logging.getLogger(__name__)

# Import Firecrawl directly (fixed version)
try:
    from firecrawl import FirecrawlApp
    FIRECRAWL_AVAILABLE = True
    logger.info("🔥 Firecrawl imported successfully with patch")
except Exception as e:
    logger.error(f"Failed to import Firecrawl: {e}")
    FIRECRAWL_AVAILABLE = False
    FirecrawlApp = None

logger = logging.getLogger(__name__)

class FirecrawlCrawler:
    """Firecrawl-based crawler for VoiceForge."""
    
    def __init__(self, domain: str, config: CrawlConfig, db, crawl_id: str, org_id: str):
        """Initialize the Firecrawl crawler."""
        if not FIRECRAWL_AVAILABLE or FirecrawlApp is None:
            raise ValueError("Firecrawl is not available due to dependency conflicts")
            
        self.domain = self._normalize_domain(domain)
        self.config = config
        self.db = db
        self.crawl_id = crawl_id
        self.org_id = org_id
        
        # Initialize Firecrawl
        api_key = os.getenv('FIRECRAWL_API_KEY')
        if not api_key:
            raise ValueError("FIRECRAWL_API_KEY environment variable is required")
        
        self.firecrawl = FirecrawlApp(api_key=api_key)
        self.extractor = ContentExtractor()
        
        # Progress tracking
        self.pages_crawled = 0
        self.pages_discovered = 0
        self.pages_failed = 0
        self.content_extracted = 0
        self.current_depth = 0
        
        logger.info(f"🔥 Firecrawl crawler initialized for {domain}")
    
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
    
    def crawl(self):
        """Run the Firecrawl crawler with enhanced URL handling and retry logic."""
        logger.info(f"🚀 Starting Firecrawl crawl for {self.domain}")
        logger.info(f"📋 Config: max_pages={self.config.max_pages}, max_depth={self.config.max_depth}")
        
        # Try multiple URL patterns for better success rate
        url_patterns = [
            f"{self.domain}/docs",      # Documentation first
            f"{self.domain}/blog",      # Blog content
            f"docs.{self.domain.replace('https://', '').replace('http://', '')}",  # Docs subdomain
            self.domain                 # Original URL last
        ]
        
        crawl_result = None
        successful_url = None
        
        for attempt_url in url_patterns:
            try:
                logger.info(f"🔄 Attempting crawl of: {attempt_url}")
                
                # First, test single page access to validate URL
                test_result = self._test_single_page_access(attempt_url)
                if not test_result:
                    logger.warning(f"⚠️ Single page test failed for: {attempt_url}")
                    continue
                
                # Build enhanced Firecrawl options for v1 API
                logger.info(f"🔥 Using Firecrawl v1 API format")
                
                # Start the crawl with current URL using v1 API format
                logger.info(f"🌐 Crawling {attempt_url}...")
                
                # Try v1 API format first
                try:
                    crawl_result = self.firecrawl.crawl_url(
                        attempt_url,
                        limit=min(self.config.max_pages, 25),
                        scrapeOptions={
                            "formats": ["markdown", "html"]
                        }
                    )
                except Exception as v1_error:
                    logger.warning(f"⚠️ V1 crawl format failed: {v1_error}")
                    logger.info("🔄 Trying alternative crawl format...")
                    
                    # Try alternative format
                    crawl_result = self.firecrawl.crawl_url(
                        attempt_url,
                        limit=min(self.config.max_pages, 25)
                    )
                
                # Check if we got actual data
                if (crawl_result and 
                    hasattr(crawl_result, 'data') and 
                    crawl_result.data and 
                    len(crawl_result.data) > 0):
                    
                    logger.info(f"✅ Success with URL: {attempt_url}")
                    logger.info(f"📄 Found {len(crawl_result.data)} pages")
                    successful_url = attempt_url
                    break
                else:
                    logger.warning(f"⚠️ No data from: {attempt_url}")
                    self._log_crawl_details(crawl_result)
                    if attempt_url == url_patterns[-1]:  # Last attempt
                        logger.error("❌ All URL patterns failed")
                    continue
                    
            except Exception as e:
                logger.error(f"❌ Failed {attempt_url}: {str(e)}")
                if attempt_url == url_patterns[-1]:  # Last attempt
                    raise
                continue
        
        # Process results
        try:
            
            if not crawl_result or not hasattr(crawl_result, 'data') or not crawl_result.data:
                logger.error("❌ All crawl attempts failed - no data returned")
                self._log_crawl_details(crawl_result)
                
                # Try fallback to direct HTTP scraping
                logger.info("🔄 Attempting fallback to direct scraping...")
                fallback_result = self._fallback_scrape(self.domain)
                if fallback_result:
                    self._process_fallback_content(fallback_result)
                    return
                    
                logger.error("❌ All crawl methods failed")
                return
            
            pages = crawl_result.data
            self.pages_discovered = len(pages)
            
            logger.info(f"📄 Firecrawl discovered {len(pages)} pages from {successful_url}")
            
            # Process each page
            for i, page in enumerate(pages, 1):
                try:
                    logger.info(f"📝 Processing {i}/{len(pages)}: {getattr(page, 'title', 'Untitled')}")
                    
                    # Extract page data - handle FirecrawlDocument objects properly
                    try:
                        # All data is in the object attributes, not dict methods
                        url = None
                        if hasattr(page, 'url') and page.url:
                            url = page.url
                        elif hasattr(page, 'metadata') and page.metadata:
                            # Extract URL from metadata object
                            if hasattr(page.metadata, 'sourceURL'):
                                url = page.metadata.sourceURL
                            elif hasattr(page.metadata, 'url'):
                                url = page.metadata.url
                            elif isinstance(page.metadata, dict):
                                url = page.metadata.get('sourceURL') or page.metadata.get('url')
                        
                        # Extract title
                        title = ''
                        if hasattr(page, 'title') and page.title:
                            title = page.title
                        elif hasattr(page, 'metadata') and page.metadata:
                            if hasattr(page.metadata, 'title'):
                                title = page.metadata.title or ''
                            elif isinstance(page.metadata, dict):
                                title = page.metadata.get('title', '')
                        
                        # Extract content
                        markdown_content = getattr(page, 'markdown', '') or ''
                        html_content = getattr(page, 'html', '') or ''
                        
                        # Convert metadata to dict for storage
                        metadata = {}
                        if hasattr(page, 'metadata') and page.metadata:
                            if isinstance(page.metadata, dict):
                                metadata = page.metadata
                            elif hasattr(page.metadata, '__dict__'):
                                metadata = page.metadata.__dict__
                            else:
                                # Try to convert pydantic model to dict
                                try:
                                    metadata = page.metadata.dict() if hasattr(page.metadata, 'dict') else {}
                                except:
                                    metadata = {}
                        
                    except Exception as e:
                        logger.error(f"❌ Error extracting data from page {i}: {e}")
                        logger.info(f"🔍 Page {i} type: {type(page)}, attributes: {dir(page)}")
                        continue
                    
                    # Debug: Log the page structure to understand what we're getting
                    if i <= 3:  # Only log first 3 pages to avoid spam
                        logger.info(f"🔍 DEBUG Page {i} structure: {list(page.__dict__.keys()) if hasattr(page, '__dict__') else list(page.keys())}")
                        logger.info(f"🔍 DEBUG Page {i} URL candidates: url={getattr(page, 'url', None)}, sourceURL={getattr(page, 'sourceURL', None)}")
                        if hasattr(page, 'metadata'):
                            logger.info(f"🔍 DEBUG Page {i} metadata: {page.metadata}")
                        elif isinstance(page, dict) and 'metadata' in page:
                            logger.info(f"🔍 DEBUG Page {i} metadata: {page['metadata']}")
                    
                    if not url:
                        logger.warning(f"⚠️ Skipping page {i}: no URL")
                        continue
                    
                    if not markdown_content and not html_content:
                        logger.warning(f"⚠️ Skipping page {i}: no content")
                        continue
                    
                    # Create content data structure
                    content_data = {
                        'content_id': str(uuid.uuid4()),
                        'url': url,
                        'domain': self._get_domain_from_url(url),
                        'text': markdown_content or self._html_to_text(html_content),
                        'html': html_content,
                        'crawl_id': self.crawl_id,
                        'extracted_at': datetime.utcnow(),
                        'metadata': {
                            'title': title,
                            'author': metadata.get('author') if isinstance(metadata, dict) else None,
                            'description': metadata.get('description') or metadata.get('ogDescription') if isinstance(metadata, dict) else None,
                            'keywords': metadata.get('keywords', []) if isinstance(metadata, dict) else [],
                            'language': metadata.get('language', 'en') if isinstance(metadata, dict) else 'en',
                            'content_type': self._determine_content_type(url, title),
                            'publication_date': self._parse_date(metadata.get('publishedTime') if isinstance(metadata, dict) else None),
                            'last_modified': self._parse_date(metadata.get('modifiedTime') if isinstance(metadata, dict) else None),
                            'categories': [],
                            'tags': metadata.get('keywords', []) if isinstance(metadata, dict) else [],
                            'source_url': url,
                            'crawl_metadata': metadata if isinstance(metadata, dict) else {}
                        }
                    }
                    
                    # Save to database
                    try:
                        self.db.save_content(content_data, self.org_id)
                        self.content_extracted += 1
                        self.pages_crawled += 1
                        
                        logger.info(f"✅ Saved content from {url}")
                    except Exception as db_error:
                        logger.error(f"❌ Failed to save content from {url}: {str(db_error)}")
                        logger.error(f"❌ Content data structure: {type(content_data)}")
                        logger.error(f"❌ Metadata type: {type(content_data.get('metadata', 'missing'))}")
                        self.pages_failed += 1
                        continue
                    
                except Exception as e:
                    logger.error(f"❌ Failed to process page {i}: {str(e)}")
                    self.pages_failed += 1
                    continue
            
            logger.info(f"🎉 Firecrawl crawl completed using {successful_url}!")
            logger.info(f"📊 Results: {self.pages_crawled} crawled, {self.content_extracted} extracted, {self.pages_failed} failed")
            
        except Exception as e:
            logger.error(f"❌ Firecrawl crawl processing failed: {str(e)}")
            raise
    
    def _get_domain_from_url(self, url: str) -> str:
        """Extract domain from URL."""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
    
    def _html_to_text(self, html: str) -> str:
        """Convert HTML to plain text as fallback."""
        from bs4 import BeautifulSoup
        try:
            soup = BeautifulSoup(html, 'html.parser')
            return soup.get_text(strip=True)
        except:
            return html
    
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
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime."""
        if not date_str:
            return None
        
        try:
            # Try ISO format first
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            try:
                # Try common formats
                from dateutil import parser
                return parser.parse(date_str)
            except:
                return None
    
    def _test_single_page_access(self, url: str) -> bool:
        """Test if we can access a single page before attempting full crawl."""
        try:
            logger.info(f"🔍 Testing single page access: {url}")
            
            # Use Firecrawl's scrape_url with v1 API format (formats parameter)
            result = self.firecrawl.scrape_url(
                url,
                formats=["markdown", "html"]
            )
            
            # Check for content in v1 API response format
            if result and hasattr(result, 'data'):
                data = result.data
                if hasattr(data, 'markdown') and data.markdown:
                    logger.info(f"✅ Single page access successful: {len(data.markdown)} chars")
                    return True
                elif hasattr(data, 'content') and data.content:
                    logger.info(f"✅ Single page access successful: {len(data.content)} chars")
                    return True
                else:
                    logger.warning("⚠️ Single page access failed - no content in data")
                    return False
            elif result and hasattr(result, 'content') and result.content:
                logger.info(f"✅ Single page access successful: {len(result.content)} chars")
                return True
            else:
                logger.warning("⚠️ Single page access failed - no content")
                logger.info(f"🔍 Result type: {type(result)}, attributes: {dir(result) if result else 'None'}")
                return False
                
        except Exception as e:
            logger.warning(f"⚠️ Single page access error: {str(e)}")
            # Try fallback format
            try:
                logger.info("🔄 Trying fallback API format...")
                result = self.firecrawl.scrape_url(url)
                if result and hasattr(result, 'content') and result.content:
                    logger.info(f"✅ Fallback scrape successful: {len(result.content)} chars")
                    return True
                else:
                    return False
            except Exception as fallback_error:
                logger.warning(f"⚠️ Fallback also failed: {str(fallback_error)}")
                return False
    
    def _log_crawl_details(self, result):
        """Detailed logging for debugging crawl issues."""
        logger.info(f"🔍 Crawl Result Analysis:")
        
        if not result:
            logger.info("   Result: None")
            return
            
        logger.info(f"   Success: {getattr(result, 'success', 'unknown')}")
        logger.info(f"   Status: {getattr(result, 'status', 'unknown')}")
        logger.info(f"   Total: {getattr(result, 'total', 0)}")
        logger.info(f"   Completed: {getattr(result, 'completed', 0)}")
        logger.info(f"   Credits Used: {getattr(result, 'creditsUsed', 0)}")
        
        if hasattr(result, 'data') and result.data:
            logger.info(f"   Data Length: {len(result.data)}")
            for i, page in enumerate(result.data[:3]):  # Log first 3 pages
                page_url = getattr(page, 'url', 'no-url')
                logger.info(f"   Page {i+1}: {page_url}")
        else:
            logger.warning("   ⚠️ No data in result")
    
    def _fallback_scrape(self, url: str) -> Optional[Dict[str, Any]]:
        """Fallback using direct HTTP requests when Firecrawl fails."""
        try:
            import requests
            from bs4 import BeautifulSoup
            
            logger.info(f"🔄 Attempting direct HTTP scrape of: {url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract main content
            main_content = (
                soup.find('main') or 
                soup.find('article') or 
                soup.find('div', class_='content') or 
                soup.body
            )
            
            if main_content:
                content_text = main_content.get_text(strip=True)
                title = soup.title.string if soup.title else ''
                
                logger.info(f"✅ Direct scrape successful: {len(content_text)} chars")
                
                return {
                    'url': url,
                    'content': content_text,
                    'html': str(main_content),
                    'title': title,
                    'method': 'direct_http'
                }
            else:
                logger.warning("⚠️ Direct scrape found no main content")
                return None
                
        except Exception as e:
            logger.error(f"❌ Direct scrape failed: {str(e)}")
            return None
    
    def _process_fallback_content(self, content_data: Dict[str, Any]):
        """Process content from fallback scraping method."""
        try:
            logger.info(f"📦 Processing fallback content from {content_data['url']}")
            
            # Create content data structure similar to Firecrawl format
            processed_content = {
                'content_id': str(uuid.uuid4()),
                'url': content_data['url'],
                'domain': self._get_domain_from_url(content_data['url']),
                'text': content_data['content'],
                'html': content_data.get('html', ''),
                'crawl_id': self.crawl_id,
                'extracted_at': datetime.utcnow(),
                'metadata': {
                    'title': content_data.get('title', ''),
                    'author': None,
                    'description': None,
                    'keywords': [],
                    'language': 'en',
                    'content_type': 'webpage',
                    'publication_date': None,
                    'last_modified': None,
                    'categories': [],
                    'tags': [],
                    'source_url': content_data['url'],
                    'crawl_metadata': {
                        'extraction_method': content_data.get('method', 'fallback'),
                        'fallback_reason': 'firecrawl_failed'
                    }
                }
            }
            
            # Save to database
            self.db.save_content(processed_content, self.org_id)
            self.content_extracted += 1
            self.pages_crawled += 1
            
            logger.info(f"✅ Saved fallback content from {content_data['url']}")
            logger.info(f"📊 Fallback Results: 1 page crawled and extracted")
            
        except Exception as e:
            logger.error(f"❌ Failed to process fallback content: {str(e)}")
            self.pages_failed += 1
    
    def stop(self):
        """Stop the crawler (not applicable for Firecrawl)."""
        logger.info("🛑 Firecrawl crawl stop requested")
