#!/usr/bin/env python3
"""
Debug crawler issues by testing a simple crawl directly.
"""

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append('/Users/andrewbrown/Sites/noosphere/github/voice-forge/backend')

from crawler.engine import PlaywrightCrawler
from api.models import CrawlConfig

class MockDB:
    """Mock database for testing."""
    def save_content(self, content_data):
        print(f"📄 Would save content: {content_data.get('title', 'No title')} from {content_data.get('url', 'No URL')}")
    
    def update_crawl_status(self, status, org_id=None):
        print(f"📊 Status update: {status}")

def test_crawler():
    """Test the crawler directly."""
    print("🕷️ Testing Playwright Crawler")
    print("=" * 50)
    
    # Test configuration
    config = CrawlConfig(
        max_depth=1,
        max_pages=3,
        delay=1.0,
        timeout=30,
        user_agent="Mozilla/5.0 (compatible; VoiceForge/1.0)",
        follow_external_links=False,
        include_patterns=[],
        exclude_patterns=['\.pdf$', '\.jpg$', '\.png$', '\.gif$']
    )
    
    # Test domain
    domain = "https://example.com"
    crawl_id = "test_crawl_123"
    org_id = "test_org"
    
    print(f"🎯 Target: {domain}")
    print(f"📋 Config: max_depth={config.max_depth}, max_pages={config.max_pages}")
    
    try:
        # Create crawler
        db = MockDB()
        crawler = PlaywrightCrawler(
            domain=domain,
            config=config,
            db=db,
            crawl_id=crawl_id,
            org_id=org_id
        )
        
        print("🚀 Starting crawl...")
        
        # Run crawler
        crawler.crawl()
        
        # Get final progress
        progress = crawler.get_progress()
        print(f"✅ Crawl completed!")
        print(f"   Pages crawled: {progress.pages_crawled}")
        print(f"   Pages discovered: {progress.pages_discovered}")
        print(f"   Pages failed: {progress.pages_failed}")
        print(f"   Content extracted: {progress.content_extracted}")
        print(f"   Max depth reached: {progress.current_depth}")
        
    except Exception as e:
        print(f"❌ Crawler failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_crawler()
