# Quick fix to bypass auth temporarily for testing
# Edit backend/api/main.py

# Find the crawl endpoint (around line 165) and change:

# FROM:
async def start_crawl(
    request: CrawlRequest,
    background_tasks: BackgroundTasks,
    current_user: AuthUser = Depends(get_current_user_with_org),  # REMOVE THIS LINE
    crawler_service: CrawlerService = Depends(get_crawler_service),
):

# TO:
async def start_crawl(
    request: CrawlRequest,
    background_tasks: BackgroundTasks,
    # current_user: AuthUser = Depends(get_current_user_with_org),  # COMMENTED OUT
    crawler_service: CrawlerService = Depends(get_crawler_service),
):

# Then in the function body, replace:
# org_id = get_org_id_from_user(current_user)

# WITH:
org_id = "test-org"  # Temporary test org ID
