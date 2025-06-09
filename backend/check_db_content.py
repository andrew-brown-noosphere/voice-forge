#!/usr/bin/env python
"""
Quick check of database content for debugging Signal Scan
"""
import sys
import os

# Add backend directory to path
backend_path = "/Users/andrewbrown/Sites/noosphere/github/voice-forge/backend"
sys.path.insert(0, backend_path)

# Change to backend directory
os.chdir(backend_path)

from database.session import get_db_session
from database.models import Content
from database.db import Database

def debug_content():
    """Debug what content exists in the database"""
    print("🔍 DEBUG: Checking VoiceForge database content...")
    
    session = next(get_db_session())
    db = Database(session)
    
    try:
        # 1. Check total content count
        total_content = session.query(Content).count()
        print(f"📊 Total content items in database: {total_content}")
        
        if total_content == 0:
            print("❌ NO CONTENT FOUND!")
            print("💡 You need to crawl buf.build first:")
            print("   1. Go to VoiceForge crawl interface")
            print("   2. Crawl docs.buf.build or buf.build")
            print("   3. Wait for content to be processed")
            return
        
        # 2. Check content by org_id
        print("\n📋 Content by organization:")
        org_counts = session.query(Content.org_id, session.func.count(Content.id)).group_by(Content.org_id).all()
        for org_id, count in org_counts:
            print(f"   Org: {org_id} - {count} items")
        
        # 3. Check domains
        print("\n🌐 Content by domain:")
        domain_counts = session.query(Content.domain, session.func.count(Content.id)).group_by(Content.domain).all()
        for domain, count in domain_counts:
            print(f"   Domain: {domain} - {count} items")
        
        # 4. Check content types
        print("\n📄 Content by type:")
        type_counts = session.query(Content.content_type, session.func.count(Content.id)).group_by(Content.content_type).all()
        for content_type, count in type_counts:
            print(f"   Type: {content_type} - {count} items")
        
        # 5. Test specific org search
        target_org = "org_2xv0xClQv3WlCBhRahmK59pEzBY"
        org_content = session.query(Content).filter(Content.org_id == target_org).count()
        print(f"\n🎯 Content for target org {target_org}: {org_content} items")
        
        if org_content == 0:
            print("❌ No content found for your org ID!")
            print("💡 This means either:")
            print("   1. Content hasn't been crawled yet")
            print("   2. Content was crawled under a different org ID")
            print("   3. You need to crawl buf.build content first")
        
        # 6. Test search_content method
        print("\n🔍 Testing search_content method...")
        test_query = {
            'org_id': target_org,
            'limit': 5,
            'include_metadata': True
        }
        
        results = db.search_content(test_query)
        print(f"✅ search_content (no filters) returned: {len(results)} results")
        
        # 7. Sample some content to understand the data
        if total_content > 0 and total_content <= 10:
            print("\n📝 Sample content (first 3 items):")
            sample_content = session.query(Content).limit(3).all()
            for i, content in enumerate(sample_content, 1):
                print(f"   {i}. ID: {content.id}")
                print(f"      URL: {content.url}")
                print(f"      Domain: {content.domain}")
                print(f"      Org ID: {content.org_id}")
                print(f"      Title: {content.title}")
                print(f"      Content Type: {content.content_type}")
                print(f"      Text Length: {len(content.text) if content.text else 0}")
                print(f"      Text Preview: {(content.text or '')[:100]}...")
                print()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    debug_content()
