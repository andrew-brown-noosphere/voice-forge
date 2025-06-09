#!/usr/bin/env python
"""
Quick script to check what content exists in the database for debugging.
"""
import sys
import os
import logging

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.session import get_db_session
from database.models import Content
from database.db import Database

def check_content_debug():
    """Check what content exists in the database."""
    print("🔍 Checking database content...")
    
    # Get database session
    session = next(get_db_session())
    db = Database(session)
    
    try:
        # Check total content count
        content_count = session.query(Content).count()
        print(f"📊 Total content items: {content_count}")
        
        if content_count == 0:
            print("❌ No content found in database!")
            print("💡 You need to crawl buf.build first")
            return
        
        # Check content by org_id
        org_content = session.query(Content.org_id, session.query(Content).filter(Content.org_id == Content.org_id).count()).distinct().all()
        print("\n📋 Content by organization:")
        for row in session.query(Content.org_id).distinct().all():
            org_id = row[0]
            org_count = session.query(Content).filter(Content.org_id == org_id).count()
            print(f"  Org ID: {org_id} - {org_count} items")
        
        # Check domains
        domains = session.query(Content.domain).distinct().all()
        print(f"\n🌐 Domains found: {[d[0] for d in domains]}")
        
        # Sample content
        sample_content = session.query(Content).limit(3).all()
        print("\n📄 Sample content:")
        for content in sample_content:
            print(f"  ID: {content.id}")
            print(f"  URL: {content.url}")
            print(f"  Domain: {content.domain}")
            print(f"  Org ID: {content.org_id}")
            print(f"  Title: {content.title}")
            print(f"  Text length: {len(content.text) if content.text else 0}")
            print(f"  Content type: {content.content_type}")
            print("  ---")
        
        # Test the search_content method
        print("\n🔍 Testing search_content method...")
        
        # Get a real org_id from the database
        real_org_id = session.query(Content.org_id).first()
        if real_org_id:
            test_org_id = real_org_id[0]
            print(f"Using org_id: {test_org_id}")
            
            # Test the search_content method
            test_query = {
                'org_id': test_org_id,
                'content_types': ['landing_page', 'product_description', 'blog_post', 'about_page', 'feature_page'],
                'limit': 5,
                'sort_by': 'relevance',
                'min_length': 100,
                'include_metadata': True
            }
            
            search_results = db.search_content(test_query)
            print(f"✅ search_content returned {len(search_results)} results")
            
            if search_results:
                print("📝 First result sample:")
                first_result = search_results[0]
                print(f"  Content ID: {first_result.get('content_id')}")
                print(f"  URL: {first_result.get('url')}")
                print(f"  Domain: {first_result.get('domain')}")
                print(f"  Content type: {first_result.get('content_type')}")
                print(f"  Text length: {len(first_result.get('text', ''))}")
                print(f"  Text preview: {first_result.get('text', '')[:200]}...")
            else:
                print("❌ search_content returned no results with the test query")
                
                # Try with no filters
                simple_query = {'org_id': test_org_id, 'limit': 5}
                simple_results = db.search_content(simple_query)
                print(f"🔄 Simple query returned {len(simple_results)} results")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    check_content_debug()
