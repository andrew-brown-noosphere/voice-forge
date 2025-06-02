"""
Debug patch for api/main.py to log incoming crawl requests
"""

debug_patch = '''
@app.post("/crawl", response_model=CrawlStatus, status_code=status.HTTP_202_ACCEPTED)
async def start_crawl(
    request: CrawlRequest,
    background_tasks: BackgroundTasks,
    current_user: AuthUser = Depends(get_current_user_with_org),
    crawler_service: CrawlerService = Depends(get_crawler_service),
):
    """
    Start a new website crawl.
    
    This endpoint accepts a domain URL and crawl configurations, then
    initiates a background task to crawl the website.
    """
    try:
        # 🔍 DEBUG: Log the incoming request
        logger.warning(f"🔍 DEBUG: Incoming crawl request:")
        logger.warning(f"  Domain: {request.domain}")
        logger.warning(f"  Config max_pages: {request.config.max_pages}")
        logger.warning(f"  Config max_depth: {request.config.max_depth}")
        logger.warning(f"  Full config: {request.config.json()}")
        
        # Generate a unique ID for this crawl job
        crawl_id = str(uuid.uuid4())
        
        # Get organization ID for multi-tenant isolation
        org_id = get_org_id_from_user(current_user)
        
        # 🔍 DEBUG: Log processed values
        logger.warning(f"🔍 DEBUG: Processing crawl:")
        logger.warning(f"  Crawl ID: {crawl_id}")
        logger.warning(f"  Org ID: {org_id}")
        
        # Initialize the crawl status
        status = crawler_service.init_crawl(crawl_id, request, org_id)
        
        # 🔍 DEBUG: Log initialized status
        logger.warning(f"🔍 DEBUG: Initialized status:")
        logger.warning(f"  Status config max_pages: {status.config.max_pages}")
        
        # Start the crawl process in the background
        background_tasks.add_task(
            crawler_service.run_crawl,
            crawl_id=crawl_id,
            domain=request.domain,
            config=request.config,
            org_id=org_id
        )
        
        logger.info(f"🎆 Started background task for crawl {crawl_id}")
        
        return status
    except Exception as e:
        logger.error(f"Failed to start crawl: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start crawl: {str(e)}"
        )
'''

print("🔧 API Debug Patch")
print("=" * 50)
print()
print("To debug incoming crawl requests, replace the start_crawl function")
print("in api/main.py with the enhanced version above.")
print()
print("This will log:")
print("• Incoming request configuration")
print("• Processed values")
print("• Initialized status")
print()
print("Look for log lines with '🔍 DEBUG:' prefix in your server logs.")
print()
print("IMPORTANT: The logs use logger.warning() so they appear even with")
print("standard logging levels.")
