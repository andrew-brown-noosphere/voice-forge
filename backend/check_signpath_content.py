#!/usr/bin/env python
"""
Check for signpath.io content in database
"""
import os
import sys
sys.path.append('/Users/andrewbrown/Sites/noosphere/github/voice-forge/backend')

os.chdir('/Users/andrewbrown/Sites/noosphere/github/voice-forge/backend')

from database.session import get_db_session
from database.models import Content

# Get database session
session = next(get_db_session())

# Check total content
total = session.query(Content).count()
print(f"Total content: {total}")

if total > 0:
    # Check for signpath.io specifically
    signpath_content = session.query(Content).filter(Content.domain.like('%signpath%')).all()
    print(f"\n🎯 SignPath.io content: {len(signpath_content)} items")
    
    if signpath_content:
        print("\n📄 SignPath.io content details:")
        for content in signpath_content[:5]:  # Show first 5
            print(f"  URL: {content.url}")
            print(f"  Title: {content.title}")
            print(f"  Org ID: {content.org_id}")
            print(f"  Content Type: {content.content_type}")
            print(f"  Text Length: {len(content.text or '')}")
            print(f"  Text Preview: {(content.text or '')[:200]}...")
            print("  ---")
    
    # Check org distribution
    orgs = session.query(Content.org_id, session.func.count(Content.id)).group_by(Content.org_id).all()
    print("\n🏢 Organizations:")
    for org_id, count in orgs:
        print(f"  {org_id}: {count} items")
    
    # Check all domains
    domains = session.query(Content.domain, session.func.count(Content.id)).group_by(Content.domain).all()
    print("\n🌐 All Domains:")
    for domain, count in domains:
        print(f"  {domain}: {count} items")
    
    # Check content types
    types = session.query(Content.content_type, session.func.count(Content.id)).group_by(Content.content_type).all()
    print("\n📋 Content Types:")
    for ctype, count in types:
        print(f"  {ctype}: {count} items")
        
    # Check target org specifically
    target_org = "org_2xv0xClQv3WlCBhRahmK59pEzBY"
    target_org_content = session.query(Content).filter(Content.org_id == target_org).count()
    print(f"\n🎯 Content for your org {target_org}: {target_org_content} items")
    
    if target_org_content > 0:
        target_content = session.query(Content).filter(Content.org_id == target_org).all()
        print(f"\n📝 Your org's content:")
        for content in target_content[:3]:
            print(f"  URL: {content.url}")
            print(f"  Title: {content.title}")
            print(f"  Domain: {content.domain}")
            print(f"  Type: {content.content_type}")
            print(f"  Text: {(content.text or '')[:150]}...")
            print("  ---")
else:
    print("❌ No content found! You need to crawl content first.")

session.close()
