#!/usr/bin/env python3
"""
Enhanced crawler engine with debug logging to identify the 25-page limit issue.
"""

# Let's add debug logging to the PlaywrightCrawler class

debug_patch = '''
def crawl(self):
    """Run the crawler with enhanced debugging."""
    self.running = True
    
    # DEBUG: Log initial configuration
    logger.info(f"🔍 DEBUG: Starting crawl with config:")
    logger.info(f"  max_pages: {self.config.max_pages}")
    logger.info(f"  max_depth: {self.config.max_depth}")
    logger.info(f"  delay: {self.config.delay}")
    logger.info(f"  follow_external_links: {self.config.follow_external_links}")
    
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
                # DEBUG: Log current status
                logger.info(f"🔍 DEBUG: Queue length: {len(self.queue)}, Visited: {len(self.visited_urls)}")
                
                # Check if max pages limit reached
                if (self.config.max_pages is not None and 
                    len(self.visited_urls) >= self.config.max_pages):
                    logger.info(f"📊 DEBUG: Reached max_pages limit: {self.config.max_pages}")
                    logger.info(f"📊 DEBUG: Visited URLs: {len(self.visited_urls)}")
                    break
                
                # Get next URL from queue
                url, depth = self.queue.pop(0)
                
                # Skip if already visited
                if url in self.visited_urls:
                    continue
                
                # Check depth limit
                if depth > self.config.max_depth:
                    logger.info(f"📊 DEBUG: Skipping {url} - depth {depth} > max_depth {self.config.max_depth}")
                    continue
                
                # Update current depth
                self.current_depth = max(self.current_depth, depth)
                
                # DEBUG: Every 5 pages, log status
                if len(self.visited_urls) % 5 == 0:
                    logger.info(f"🔍 DEBUG: Progress - Visited: {len(self.visited_urls)}, Queue: {len(self.queue)}")
                
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
                        # Save content to database with org_id
                        content_data['crawl_id'] = self.crawl_id
                        content_data['org_id'] = self.org_id
                        content_data['extracted_at'] = datetime.now()
                        self.db.save_content(content_data, self.org_id)
                        self.content_extracted += 1
                    
                    # Extract links for further crawling
                    links = self._extract_links(html, url)
                    
                    # DEBUG: Log link discovery
                    if links:
                        logger.info(f"🔍 DEBUG: Found {len(links)} new links from {url}")
                    
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
    
    # DEBUG: Final status
    logger.info(f"📊 DEBUG: Crawl completed - Final status:")
    logger.info(f"  Pages crawled: {len(self.visited_urls)}")
    logger.info(f"  Pages discovered: {len(self.discovered_urls)}")
    logger.info(f"  Pages failed: {len(self.failed_urls)}")
    logger.info(f"  Content extracted: {self.content_extracted}")
    logger.info(f"  Max pages setting: {self.config.max_pages}")
    
    logger.info(f"Crawl completed: {len(self.visited_urls)} pages crawled, "
               f"{len(self.failed_urls)} failed, {self.content_extracted} content extracted")
'''

print("🔧 Enhanced Crawler Debug Patch")
print("=" * 50)
print()
print("To add debug logging to your crawler, replace the 'crawl' method")
print("in crawler/engine.py with the enhanced version above.")
print()
print("This will help identify:")
print("• What max_pages value is actually being used")
print("• When the limit is being reached")
print("• How many pages are being processed")
print("• Link discovery patterns")
print()
print("The debug logs will show in your console with 🔍 DEBUG prefix.")
