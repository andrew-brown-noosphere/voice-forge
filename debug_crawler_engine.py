#!/usr/bin/env python3
"""
Direct crawler test - bypass Celery and test crawler engine directly
"""

import sys
import os
import logging

# Add the backend directory to Python path
sys.path.append('/Users/andrewbrown/Sites/noosphere/github/voice-forge/backend')

# Set up logging to see what's happening
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_crawler_directly():
    """Test the crawler engine directly without Celery"""
    
    print("🔍 DIRECT CRAWLER TEST")
    print("=" * 50)
    
    try:
        # Import required modules
        from crawler.engine import PlaywrightCrawler
        from api.models import CrawlConfig
        
        print("✅ Imports successful")
        
        # Create a simple config without include patterns
        config = CrawlConfig(
            max_depth=2,
            max_pages=3,  # Just crawl 3 pages for testing
            respect_robots_txt=True,
            delay=1.0,
            timeout=15,
            follow_external_links=False,
            exclude_patterns=[
                '.*/contact.*',
                '.*/admin.*',
                '.*\\.pdf$',
                '.*\\.jpg$',
                '.*\\.png$',
                '.*\\.css$',
                '.*\\.js$'
            ],
            include_patterns=[],  # Empty - should crawl everything
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        print("✅ Config created")
        print(f"   Max pages: {config.max_pages}")
        print(f"   Max depth: {config.max_depth}")
        print(f"   Include patterns: {config.include_patterns}")
        print(f"   Exclude patterns: {len(config.exclude_patterns)} patterns")
        
        # Mock database for testing
        class MockDB:
            def save_content(self, content_data, org_id):
                print(f"📄 MOCK: Would save content from {content_data['url']}")
                print(f"   Title: {content_data.get('metadata', {}).get('title', 'No title')}")
                print(f"   Content length: {len(content_data.get('text', ''))}")
                return True
        
        mock_db = MockDB()
        
        # Test with a simple domain first
        test_domain = "https://httpbin.org"
        crawl_id = "test-crawl-123"
        org_id = "test-org"
        
        print(f"\n🚀 Starting crawler test with {test_domain}")
        
        # Create crawler instance
        crawler = PlaywrightCrawler(
            domain=test_domain,
            config=config,
            db=mock_db,
            crawl_id=crawl_id,
            org_id=org_id
        )
        
        print("✅ Crawler instance created")
        
        # Check initial state
        progress = crawler.get_progress()
        print(f"📊 Initial progress:")
        print(f"   Pages crawled: {progress.pages_crawled}")
        print(f"   Pages discovered: {progress.pages_discovered}")
        print(f"   Pages failed: {progress.pages_failed}")
        print(f"   Current depth: {progress.current_depth}")
        
        # Run the crawler
        print(f"\n🔄 Running crawler...")
        crawler.crawl()
        
        # Check final state
        final_progress = crawler.get_progress()
        print(f"\n📊 Final progress:")
        print(f"   Pages crawled: {final_progress.pages_crawled}")
        print(f"   Pages discovered: {final_progress.pages_discovered}")
        print(f"   Pages failed: {final_progress.pages_failed}")
        print(f"   Current depth: {final_progress.current_depth}")
        print(f"   Content extracted: {final_progress.content_extracted}")
        
        if final_progress.pages_crawled > 0:
            print("✅ SUCCESS: Crawler worked!")
        else:
            print("❌ FAILURE: Still 0 pages crawled")
            
            # Debug the issue
            print(f"\n🔍 Debugging crawler state:")
            print(f"   Visited URLs: {len(crawler.visited_urls)}")
            print(f"   Queue: {len(crawler.queue)}")
            print(f"   Failed URLs: {len(crawler.failed_urls)}")
            
            if crawler.visited_urls:
                print(f"   Visited: {list(crawler.visited_urls)}")
            if crawler.failed_urls:
                print(f"   Failed: {list(crawler.failed_urls)}")
                
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running from the backend directory")
    except Exception as e:
        print(f"❌ Crawler error: {e}")
        import traceback
        traceback.print_exc()

def test_playwright_installation():
    """Test if Playwright is properly installed"""
    
    print(f"\n🎭 PLAYWRIGHT TEST")
    print("=" * 50)
    
    try:
        from playwright.sync_api import sync_playwright
        print("✅ Playwright import successful")
        
        # Test browser launch
        with sync_playwright() as p:
            print("🔄 Launching browser...")
            browser = p.chromium.launch(headless=True)
            print("✅ Browser launched successfully")
            
            context = browser.new_context()
            page = context.new_page()
            
            print("🔄 Testing page navigation...")
            response = page.goto("https://httpbin.org/html", timeout=10000)
            print(f"✅ Page loaded: {response.status}")
            
            title = page.title()
            print(f"✅ Page title: {title}")
            
            content = page.content()
            print(f"✅ Content length: {len(content)} chars")
            
            browser.close()
            print("✅ Browser closed successfully")
            
    except ImportError:
        print("❌ Playwright not installed")
        print("Run: pip install playwright && playwright install")
    except Exception as e:
        print(f"❌ Playwright error: {e}")

def test_celery_status():
    """Test Celery worker status"""
    
    print(f"\n⚡ CELERY TEST")
    print("=" * 50)
    
    try:
        # Try to import Celery
        from celery_app import celery_app
        print("✅ Celery app import successful")
        
        # Check if workers are active
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        
        if stats:
            print(f"✅ Active workers: {len(stats)}")
            for worker, info in stats.items():
                print(f"   Worker: {worker}")
        else:
            print("❌ No active Celery workers found")
            print("Start workers with: celery -A celery_app worker --loglevel=info")
            
    except ImportError as e:
        print(f"❌ Celery import error: {e}")
    except Exception as e:
        print(f"❌ Celery error: {e}")

if __name__ == "__main__":
    print("🚨 COMPREHENSIVE CRAWLER DEBUG")
    print("=" * 60)
    
    # Change to backend directory
    backend_dir = "/Users/andrewbrown/Sites/noosphere/github/voice-forge/backend"
    if os.path.exists(backend_dir):
        os.chdir(backend_dir)
        print(f"📁 Changed to directory: {backend_dir}")
    else:
        print(f"❌ Backend directory not found: {backend_dir}")
        sys.exit(1)
    
    # Run all tests
    test_playwright_installation()
    test_celery_status() 
    test_crawler_directly()
    
    print(f"\n🎯 DIAGNOSTIC COMPLETE")
    print("=" * 60)
