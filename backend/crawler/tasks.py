"""
Celery tasks for web crawling operations.

This module defines distributed tasks for handling web crawling
operations that can run asynchronously across multiple workers.
"""
import logging
from typing import Dict, Any
from celery import current_task
from celery_app import celery_app  # Remove RETRY_KWARGS import
from crawler.service import CrawlerService
from database.session import get_db_session

logger = logging.getLogger(__name__)

@celery_app.task(bind=True)  # Remove RETRY_KWARGS to avoid serialization issues
def crawl_website_task(self, crawl_id: str, domain: str, config: Dict[str, Any], org_id: str):
    """
    Celery task to crawl a website.
    
    Args:
        crawl_id: Unique identifier for the crawl
        domain: Domain to crawl
        config: Crawl configuration
        org_id: Organization ID for multi-tenant isolation
    
    Returns:
        Crawl status dictionary
    """
    try:
        logger.info(f"🚀 Starting crawl task for {domain} (ID: {crawl_id})")
        
        # Get database session and wrap it
        db_session = get_db_session()
        
        try:
            # Import and create Database wrapper
            from database.db import Database
            db = Database(db_session)
            
            # Initialize crawler service
            crawler_service = CrawlerService(db)
            
            # Run the crawl
            result = crawler_service.run_crawl_sync(
                crawl_id=crawl_id,
                domain=domain,
                config=config,
                org_id=org_id,
                task_callback=None  # Disable callback to avoid serialization issues
            )
            
            logger.info(f"✅ Crawl task completed for {domain} (ID: {crawl_id})")
            return result
            
        finally:
            db_session.close()
            
    except Exception as exc:
        error_msg = str(exc)
        logger.error(f"❌ Crawl task failed for {domain} (ID: {crawl_id}): {error_msg}", exc_info=True)
        
        # Simple error return instead of complex state updates
        return {
            "status": "failed",
            "error": error_msg,
            "crawl_id": crawl_id
        }

@celery_app.task(bind=True)  # Remove RETRY_KWARGS
def process_crawled_content_task(self, crawl_id: str, org_id: str):
    """
    Celery task to process crawled content for RAG.
    
    Args:
        crawl_id: Crawl ID to process content for
        org_id: Organization ID for multi-tenant isolation
    
    Returns:
        Processing status dictionary
    """
    try:
        logger.info(f"🔄 Starting content processing task for crawl {crawl_id}")
        
        # Get database session and wrap it
        db_session = get_db_session()
        
        try:
            # Import and create Database wrapper
            from database.db import Database
            db = Database(db_session)
            
            # Import processor service
            from processor.service import ProcessorService
            
            # Initialize processor service
            processor_service = ProcessorService(db)
            
            # Process all content from the crawl
            result = processor_service.process_crawl_for_rag(
                crawl_id=crawl_id,
                org_id=org_id,
                task_callback=None  # Remove problematic callback
            )
            
            logger.info(f"✅ Content processing completed for crawl {crawl_id}")
            return result
            
        finally:
            db_session.close()
            
    except Exception as exc:
        error_msg = str(exc)
        logger.error(f"❌ Content processing failed for crawl {crawl_id}: {error_msg}", exc_info=True)
        
        return {
            "status": "failed",
            "error": error_msg,
            "crawl_id": crawl_id
        }

@celery_app.task(bind=True)  # Remove RETRY_KWARGS
def cleanup_old_crawls_task(self, days_old: int = 30):
    """
    Celery task to clean up old crawl data.
    
    Args:
        days_old: Delete crawls older than this many days
    
    Returns:
        Cleanup summary
    """
    try:
        logger.info(f"🧹 Starting cleanup task for crawls older than {days_old} days")
        
        # Get database session and wrap it
        db_session = get_db_session()
        
        try:
            # Import and create Database wrapper
            from database.db import Database
            db = Database(db_session)
            
            # Initialize crawler service
            crawler_service = CrawlerService(db)
            
            # Perform cleanup
            result = crawler_service.cleanup_old_crawls(
                days_old=days_old,
                task_callback=None  # Remove problematic callback
            )
            
            logger.info(f"✅ Cleanup completed: {result}")
            return result
            
        finally:
            db_session.close()
            
    except Exception as exc:
        error_msg = str(exc)
        logger.error(f"❌ Cleanup task failed: {error_msg}", exc_info=True)
        
        return {
            "status": "failed",
            "error": error_msg
        }

@celery_app.task(bind=True)
def health_check_task(self):
    """
    Simple health check task to verify Celery is working.
    
    Returns:
        Health status dictionary
    """
    try:
        logger.info("🔍 Running Celery health check")
        
        import time
        time.sleep(1)  # Simulate some work
        
        result = {
            "status": "healthy",
            "task_id": str(current_task.request.id),
            "timestamp": time.time()
        }
        
        logger.info("✅ Celery health check passed")
        return result
        
    except Exception as exc:
        logger.error(f"❌ Health check failed: {str(exc)}")
        raise exc