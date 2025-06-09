"""
Crawler service implementation.
Enhanced with Celery distributed task processing and automated RAG optimization.
"""
import os
import logging
import asyncio
import time
from datetime import datetime
from typing import Dict, List, Optional, Callable
from concurrent.futures import ThreadPoolExecutor

from crawler.engine import PlaywrightCrawler
from crawler.scrapingbee_engine import ScrapingBeeCrawler
from api.models import CrawlRequest, CrawlStatus, CrawlState, CrawlConfig, CrawlProgress

logger = logging.getLogger(__name__)

# Try to import Firecrawl (might fail due to Pydantic conflict)
try:
    from crawler.firecrawl_engine import FirecrawlCrawler
    FIRECRAWL_AVAILABLE = True
    logger.info("✅ Firecrawl imported successfully")
except Exception as e:
    logger.warning(f"⚠️ Firecrawl not available: {e}")
    FIRECRAWL_AVAILABLE = False
    # Create a dummy class to prevent import errors
    class FirecrawlCrawler:
        def __init__(self, *args, **kwargs):
            raise ValueError("Firecrawl is not available due to dependency conflicts")

class CrawlerService:
    """Service for managing website crawls with Celery task queue integration."""
    
    def __init__(self, db):
        """Initialize the crawler service."""
        self.db = db
        self.active_crawls = {}  # Dict[str, PlaywrightCrawler]
        self.crawl_statuses = {}  # Dict[str, CrawlStatus]
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Try to import Celery for distributed processing
        self.use_celery = self._init_celery()
        
    def _init_celery(self) -> bool:
        """Initialize Celery if available."""
        try:
            from celery_app import celery_app
            from crawler.tasks import crawl_website_task
            self.celery_app = celery_app
            self.crawl_task = crawl_website_task
            logger.info("✅ Celery initialized for distributed crawling")
            return True
        except ImportError:
            logger.warning("⚠️ Celery not available - using synchronous processing")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to initialize Celery: {e}")
            return False
    
    def init_crawl(self, crawl_id: str, request: CrawlRequest, org_id: str) -> CrawlStatus:
        """Initialize a new crawl job."""
        status = CrawlStatus(
            crawl_id=crawl_id,
            domain=request.domain,
            state=CrawlState.PENDING,
            progress=CrawlProgress(),
            config=request.config,
            start_time=None,
            end_time=None,
            error=None
        )
        
        # Save crawl status to both memory and database
        self.crawl_statuses[crawl_id] = status
        self.db.save_crawl_status(status, org_id)
        
        return status
    
    async def run_crawl(self, crawl_id: str, domain: str, config: CrawlConfig, org_id: str):
        """
        Run a crawl job using Celery if available, otherwise run synchronously.
        Enhanced with automated RAG optimization integration.
        """
        if self.use_celery:
            # Use Celery for distributed processing
            logger.info(f"🚀 Starting distributed crawl {crawl_id} for domain {domain}")
            
            # Update status to running
            status = self.crawl_statuses.get(crawl_id)
            if status:
                status.state = CrawlState.RUNNING
                status.start_time = datetime.now()
                self.db.update_crawl_status(status, org_id)
            
            # Submit to Celery
            try:
                task_result = self.crawl_task.delay(
                    crawl_id=crawl_id,
                    domain=domain,
                    config=config.dict(),
                    org_id=org_id
                )
                
                logger.info(f"✅ Crawl task {crawl_id} submitted to Celery: {task_result.id}")
                
                # Store task ID for monitoring
                if status:
                    status.task_id = task_result.id
                    self.db.update_crawl_status(status, org_id)
                    
                return task_result
                
            except Exception as e:
                logger.error(f"❌ Failed to submit crawl task {crawl_id} to Celery: {e}")
                # Fall back to synchronous processing
                return await self._run_crawl_sync(crawl_id, domain, config, org_id)
        else:
            # Run synchronously
            return await self._run_crawl_sync(crawl_id, domain, config, org_id)
    
    async def _run_crawl_sync(self, crawl_id: str, domain: str, config: CrawlConfig, org_id: str):
        """
        Run a crawl job. This method is intended to be run in a background task.
        Enhanced with automated RAG optimization integration.
        """
        try:
            logger.info(f"🚀 Starting crawl {crawl_id} for domain {domain}")
            
            # Update status to running
            status = self.crawl_statuses.get(crawl_id)
            if not status:
                logger.error(f"❌ Crawl status not found for {crawl_id}")
                return
                
            status.state = CrawlState.RUNNING
            status.start_time = datetime.now()
            self.db.update_crawl_status(status, org_id)
            
            logger.info(f"✅ Updated crawl {crawl_id} status to RUNNING at {status.start_time}")
            
            # 🔍 DEBUG: Log config before creating crawler
            logger.warning(f"🔍 SERVICE DEBUG: About to create crawler with config:")
            logger.warning(f"  config.max_pages: {config.max_pages}")
            logger.warning(f"  config.max_depth: {config.max_depth}")
            logger.warning(f"  config.delay: {config.delay}")
            logger.warning(f"  config type: {type(config)}")
            
            # Choose crawler engine based on environment and availability
            crawler_engine = os.getenv('CRAWLER_ENGINE', 'firecrawl').lower()  # Default to Firecrawl
            
            if crawler_engine == 'firecrawl' and FIRECRAWL_AVAILABLE:
                logger.info(f"🔥 Using Firecrawl engine for {crawl_id}")
                crawler = FirecrawlCrawler(
                    domain=domain,
                    config=config,
                    db=self.db,
                    crawl_id=crawl_id,
                    org_id=org_id
                )
            elif crawler_engine == 'scrapingbee' and os.getenv('SCRAPINGBEE_API_KEY'):
                logger.info(f"🐝 Using ScrapingBee engine for {crawl_id}")
                crawler = ScrapingBeeCrawler(
                    domain=domain,
                    config=config,
                    db=self.db,
                    crawl_id=crawl_id,
                    org_id=org_id
                )
            else:
                logger.info(f"🕷️ Using Playwright engine for {crawl_id}")
                crawler = PlaywrightCrawler(
                    domain=domain,
                    config=config,
                    db=self.db,
                    crawl_id=crawl_id,
                    org_id=org_id
                )
            
            # Store crawler reference for potential cancellation
            self.active_crawls[crawl_id] = crawler
            
            logger.info(f"🕷️ Starting crawler for {crawl_id}")
            
            # Run the crawler in a thread since it's synchronous
            import asyncio
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(self.executor, crawler.crawl)
            
            logger.info(f"🎉 Crawl {crawl_id} completed successfully")
            
            # Update status on completion
            status.state = CrawlState.COMPLETED
            status.end_time = datetime.now()
            status.progress = crawler.get_progress()
            
            # 🆕 ADD: Trigger automated RAG optimization after successful crawl
            try:
                from automated_rag_integration import RAGIntegrationHooks
                
                crawl_results = {
                    'pages_crawled': status.progress.pages_crawled,
                    'content_extracted': status.progress.content_extracted,
                    'pages_failed': status.progress.pages_failed,
                    'pages_discovered': status.progress.pages_discovered
                }
                
                logger.info(f"🧠 Checking RAG optimization for crawl {crawl_id}")
                rag_result = RAGIntegrationHooks.on_crawl_completed(crawl_id, org_id, crawl_results)
                
                if rag_result['status'] == 'processing':
                    logger.info(f"🚀 RAG optimization triggered for org {org_id} after crawl {crawl_id}")
                elif rag_result['status'] == 'not_needed':
                    logger.info(f"⏭️ RAG optimization not needed for org {org_id}: {rag_result.get('reason', 'unknown')}")
                else:
                    logger.info(f"📊 RAG optimization result for org {org_id}: {rag_result['status']}")
                    
            except Exception as e:
                logger.warning(f"⚠️ RAG optimization check failed for crawl {crawl_id}: {e}")
                # Don't fail the crawl if RAG optimization check fails
                
        except Exception as e:
            logger.error(f"💥 Crawl {crawl_id} failed: {str(e)}", exc_info=True)
            
            # Update status on failure
            status = self.crawl_statuses.get(crawl_id)
            if status:
                status.state = CrawlState.FAILED
                status.end_time = datetime.now()
                status.error = str(e)
        
        finally:
            # Clean up and save final status
            if crawl_id in self.active_crawls:
                del self.active_crawls[crawl_id]
            
            if status:
                self.db.update_crawl_status(status, org_id)
                logger.info(f"📊 Final status for crawl {crawl_id}: {status.state}")
    
    def run_crawl_sync(self, crawl_id: str, domain: str, config: Dict, org_id: str, task_callback: Optional[Callable] = None):
        """
        Synchronous version of crawl for Celery tasks.
        
        Args:
            crawl_id: Unique crawl identifier
            domain: Domain to crawl
            config: Crawl configuration dictionary
            org_id: Organization ID
            task_callback: Optional callback for task state updates
        
        Returns:
            Crawl results dictionary
        """
        try:
            logger.info(f"🚀 Starting synchronous crawl {crawl_id} for domain {domain}")
            
            if task_callback:
                task_callback("PROGRESS", {"status": "Initializing crawler", "progress": 10})
            
            # Get or create crawl status
            status = self.crawl_statuses.get(crawl_id)
            if not status:
                # Create status if it doesn't exist
                from api.models import CrawlConfig
                config_obj = CrawlConfig(**config)
                status = CrawlStatus(
                    crawl_id=crawl_id,
                    domain=domain,
                    state=CrawlState.RUNNING,
                    progress=CrawlProgress(),
                    config=config_obj,
                    start_time=datetime.now(),
                    end_time=None,
                    error=None
                )
                self.crawl_statuses[crawl_id] = status
            
            status.state = CrawlState.RUNNING
            status.start_time = datetime.now()
            self.db.update_crawl_status(status, org_id)
            
            if task_callback:
                task_callback("PROGRESS", {"status": "Starting crawler", "progress": 20})
            
            # Initialize crawler
            from api.models import CrawlConfig
            config_obj = CrawlConfig(**config) if isinstance(config, dict) else config
            
            # 🔍 DEBUG: Log sync config before creating crawler
            logger.warning(f"🔍 SERVICE SYNC DEBUG: About to create crawler with config:")
            logger.warning(f"  config_obj.max_pages: {config_obj.max_pages}")
            logger.warning(f"  config_obj.max_depth: {config_obj.max_depth}")
            logger.warning(f"  config_obj type: {type(config_obj)}")
            logger.warning(f"  original config dict: {config}")
            
            # Choose crawler engine
            crawler_engine = os.getenv('CRAWLER_ENGINE', 'firecrawl').lower()  # Default to Firecrawl
            
            if crawler_engine == 'firecrawl' and FIRECRAWL_AVAILABLE:
                logger.info(f"🔥 Using Firecrawl engine for sync crawl {crawl_id}")
                crawler = FirecrawlCrawler(
                    domain=domain,
                    config=config_obj,
                    db=self.db,
                    crawl_id=crawl_id,
                    org_id=org_id
                )
            elif crawler_engine == 'scrapingbee' and os.getenv('SCRAPINGBEE_API_KEY'):
                logger.info(f"🐝 Using ScrapingBee engine for sync crawl {crawl_id}")
                crawler = ScrapingBeeCrawler(
                    domain=domain,
                    config=config_obj,
                    db=self.db,
                    crawl_id=crawl_id,
                    org_id=org_id
                )
            else:
                logger.info(f"🕷️ Using Playwright engine for sync crawl {crawl_id}")
                crawler = PlaywrightCrawler(
                    domain=domain,
                    config=config_obj,
                    db=self.db,
                    crawl_id=crawl_id,
                    org_id=org_id
                )
            
            # Store crawler reference
            self.active_crawls[crawl_id] = crawler
            
            if task_callback:
                task_callback("PROGRESS", {"status": "Crawling website", "progress": 30})
            
            # Run the crawler synchronously
            crawler.crawl()
            
            if task_callback:
                task_callback("PROGRESS", {"status": "Crawl completed", "progress": 90})
            
            # Update status on completion
            status.state = CrawlState.COMPLETED
            status.end_time = datetime.now()
            status.progress = crawler.get_progress()
            
            # Trigger RAG optimization
            try:
                from automated_rag_integration import RAGIntegrationHooks
                
                crawl_results = {
                    'pages_crawled': status.progress.pages_crawled,
                    'content_extracted': status.progress.content_extracted,
                    'pages_failed': status.progress.pages_failed,
                    'pages_discovered': status.progress.pages_discovered
                }
                
                if task_callback:
                    task_callback("PROGRESS", {"status": "Optimizing for AI", "progress": 95})
                
                rag_result = RAGIntegrationHooks.on_crawl_completed(crawl_id, org_id, crawl_results)
                logger.info(f"🧠 RAG optimization result: {rag_result['status']}")
                
            except Exception as e:
                logger.warning(f"⚠️ RAG optimization failed: {e}")
            
            # Final status update
            self.db.update_crawl_status(status, org_id)
            
            if task_callback:
                task_callback("SUCCESS", {"status": "Crawl completed successfully", "progress": 100})
            
            result = {
                "crawl_id": crawl_id,
                "status": "completed",
                "pages_crawled": status.progress.pages_crawled,
                "content_extracted": status.progress.content_extracted,
                "duration": (status.end_time - status.start_time).total_seconds()
            }
            
            logger.info(f"✅ Synchronous crawl {crawl_id} completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"💥 Synchronous crawl {crawl_id} failed: {str(e)}")
            
            # Update status on failure
            if status:
                status.state = CrawlState.FAILED
                status.end_time = datetime.now()
                status.error = str(e)
                self.db.update_crawl_status(status, org_id)
            
            if task_callback:
                task_callback("FAILURE", {"status": f"Crawl failed: {str(e)}", "error": str(e)})
            
            raise e
            
        finally:
            # Clean up
            if crawl_id in self.active_crawls:
                del self.active_crawls[crawl_id]
    
    def get_crawl_status(self, crawl_id: str, org_id: str) -> Optional[CrawlStatus]:
        """Get the current status of a crawl job."""
        # Try in-memory cache first
        if crawl_id in self.crawl_statuses:
            status = self.crawl_statuses[crawl_id]
            
            # For active crawls, update the progress
            if crawl_id in self.active_crawls:
                status.progress = self.active_crawls[crawl_id].get_progress()
            
            return status
        
        # Otherwise fetch from database
        status = self.db.get_crawl_status(crawl_id, org_id)
        if status:
            self.crawl_statuses[crawl_id] = status
        
        return status
    
    def cancel_crawl(self, crawl_id: str, org_id: str) -> bool:
        """Cancel an ongoing crawl job."""
        if crawl_id not in self.active_crawls:
            return False
        
        try:
            # Signal the crawler to stop
            self.active_crawls[crawl_id].stop()
            
            # Update status
            status = self.crawl_statuses[crawl_id]
            status.state = CrawlState.CANCELLED
            status.end_time = datetime.now()
            
            # Clean up
            del self.active_crawls[crawl_id]
            
            # Save updated status
            self.db.update_crawl_status(status, org_id)
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to cancel crawl {crawl_id}: {str(e)}")
            return False
    
    def delete_crawl(self, crawl_id: str, org_id: str) -> bool:
        """Delete a crawl job and its associated content from the database."""
        try:
            logger.info(f"Deleting crawl {crawl_id} for organization {org_id}")
            
            # First, cancel if it's an active crawl
            if crawl_id in self.active_crawls:
                logger.info(f"Cancelling active crawl {crawl_id} before deletion")
                self.cancel_crawl(crawl_id, org_id)
            
            # Remove from memory cache
            if crawl_id in self.crawl_statuses:
                del self.crawl_statuses[crawl_id]
            
            # Delete from database
            from database.models import ContentChunk, Content, Crawl
            session = self.db.session
            
            # Find the crawl record
            crawl_record = session.query(Crawl).filter(
                Crawl.id == crawl_id,
                Crawl.org_id == org_id
            ).first()
            
            if not crawl_record:
                logger.warning(f"Crawl {crawl_id} not found in database for org {org_id}")
                return False
            
            # Get all content associated with this crawl
            content_items = session.query(Content).filter(
                Content.crawl_id == crawl_id,
                Content.org_id == org_id
            ).all()
            
            # Delete chunks first (foreign key constraint)
            for content_item in content_items:
                chunk_count = session.query(ContentChunk).filter(
                    ContentChunk.content_id == content_item.id
                ).delete()
                logger.info(f"Deleted {chunk_count} chunks for content {content_item.id}")
            
            # Delete content items
            content_count = session.query(Content).filter(
                Content.crawl_id == crawl_id,
                Content.org_id == org_id
            ).delete()
            logger.info(f"Deleted {content_count} content items for crawl {crawl_id}")
            
            # Delete the crawl record
            session.delete(crawl_record)
            session.commit()
            
            logger.info(f"Successfully deleted crawl {crawl_id} and associated content")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete crawl {crawl_id}: {str(e)}")
            session.rollback()
            return False
    
    def list_crawls(self, limit: int, offset: int, org_id: str) -> List[CrawlStatus]:
        """List all crawl jobs with pagination."""
        return self.db.list_crawl_statuses(limit, offset, org_id)
    
    def delete_all_crawls(self, org_id: str):
        """Delete all crawls and associated content."""
        try:
            logger.info("Starting deletion of all crawls and associated content")
            
            # Cancel any active crawls first
            for crawl_id in list(self.active_crawls.keys()):
                logger.info(f"Cancelling active crawl: {crawl_id}")
                self.cancel_crawl(crawl_id)
            
            # Clear in-memory references
            self.active_crawls = {}
            self.crawl_statuses = {}
            
            # Delete from database
            from database.models import ContentChunk, Content, Crawl
            session = self.db.session
            
            # Delete chunks first (foreign key constraint)
            logger.info("Deleting content chunks...")
            chunk_count = session.query(ContentChunk).filter(ContentChunk.org_id == org_id).delete()
            logger.info(f"Deleted {chunk_count} content chunks")
            
            # Delete content items
            logger.info("Deleting content items...")
            content_count = session.query(Content).filter(Content.org_id == org_id).delete()
            logger.info(f"Deleted {content_count} content items")
            
            # Delete crawls
            logger.info("Deleting crawl records...")
            crawl_count = session.query(Crawl).filter(Crawl.org_id == org_id).delete()
            logger.info(f"Deleted {crawl_count} crawl records")
            
            # Commit the changes
            session.commit()
            
            logger.info(f"Successfully deleted all crawls and associated content for organization {org_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete all crawls: {str(e)}")
            session.rollback()
            return False
