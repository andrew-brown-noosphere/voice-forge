# Automated RAG Integration Guide for VoiceForge

This guide shows you exactly how to integrate automated RAG optimization into your existing VoiceForge codebase with minimal changes.

## 🚀 Quick Integration Steps

### Step 1: Add the API Router to Your FastAPI App

In your main FastAPI application file (likely `main.py` or `app.py`):

```python
from fastapi import FastAPI
from api.rag_endpoints import rag_router

app = FastAPI()

# Add your existing routers
# app.include_router(your_existing_routers...)

# Add the new RAG optimization router
app.include_router(rag_router)
```

### Step 2: Add Hooks to Your Existing Organization Creation Code

Find where you create new organizations and add this hook:

```python
# Your existing org creation code
def create_organization(org_data):
    # Your existing logic
    org = Organization.create(org_data)
    org_id = org.id
    
    # 🆕 ADD THIS: Trigger RAG setup for new org
    from automated_rag_integration import RAGIntegrationHooks
    RAGIntegrationHooks.on_organization_created(org_id, org_data)
    
    return org
```

### Step 3: Add Hooks to Your Crawling Completion Code

Find where you mark crawls as complete and add this hook:

```python
# Your existing crawl completion code
def complete_crawl(crawl_id, org_id):
    # Your existing logic
    crawl = get_crawl(crawl_id)
    crawl.state = CrawlState.COMPLETED
    crawl.save()
    
    # 🆕 ADD THIS: Check if we should optimize RAG
    from automated_rag_integration import RAGIntegrationHooks
    crawl_results = {
        'pages_crawled': crawl.pages_crawled,
        'content_extracted': crawl.content_extracted
    }
    RAGIntegrationHooks.on_crawl_completed(crawl_id, org_id, crawl_results)
    
    return crawl
```

### Step 4: Add Lazy Optimization to RAG Queries (Optional)

In your RAG service, add this check before processing queries:

```python
# In your processor/rag_service.py or similar
def search_chunks(self, query, org_id, **kwargs):
    # 🆕 ADD THIS: Ensure org is optimized before querying
    from automated_rag_integration import RAGIntegrationHooks
    RAGIntegrationHooks.on_rag_query_requested(org_id, query)
    
    # Your existing search logic
    return self.rag_system.retrieve_relevant_chunks(
        query=query, org_id=org_id, **kwargs
    )
```

### Step 5: Configure Background Processing (Optional but Recommended)

If you're using Celery for background tasks, configure it:

```python
# In your celery.py or worker configuration
from celery import Celery
from automated_rag_integration import optimize_org_rag_task

# Your existing Celery app
celery_app = Celery('voiceforge')

# The RAG optimization task will be automatically registered
# No additional configuration needed!
```

## 🔧 Configuration Options

### Environment Variables

Set these in your `.env` file or environment:

```bash
# Optional: Default org ID for testing
VOICEFORGE_ORG_ID=your-default-org-id

# Optional: RAG optimization settings
RAG_AUTO_OPTIMIZE_NEW_ORGS=true
RAG_CONTENT_THRESHOLD=10
RAG_MIN_INTERVAL_HOURS=6
RAG_MAX_CONCURRENT=3
```

### Programmatic Configuration

```python
from automated_rag_integration import automated_rag_service

# Customize behavior
automated_rag_service.config.update({
    'auto_optimize_new_orgs': True,
    'auto_optimize_on_content_threshold': 20,  # Higher threshold
    'min_optimization_interval': timedelta(hours=12),  # Less frequent
})
```

## 📡 API Endpoints Added

Your application now has these new endpoints:

### Manual Optimization
```bash
# Trigger optimization manually
POST /api/rag/optimize
{
  "org_id": "your-org-id",
  "force": false,
  "chunk_size": 400,
  "batch_size": 32
}
```

### Check Status
```bash
# Check optimization status
GET /api/rag/status/your-org-id

# Check RAG readiness
GET /api/rag/readiness/your-org-id
```

### Health Check
```bash
# System health
GET /api/rag/health
```

