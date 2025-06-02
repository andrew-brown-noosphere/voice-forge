#!/usr/bin/env python3
"""
Quick diagnostic to check actual crawl configurations in database
"""

import os
import sys
import json
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

# Set up environment
os.environ['DATABASE_URL'] = 'postgresql://andrewbrown@localhost:5432/voice_forge'

try:
    from database.session import get_db_session
    from database.models import Crawl
    
    # Get database session
    db_session = get_db_session()
    
    print("🔍 Recent Crawls Analysis")
    print("=" * 50)
    
    # Get recent crawls
    crawls = db_session.query(Crawl).order_by(Crawl.start_time.desc()).limit(10).all()
    
    if not crawls:
        print("No crawls found.")
    else:
        for crawl in crawls:
            print(f"Crawl ID: {crawl.id[:8]}...")
            print(f"Domain: {crawl.domain}")
            print(f"State: {crawl.state}")
            print(f"Pages Crawled: {crawl.pages_crawled}")
            print(f"Pages Discovered: {crawl.pages_discovered}")
            
            # Parse config
            config = crawl.config
            if isinstance(config, dict):
                max_pages = config.get('max_pages', 'Not set')
                max_depth = config.get('max_depth', 'Not set')
                print(f"Config max_pages: {max_pages}")
                print(f"Config max_depth: {max_depth}")
                
                # Look for any 25 values
                config_str = json.dumps(config, indent=2)
                if '25' in config_str:
                    print("🚨 Found '25' in config:")
                    print(config_str)
            else:
                print(f"Config type: {type(config)}")
                print(f"Config: {config}")
            
            print("---")
    
    db_session.close()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
