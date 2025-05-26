#!/usr/bin/env python
"""
Simple script to clear all crawls from the database.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.session import get_db_session
from database.models import Crawl, Content, ContentChunk

def clear_all_crawls():
    """Clear all crawls and associated content from the database."""
    print("WARNING: This will delete all crawls and content from the database.")
    confirm = input("Type 'yes' to confirm: ")
    
    if confirm.lower() != 'yes':
        print("Operation cancelled.")
        return
    
    # Get database session
    session = get_db_session()
    if hasattr(session, '__next__'):
        session = next(session)
    
    try:
        # Count records
        chunk_count = session.query(ContentChunk).count()
        content_count = session.query(Content).count()
        crawl_count = session.query(Crawl).count()
        
        print(f"Found {chunk_count} chunks, {content_count} content items, and {crawl_count} crawls.")
        
        # Delete chunks first (they reference content)
        if chunk_count > 0:
            print(f"Deleting {chunk_count} content chunks...")
            session.query(ContentChunk).delete()
        
        # Delete content (references crawls)
        if content_count > 0:
            print(f"Deleting {content_count} content items...")
            session.query(Content).delete()
        
        # Delete crawls
        if crawl_count > 0:
            print(f"Deleting {crawl_count} crawl records...")
            session.query(Crawl).delete()
        
        # Commit the changes
        session.commit()
        print("All crawls and associated data successfully deleted.")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    clear_all_crawls()
