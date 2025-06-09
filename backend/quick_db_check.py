#!/usr/bin/env python
"""
Simple database content check
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
    # Check org distribution
    orgs = session.query(Content.org_id, session.func.count(Content.id)).group_by(Content.org_id).all()
    print("\\nOrganizations:")
    for org_id, count in orgs:
        print(f"  {org_id}: {count} items")
    
    # Check domains
    domains = session.query(Content.domain, session.func.count(Content.id)).group_by(Content.domain).all()
    print("\\nDomains:")
    for domain, count in domains:
        print(f"  {domain}: {count} items")
    
    # Check content types
    types = session.query(Content.content_type, session.func.count(Content.id)).group_by(Content.content_type).all()
    print("\\nContent Types:")
    for ctype, count in types:
        print(f"  {ctype}: {count} items")
        
    # Show sample
    sample = session.query(Content).first()
    print(f"\\nSample content:")
    print(f"  URL: {sample.url}")
    print(f"  Domain: {sample.domain}")
    print(f"  Org ID: {sample.org_id}")
    print(f"  Type: {sample.content_type}")
else:
    print("❌ No content found! You need to crawl buf.build first.")

session.close()
