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

from api.models import (
    CrawlRequest, CrawlStatus, ContentSearchRequest, ContentResponse,
    ChunkSearchRequest, ChunkResponse, GenerateContentRequest, GeneratedContent,
    MarketingTemplateCreate, MarketingTemplateResponse, TemplateSearchRequest
)
from api.dependencies import get_crawler_service, get_processor_service, get_rag_service, get_db
from crawler.service import CrawlerService
from processor.service import ProcessorService
from processor.rag_service import RAGService
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
    version="0.2.0",
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
    return {"status": "VoiceForge API is running", "version": "0.2.0"}

# Crawl endpoints

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

@app.delete("/crawl-all", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_crawls(
    background_tasks: BackgroundTasks,
    crawler_service: CrawlerService = Depends(get_crawler_service),
):
    """Delete all crawls and associated content."""
    try:
        # Start the deletion process in the background
        background_tasks.add_task(
            crawler_service.delete_all_crawls
        )
        
        return None
    except Exception as e:
        logger.error(f"Failed to delete all crawls: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete all crawls: {str(e)}"
        )

@app.get("/crawl/{crawl_id}", response_model=CrawlStatus)
async def get_crawl_status(
    crawl_id: str,
    crawler_service: CrawlerService = Depends(get_crawler_service),
):
    """Get the status of a specific crawl job."""
    try:
        crawl_status = crawler_service.get_crawl_status(crawl_id)
        if not crawl_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Crawl job with ID {crawl_id} not found"
            )
        return crawl_status
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

# Content search endpoints

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
        
        # Manually add domains if the list is empty
        if not domains:
            domains = ["https://noosphere.tech", "https://www.noosphere.tech"]
            
        return domains
    except Exception as e:
        logger.error(f"Failed to list domains: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list domains: {str(e)}"
        )

# New RAG endpoints

@app.post("/rag/chunks/search", response_model=List[ChunkResponse])
async def search_chunks(
    request: ChunkSearchRequest,
    rag_service: RAGService = Depends(get_rag_service),
):
    """
    Search for content chunks for RAG.
    
    This endpoint accepts a search query and returns relevant content chunks
    that can be used for retrieval-augmented generation.
    """
    try:
        chunks = rag_service.search_chunks(
            query=request.query,
            domain=request.domain,
            content_type=request.content_type,
            top_k=request.top_k
        )
        return chunks
    except Exception as e:
        logger.error(f"Failed to search chunks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search chunks: {str(e)}"
        )

@app.get("/rag/content/{content_id}/chunks", response_model=List[ChunkResponse])
async def get_content_chunks(
    content_id: str,
    rag_service: RAGService = Depends(get_rag_service),
):
    """Get all chunks for a specific content piece."""
    try:
        chunks = rag_service.get_content_chunks(content_id)
        return chunks
    except Exception as e:
        logger.error(f"Failed to get content chunks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get content chunks: {str(e)}"
        )

@app.post("/rag/process/{content_id}", status_code=status.HTTP_202_ACCEPTED)
async def process_content_for_rag(
    content_id: str,
    background_tasks: BackgroundTasks,
    rag_service: RAGService = Depends(get_rag_service),
):
    """
    Process content for RAG.
    
    This endpoint initiates a background task to process content into chunks
    for retrieval-augmented generation.
    """
    try:
        # Start processing in the background
        background_tasks.add_task(rag_service.process_content_for_rag, content_id)
        
        return {"status": "processing", "content_id": content_id}
    except Exception as e:
        logger.error(f"Failed to process content for RAG: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process content for RAG: {str(e)}"
        )

@app.post("/rag/generate", response_model=GeneratedContent)
async def generate_content(
    request: GenerateContentRequest,
    rag_service: RAGService = Depends(get_rag_service),
):
    """
    Generate content using RAG.
    
    This endpoint uses retrieval-augmented generation to create content
    based on the provided query and parameters.
    """
    try:
        content = rag_service.generate_content(
            query=request.query,
            platform=request.platform,
            tone=request.tone,
            domain=request.domain,
            content_type=request.content_type,
            top_k=request.top_k
        )
        return content
    except Exception as e:
        logger.error(f"Failed to generate content: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate content: {str(e)}"
        )

# Template management endpoints

@app.post("/templates", response_model=MarketingTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template: MarketingTemplateCreate,
    rag_service: RAGService = Depends(get_rag_service),
):
    """Create a new marketing template."""
    try:
        # Convert to dictionary
        template_data = template.dict()
        
        # Store template
        template_id = rag_service.create_template(template_data)
        
        # Get the created template
        created_template = rag_service.get_template(template_id)
        
        return created_template
    except Exception as e:
        logger.error(f"Failed to create template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create template: {str(e)}"
        )

@app.get("/templates/{template_id}", response_model=MarketingTemplateResponse)
async def get_template(
    template_id: str,
    rag_service: RAGService = Depends(get_rag_service),
):
    """Get a specific template by ID."""
    try:
        template = rag_service.get_template(template_id)
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template with ID {template_id} not found"
            )
        
        return template
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get template: {str(e)}"
        )

@app.post("/templates/search", response_model=List[MarketingTemplateResponse])
async def search_templates(
    request: TemplateSearchRequest,
    rag_service: RAGService = Depends(get_rag_service),
):
    """Search for templates with filters."""
    try:
        templates = rag_service.list_templates(
            platform=request.platform,
            tone=request.tone,
            purpose=request.purpose,
            limit=request.limit,
            offset=request.offset
        )
        return templates
    except Exception as e:
        logger.error(f"Failed to search templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search templates: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
