"""
FastAPI Endpoints for Automated RAG Integration
Add these endpoints to your existing FastAPI application
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, status
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime

from automated_rag_integration import (
    automated_rag_service, 
    RAGIntegrationHooks,
    auto_optimize_org,
    check_org_optimization_status,
    is_org_ready_for_rag,
    OptimizationStatus
)

logger = logging.getLogger(__name__)

# Create router for RAG optimization endpoints
rag_router = APIRouter(prefix="/api/rag", tags=["RAG Optimization"])

# Pydantic models for request/response
class OptimizationRequest(BaseModel):
    org_id: str
    force: bool = False
    chunk_size: Optional[int] = 400
    chunk_overlap: Optional[int] = 80
    batch_size: Optional[int] = 32
    max_content: Optional[int] = None

class OptimizationResponse(BaseModel):
    status: str
    org_id: str
    message: Optional[str] = None
    task_id: Optional[str] = None
    timestamp: str
    error: Optional[str] = None
    results: Optional[Dict[str, Any]] = None

class OptimizationStatusResponse(BaseModel):
    org_id: str
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    task_id: Optional[str] = None
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class OrgReadinessResponse(BaseModel):
    org_id: str
    ready: bool
    reason: str
    recommendations: Optional[List[str]] = None

# RAG Optimization Endpoints
@rag_router.post("/optimize", response_model=OptimizationResponse)
async def trigger_rag_optimization(
    request: OptimizationRequest,
    background_tasks: BackgroundTasks,
    # Add your auth dependency here: current_user: User = Depends(get_current_user)
):
    """
    Trigger RAG optimization for an organization.
    
    This endpoint allows manual triggering of RAG optimization,
    which normally happens automatically.
    """
    try:
        logger.info(f"🚀 Manual RAG optimization requested for org {request.org_id}")
        
        # TODO: Add authorization check
        # if not user_can_access_org(current_user, request.org_id):
        #     raise HTTPException(status_code=403, detail="Access denied")
        
        # Trigger optimization
        result = auto_optimize_org(
            org_id=request.org_id,
            force=request.force,
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
            batch_size=request.batch_size,
            max_content=request.max_content
        )
        
        return OptimizationResponse(**result)
        
    except Exception as e:
        logger.error(f"❌ Failed to trigger optimization for org {request.org_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to trigger optimization: {str(e)}"
        )

@rag_router.get("/status/{org_id}", response_model=OptimizationStatusResponse)
async def get_optimization_status(
    org_id: str,
    # current_user: User = Depends(get_current_user)
):
    """
    Get the current optimization status for an organization.
    """
    try:
        # TODO: Add authorization check
        # if not user_can_access_org(current_user, org_id):
        #     raise HTTPException(status_code=403, detail="Access denied")
        
        status_info = check_org_optimization_status(org_id)
        
        if not status_info:
            # No optimization history - check if org needs optimization
            ready, reason = is_org_ready_for_rag(org_id)
            return OptimizationStatusResponse(
                org_id=org_id,
                status="never_optimized" if not ready else "ready",
                error=reason if not ready else None
            )
        
        return OptimizationStatusResponse(
            org_id=org_id,
            **status_info
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to get status for org {org_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get optimization status: {str(e)}"
        )

@rag_router.get("/readiness/{org_id}", response_model=OrgReadinessResponse)
async def check_org_rag_readiness(
    org_id: str,
    # current_user: User = Depends(get_current_user)
):
    """
    Check if an organization is ready for RAG queries.
    
    Returns readiness status and recommendations if not ready.
    """
    try:
        # TODO: Add authorization check
        # if not user_can_access_org(current_user, org_id):
        #     raise HTTPException(status_code=403, detail="Access denied")
        
        ready, reason = is_org_ready_for_rag(org_id)
        
        recommendations = []
        if not ready:
            if "no content" in reason.lower():
                recommendations.append("Crawl some websites to add content")
            elif "unprocessed" in reason.lower():
                recommendations.append("Run content processing to create chunks")
            elif "embedding" in reason.lower():
                recommendations.append("Generate embeddings for content chunks")
            else:
                recommendations.append("Run RAG optimization pipeline")
        
        return OrgReadinessResponse(
            org_id=org_id,
            ready=ready,
            reason=reason,
            recommendations=recommendations if recommendations else None
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to check readiness for org {org_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check RAG readiness: {str(e)}"
        )

@rag_router.post("/auto-optimize-all")
async def auto_optimize_all_orgs(
    background_tasks: BackgroundTasks,
    force: bool = False,
    # current_user: User = Depends(get_current_admin_user)  # Admin only
):
    """
    Trigger auto-optimization for all organizations that need it.
    
    This endpoint is useful for admin operations or scheduled tasks.
    """
    try:
        # TODO: Add admin authorization check
        
        logger.info("🚀 Triggering auto-optimization for all orgs")
        
        # Get all org IDs (you'll need to implement this based on your org model)
        # org_ids = get_all_organization_ids()
        
        # For now, return a placeholder
        return {
            "message": "Auto-optimization triggered for all eligible organizations",
            "timestamp": datetime.utcnow().isoformat(),
            "note": "Implement get_all_organization_ids() to enable this endpoint"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to trigger auto-optimization for all orgs: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to trigger auto-optimization: {str(e)}"
        )

# Integration webhooks (for internal use)
@rag_router.post("/webhooks/org-created")
async def webhook_org_created(
    org_id: str,
    org_data: Dict[str, Any],
    background_tasks: BackgroundTasks
):
    """
    Webhook endpoint called when a new organization is created.
    
    This is for internal system integration - call this from your org creation logic.
    """
    try:
        logger.info(f"🏢 Webhook: Organization created - {org_id}")
        
        result = RAGIntegrationHooks.on_organization_created(org_id, org_data)
        
        return {
            "status": "processed",
            "org_id": org_id,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Webhook org-created failed for org {org_id}: {e}")
        return {
            "status": "error",
            "org_id": org_id,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@rag_router.post("/webhooks/crawl-completed")
async def webhook_crawl_completed(
    crawl_id: str,
    org_id: str,
    crawl_results: Dict[str, Any],
    background_tasks: BackgroundTasks
):
    """
    Webhook endpoint called when a content crawl is completed.
    
    This triggers auto-optimization if the org has enough new content.
    """
    try:
        logger.info(f"🕷️ Webhook: Crawl completed - {crawl_id} for org {org_id}")
        
        result = RAGIntegrationHooks.on_crawl_completed(crawl_id, org_id, crawl_results)
        
        return {
            "status": "processed",
            "crawl_id": crawl_id,
            "org_id": org_id,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Webhook crawl-completed failed for crawl {crawl_id}: {e}")
        return {
            "status": "error",
            "crawl_id": crawl_id,
            "org_id": org_id,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@rag_router.post("/webhooks/content-added")
async def webhook_content_added(
    org_id: str,
    content_count: int,
    background_tasks: BackgroundTasks
):
    """
    Webhook endpoint called when content is added to an organization.
    
    This may trigger auto-optimization if enough content has been added.
    """
    try:
        logger.info(f"📄 Webhook: Content added - {content_count} items for org {org_id}")
        
        result = RAGIntegrationHooks.on_content_added(org_id, content_count)
        
        return {
            "status": "processed",
            "org_id": org_id,
            "content_count": content_count,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Webhook content-added failed for org {org_id}: {e}")
        return {
            "status": "error",
            "org_id": org_id,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# Health check endpoint
@rag_router.get("/health")
async def rag_health_check():
    """
    Health check endpoint for RAG optimization system.
    """
    try:
        # Check if optimization service is healthy
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "background_processing": automated_rag_service.config['background_processing'],
            "auto_optimize_enabled": automated_rag_service.config['auto_optimize_new_orgs'],
            "concurrent_limit": automated_rag_service.config['max_concurrent_optimizations']
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"❌ RAG health check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"RAG system unhealthy: {str(e)}"
        )

# Configuration endpoint (admin only)
@rag_router.get("/config")
async def get_rag_config(
    # current_user: User = Depends(get_current_admin_user)
):
    """
    Get current RAG optimization configuration.
    Admin-only endpoint.
    """
    return {
        "config": automated_rag_service.config,
        "timestamp": datetime.utcnow().isoformat()
    }

@rag_router.put("/config")
async def update_rag_config(
    config_updates: Dict[str, Any],
    # current_user: User = Depends(get_current_admin_user)
):
    """
    Update RAG optimization configuration.
    Admin-only endpoint.
    """
    try:
        # Update configuration
        for key, value in config_updates.items():
            if key in automated_rag_service.config:
                automated_rag_service.config[key] = value
        
        logger.info(f"🔧 RAG configuration updated: {config_updates}")
        
        return {
            "status": "updated",
            "config": automated_rag_service.config,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to update RAG config: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update configuration: {str(e)}"
        )