## 🔄 Automatic Triggers

Once integrated, RAG optimization will automatically trigger when:

1. **New Organization Created** → Waits for content, then optimizes
2. **Crawl Completed** → Optimizes if org has 10+ unprocessed items
3. **Content Added** → Optimizes when threshold is reached
4. **RAG Query Made** → Lazy optimization if needed

## 🎯 Testing Your Integration

### Test Automatic Optimization

```python
# Test org creation hook
from automated_rag_integration import RAGIntegrationHooks

result = RAGIntegrationHooks.on_organization_created("test-org-123", {})
print(f"Org creation result: {result}")

# Test crawl completion hook
result = RAGIntegrationHooks.on_crawl_completed(
    "crawl-456", 
    "test-org-123", 
    {"pages_crawled": 15, "content_extracted": 12}
)
print(f"Crawl completion result: {result}")
```

### Test Manual Optimization

```bash
# Via API
curl -X POST "http://localhost:8000/api/rag/optimize" \
  -H "Content-Type: application/json" \
  -d '{"org_id": "your-org-id", "force": true}'

# Via Python
from automated_rag_integration import auto_optimize_org
result = auto_optimize_org("your-org-id", force=True)
print(result)
```

### Test Status Checking

```python
from automated_rag_integration import check_org_optimization_status, is_org_ready_for_rag

# Check status
status = check_org_optimization_status("your-org-id")
print(f"Status: {status}")

# Check readiness
ready, reason = is_org_ready_for_rag("your-org-id")
print(f"Ready: {ready}, Reason: {reason}")
```

## 🔧 Customization Examples

### Custom Optimization Logic

```python
from automated_rag_integration import automated_rag_service

def custom_should_optimize(org_id):
    """Custom logic to determine if org should be optimized."""
    # Your custom business logic here
    # e.g., check org subscription tier, content type, etc.
    return True, "Custom trigger"

# Override the default logic
automated_rag_service.should_auto_optimize = custom_should_optimize
```

### Custom Content Thresholds

```python
# Different thresholds per org type
def get_content_threshold(org_id):
    org = get_organization(org_id)
    if org.tier == 'enterprise':
        return 50  # Higher threshold for enterprise
    elif org.tier == 'professional':
        return 20
    else:
        return 10  # Standard threshold

automated_rag_service.config['auto_optimize_on_content_threshold'] = get_content_threshold
```

## 🚨 Troubleshooting

### Common Issues

1. **"No module named 'automated_rag_integration'"**
   ```bash
   # Make sure the file is in your backend directory
   ls -la automated_rag_integration.py
   ```

2. **"Celery not available"**
   ```bash
   # Install Celery if you want background processing
   pip install celery
   # Or it will fall back to synchronous processing
   ```

3. **"No content to optimize"**
   ```bash
   # Make sure you've crawled some content first
   curl -X GET "http://localhost:8000/api/crawls?org_id=your-org-id"
   ```

### Debug Mode

Enable detailed logging:

```python
import logging
logging.getLogger('automated_rag_integration').setLevel(logging.DEBUG)
```

### Health Check

```bash
# Check if the system is working
curl -X GET "http://localhost:8000/api/rag/health"
```

## 🎉 Success Indicators

You'll know the integration is working when:

- ✅ New orgs automatically get optimized after content is added
- ✅ Background tasks are queued for optimization
- ✅ API endpoints respond correctly
- ✅ RAG queries return better results
- ✅ No manual intervention needed for new orgs

## 📊 Monitoring

### Check Overall System Status

```python
from automated_rag_integration import automated_rag_service

# Get all current optimizations
for org_id, status in automated_rag_service._optimization_status.items():
    print(f"Org {org_id}: {status['status']}")
```

### Performance Metrics

```bash
# Check API performance
GET /api/rag/health

# Check individual org status
GET /api/rag/status/{org_id}
```

Your VoiceForge application now has fully automated RAG optimization! 🚀

New organizations will automatically get optimized RAG systems without any manual intervention, and existing orgs will be kept up-to-date as new content is added.
