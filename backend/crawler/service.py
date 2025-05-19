"""
Crawler service implementation.
"""
import logging
import asyncio
import time
from datetime import datetime
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor

from crawler.engine import PlaywrightCrawler
from api.models import CrawlRequest, CrawlStatus, CrawlState, CrawlConfig, CrawlProgress

logger = logging.getLogger(__name__)

class CrawlerService:
    """Service for managing website crawls."""
    
    def __init__(self, db):
        """Initialize the crawler service."""
        self.db = db
        self.active_crawls = {}  # Dict[str, PlaywrightCrawler]
        self.crawl_statuses = {}  # Dict[str, CrawlStatus]
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    def init_crawl(self, crawl_id: str, request: CrawlRequest) -> CrawlStatus:
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
        self.db.save_crawl_status(status)
        
        return status
    
    def run_crawl(self, crawl_id: str, domain: str, config: CrawlConfig):
        """
        Run a crawl job. This method is intended to be run in a background task.
        """
        try:
            # Update status to running
            status = self.crawl_statuses[crawl_id]
            status.state = CrawlState.RUNNING
            status.start_time = datetime.now()
            self.db.update_crawl_status(status)
            
            # Initialize crawler
            crawler = PlaywrightCrawler(
                domain=domain,
                config=config,
                db=self.db,
                crawl_id=crawl_id
            )
            
            # Store crawler reference for potential cancellation
            self.active_crawls[crawl_id] = crawler
            
            # Run the crawler
            crawler.crawl()
            
            # Update status on completion
            status.state = CrawlState.COMPLETED
            status.end_time = datetime.now()
            status.progress = crawler.get_progress()
            
        except Exception as e:
            logger.error(f"Crawl {crawl_id} failed: {str(e)}", exc_info=True)
            
            # Update status on failure
            status = self.crawl_statuses[crawl_id]
            status.state = CrawlState.FAILED
            status.end_time = datetime.now()
            status.error = str(e)
        
        finally:
            # Clean up and save final status
            if crawl_id in self.active_crawls:
                del self.active_crawls[crawl_id]
            
            self.db.update_crawl_status(status)
    
    def get_crawl_status(self, crawl_id: str) -> Optional[CrawlStatus]:
        """Get the current status of a crawl job."""
        # Try in-memory cache first
        if crawl_id in self.crawl_statuses:
            status = self.crawl_statuses[crawl_id]
            
            # For active crawls, update the progress
            if crawl_id in self.active_crawls:
                status.progress = self.active_crawls[crawl_id].get_progress()
            
            return status
        
        # Otherwise fetch from database
        status = self.db.get_crawl_status(crawl_id)
        if status:
            self.crawl_statuses[crawl_id] = status
        
        return status
    
    def cancel_crawl(self, crawl_id: str) -> bool:
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
            self.db.update_crawl_status(status)
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to cancel crawl {crawl_id}: {str(e)}")
            return False
    
    def list_crawls(self, limit: int, offset: int) -> List[CrawlStatus]:
        """List all crawl jobs with pagination."""
        return self.db.list_crawl_statuses(limit, offset)
