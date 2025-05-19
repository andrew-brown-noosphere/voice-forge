"""
Main application file for the VoiceForge backend API server.
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
import logging
import uuid
import os

from api.models import CrawlRequest, CrawlStatus, ContentSearchRequest, ContentResponse
from api.dependencies import get_crawler_service, get_processor_service, get_db
from crawler.service import CrawlerService
from processor.service import ProcessorService
from database.session import get_db_session

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="VoiceForge API",
    description="API for website crawling and content processing",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with actual frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (if needed)
# app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    """Root endpoint to check if the API is running."""
    return {"status": "VoiceForge API is running"}

@app.post("/crawl", response_model=CrawlStatus, status_code=status.HTTP_202_ACCEPTED)
async def start_crawl(
    request: CrawlRequest,
    background_tasks: BackgroundTasks,
    crawler_service: CrawlerService = Depends(get_crawler_service),
):
    """
    Start a new website crawl.
    
    This endpoint accepts a domain URL and crawl configurations, then
    initiates a background task to crawl the website.
    """
    try:
        # Generate a unique ID for this crawl job
        crawl_id = str(uuid.uuid4())
        
        # Initialize the crawl status
        status = crawler_service.init_crawl(crawl_id, request)
        
        # Start the crawl process in the background
        background_tasks.add_task(
            crawler_service.run_crawl,
            crawl_id=crawl_id,
            domain=request.domain,
            config=request.config
        )
        
        return status
    except Exception as e:
        logger.error(f"Failed to start crawl: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start crawl: {str(e)}"
        )

@app.get("/crawl/{crawl_id}", response_model=CrawlStatus)
async def get_crawl_status(
    crawl_id: str,
    crawler_service: CrawlerService = Depends(get_crawler_service),
):
    """Get the status of a specific crawl job."""
    try:
        status = crawler_service.get_crawl_status(crawl_id)
        if not status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Crawl job with ID {crawl_id} not found"
            )
        return status
    except Exception as e:
        logger.error(f"Failed to get crawl status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get crawl status: {str(e)}"
        )

@app.delete("/crawl/{crawl_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_crawl(
    crawl_id: str,
    crawler_service: CrawlerService = Depends(get_crawler_service),
):
    """Cancel an ongoing crawl job."""
    try:
        success = crawler_service.cancel_crawl(crawl_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Crawl job with ID {crawl_id} not found or already completed"
            )
        return None
    except Exception as e:
        logger.error(f"Failed to cancel crawl: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel crawl: {str(e)}"
        )

@app.get("/crawl", response_model=List[CrawlStatus])
async def list_crawls(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    crawler_service: CrawlerService = Depends(get_crawler_service),
):
    """List all crawl jobs with pagination."""
    try:
        crawls = crawler_service.list_crawls(limit, offset)
        return crawls
    except Exception as e:
        logger.error(f"Failed to list crawls: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list crawls: {str(e)}"
        )

@app.post("/content/search", response_model=List[ContentResponse])
async def search_content(
    request: ContentSearchRequest,
    processor_service: ProcessorService = Depends(get_processor_service),
):
    """
    Search for content based on query text and filters.
    
    This endpoint accepts a search query and returns relevant content
    from the crawled websites.
    """
    try:
        results = processor_service.search_content(
            query=request.query,
            domain=request.domain,
            content_type=request.content_type,
            limit=request.limit,
            offset=request.offset
        )
        return results
    except Exception as e:
        logger.error(f"Failed to search content: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search content: {str(e)}"
        )

@app.get("/content/{content_id}", response_model=ContentResponse)
async def get_content(
    content_id: str,
    processor_service: ProcessorService = Depends(get_processor_service),
):
    """Get a specific piece of content by ID."""
    try:
        content = processor_service.get_content(content_id)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Content with ID {content_id} not found"
            )
        return content
    except Exception as e:
        logger.error(f"Failed to get content: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get content: {str(e)}"
        )

@app.get("/domains", response_model=List[str])
async def list_domains(
    db = Depends(get_db),
):
    """List all domains that have been crawled."""
    try:
        domains = db.get_all_domains()
        return domains
    except Exception as e:
        logger.error(f"Failed to list domains: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list domains: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
