#!/usr/bin/env python3
"""
Diagnostic script to check crawl limits and find the source of the 25-page limit.
"""

import os
import sys
import json
import logging
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.append(str(backend_dir))

from api.models import CrawlConfig
from database.session import get_db_session
from database.db import Database

def check_default_config():
    """Check the default crawl configuration."""
    print("🔍 Checking Default Crawl Configuration")
    print("=" * 50)
    
    # Create default config
    default_config = CrawlConfig()
    
    print(f"Default max_pages: {default_config.max_pages}")
    print(f"Default max_depth: {default_config.max_depth}")
    print(f"Default delay: {default_config.delay}")
    print(f"Default timeout: {default_config.timeout}")
    print(f"Default follow_external_links: {default_config.follow_external_links}")
    print()

def check_recent_crawls():
    """Check recent crawls to see their configurations and results."""
    print("🔍 Checking Recent Crawls")
    print("=" * 50)
    
    try:
        # Get database session
        db_session = get_db_session()
        db = Database(db_session)
        
        # Get recent crawls (this will need to be adjusted for your org_id)
        # For now, let's check the database structure
        from database.models import Crawl
        
        # Get some recent crawls
        crawls = db_session.query(Crawl).order_by(Crawl.start_time.desc()).limit(5).all()
        
        if not crawls:
            print("No crawls found in database.")
            return
        
        for crawl in crawls:
            print(f"Crawl ID: {crawl.id}")
            print(f"Domain: {crawl.domain}")
            print(f"State: {crawl.state}")
            print(f"Pages Crawled: {crawl.pages_crawled}")
            print(f"Pages Discovered: {crawl.pages_discovered}")
            print(f"Config: {crawl.config}")
            
            # Check if max_pages is set in config
            if isinstance(crawl.config, dict):
                max_pages = crawl.config.get('max_pages')
                print(f"Config max_pages: {max_pages}")
            
            print(f"Start Time: {crawl.start_time}")
            print(f"End Time: {crawl.end_time}")
            print("---")
            
        db_session.close()
        
    except Exception as e:
        print(f"Error checking crawls: {e}")

def check_environment_variables():
    """Check for any environment variables that might affect crawling."""
    print("🔍 Checking Environment Variables")
    print("=" * 50)
    
    crawl_related_vars = [
        'MAX_PAGES', 'CRAWL_MAX_PAGES', 'CRAWLER_MAX_PAGES',
        'MAX_CRAWL_PAGES', 'VOICEFORGE_MAX_PAGES',
        'DEFAULT_MAX_PAGES', 'CRAWL_LIMIT'
    ]
    
    found_vars = []
    for var in crawl_related_vars:
        value = os.environ.get(var)
        if value is not None:
            found_vars.append((var, value))
            print(f"{var}: {value}")
    
    if not found_vars:
        print("No crawl-related environment variables found.")
    print()

def check_config_files():
    """Check for any configuration files that might set limits."""
    print("🔍 Checking Configuration Files")
    print("=" * 50)
    
    config_files = [
        '.env',
        'config.json',
        'crawler.json',
        'settings.json',
        'crawler_config.json'
    ]
    
    for config_file in config_files:
        config_path = backend_dir / config_file
        if config_path.exists():
            print(f"Found {config_file}:")
            try:
                with open(config_path, 'r') as f:
                    content = f.read()
                    if '25' in content or 'max_pages' in content or 'limit' in content.lower():
                        print(f"  Content contains potential limits:")
                        lines = content.split('\n')
                        for i, line in enumerate(lines, 1):
                            if '25' in line or 'max_pages' in line or 'limit' in line.lower():
                                print(f"  Line {i}: {line.strip()}")
                    else:
                        print(f"  No obvious limits found in {config_file}")
            except Exception as e:
                print(f"  Error reading {config_file}: {e}")
            print()
    
    if not any((backend_dir / f).exists() for f in config_files):
        print("No configuration files found.")
    print()

def diagnose_crawl_limit():
    """Main diagnostic function."""
    print("🔧 VoiceForge Crawl Limit Diagnostic")
    print("=" * 50)
    print()
    
    check_default_config()
    check_environment_variables()
    check_config_files()
    check_recent_crawls()
    
    print("🔍 INVESTIGATION STEPS:")
    print("1. Check if the frontend is sending max_pages: 25 in the request")
    print("2. Check if there's a validation rule limiting max_pages")
    print("3. Check if there's a database constraint")
    print("4. Check if there's a middleware or decorator limiting pages")
    print("5. Check if the Playwright crawler has internal limits")
    print()
    
    print("📝 RECOMMENDED DEBUGGING:")
    print("1. Add logging to api/main.py to see incoming crawl requests")
    print("2. Add logging to crawler/engine.py to see the actual config")
    print("3. Check the browser developer tools for the frontend request")
    print("4. Look at the database crawl records to see stored configs")
    print()

if __name__ == "__main__":
    diagnose_crawl_limit()
