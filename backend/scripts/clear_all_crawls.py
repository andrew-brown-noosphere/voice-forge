#!/usr/bin/env python
"""
Script to clear/delete all crawls from the Voice Forge database.
This will remove all crawl records and associated content.
"""
import sys
import os
import logging
from datetime import datetime
import argparse

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def clear_all_crawls(dry_run=False):
    """
    Clear all crawls and their associated content from the database.
    
    Args:
        dry_run: If True, only show what would be deleted without actually deleting
    """
    try:
        # Import necessary modules
        from database.session import get_db_session
        from database.models import Crawl, Content, ContentChunk
        from sqlalchemy import func
        
        # Get database session
        session = get_db_session()
        if hasattr(session, '__next__'):
            session = next(session)
        
        # Start a transaction
        if not dry_run:
            logger.info("Starting database transaction")
        
        try:
            # Check how many records we're dealing with
            crawl_count = session.query(func.count(Crawl.id)).scalar()
            content_count = session.query(func.count(Content.id)).scalar()
            chunk_count = session.query(func.count(ContentChunk.id)).scalar()
            
            logger.info(f"Found {crawl_count} crawls, {content_count} content items, and {chunk_count} chunks")
            
            if dry_run:
                logger.info("DRY RUN: Would delete the following:")
                logger.info(f"- {chunk_count} content chunks")
                logger.info(f"- {content_count} content items")
                logger.info(f"- {crawl_count} crawl records")
                return
            
            # Delete chunks first (they reference content)
            if chunk_count > 0:
                logger.info(f"Deleting {chunk_count} content chunks...")
                session.query(ContentChunk).delete()
                logger.info("Content chunks deleted")
            
            # Delete content (references crawls)
            if content_count > 0:
                logger.info(f"Deleting {content_count} content items...")
                session.query(Content).delete()
                logger.info("Content items deleted")
            
            # Delete crawls
            if crawl_count > 0:
                logger.info(f"Deleting {crawl_count} crawl records...")
                session.query(Crawl).delete()
                logger.info("Crawl records deleted")
            
            # Commit the transaction
            session.commit()
            logger.info("All crawls and associated data successfully deleted")
            
        except Exception as e:
            logger.error(f"Error deleting crawls: {str(e)}")
            session.rollback()
            logger.info("Transaction rolled back, no changes made to the database")
            raise
        
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Failed to clear crawls: {str(e)}")

def vacuum_database():
    """
    Vacuum the database to reclaim space after deleting data.
    This is only relevant for SQLite databases.
    """
    try:
        # Import necessary modules
        from database.session import engine
        
        # Check if this is SQLite
        if 'sqlite' in str(engine.url):
            logger.info("SQLite database detected, vacuuming to reclaim space...")
            
            # Execute VACUUM
            connection = engine.connect()
            connection.execute("VACUUM")
            connection.close()
            
            logger.info("Database vacuumed successfully")
        else:
            logger.info("Not an SQLite database, skipping vacuum operation")
            
    except Exception as e:
        logger.error(f"Failed to vacuum database: {str(e)}")

if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(description="Clear all crawls from the Voice Forge database")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be deleted without actually deleting")
    parser.add_argument("--vacuum", action="store_true", help="Vacuum the database after deletion (SQLite only)")
    
    args = parser.parse_args()
    
    # Print warning and confirmation
    if not args.dry_run:
        logger.warning("!!! WARNING: This will permanently delete all crawls and content !!!")
        print("\n!!! WARNING: This will permanently delete all crawls and content !!!")
        confirmation = input("\nType 'yes' to confirm deletion: ")
        
        if confirmation.lower() != 'yes':
            print("Deletion cancelled.")
            sys.exit(0)
    
    # Clear crawls
    clear_all_crawls(dry_run=args.dry_run)
    
    # Vacuum if requested
    if args.vacuum and not args.dry_run:
        vacuum_database()
    
    logger.info("Operation completed")
