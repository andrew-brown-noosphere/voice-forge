"""
Enhanced RAG Endpoints for VoiceForge with Hybrid Search Support.

This module provides API endpoints that utilize the new hybrid RAG service
with multi-strategy retrieval and cross-encoder reranking.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Literal
import logging
from datetime import datetime

from api.dependencies import get_db
from auth.clerk_auth import get_current_user_with_org, AuthUser, get_org_id_from_user
from services.enhanced_rag_service import create_hybrid_rag_service

logger = logging.getLogger(__name__)

# Create router for enhanced RAG endpoints
enhanced_rag_router = APIRouter(prefix="/api/rag", tags=["Enhanced RAG"])

# Pydantic models for requests and responses
class HybridSearchRequest(BaseModel):
    """Request model for hybrid search."""
    query: str = Field(..., description="Search query", min_length=1, max_length=1000)
    strategy: Literal["hybrid", "semantic", "keyword", "domain"] = Field(
        "hybrid", 
        description="Search strategy to use"
    )
    top_k: int = Field(10, ge=1, le=50, description="Number of results to return")
    domain: Optional[str] = Field(None, description="Filter by specific domain")
    content_type: Optional[str] = Field(None, description="Filter by content type")

class HybridSearchResponse(BaseModel):
    """Response model for hybrid search."""
    query: str
    results: List[Dict[str, Any]]
    retrieval_stats: Dict[str, Any]
    timestamp: str
    strategy_used: str

class GenerateWithHybridRequest(BaseModel):
    """Request model for content generation with hybrid RAG."""
    query: str = Field(..., description="Query or topic for content generation")
    platform: str = Field(..., description="Target platform (twitter, linkedin, etc.)")
    tone: str = Field(..., description="Desired tone (professional, casual, etc.)")
    strategy: Literal["hybrid", "semantic", "keyword", "domain"] = Field(
        "hybrid", 
        description="Search strategy for context retrieval"
    )
    top_k: int = Field(5, ge=1, le=20, description="Number of context chunks to retrieve")
    domain: Optional[str] = Field(None, description="Filter context by domain")
    content_type: Optional[str] = Field(None, description="Filter context by content type")

class GenerateWithHybridResponse(BaseModel):
    """Response model for hybrid RAG content generation."""
    query: str
    generated_content: str
    context_sources: List[Dict[str, Any]]
    retrieval_stats: Dict[str, Any]
    generation_metadata: Dict[str, Any]
    timestamp: str

# Enhanced RAG Endpoints

@enhanced_rag_router.post("/search", response_model=HybridSearchResponse)
async def hybrid_search(
    request: HybridSearchRequest,
    current_user: AuthUser = Depends(get_current_user_with_org),
    db = Depends(get_db)
):
    """
    Enhanced search endpoint using hybrid retrieval strategies.
    
    This endpoint combines semantic search, keyword matching, and domain filtering
    with cross-encoder reranking for improved relevance.
    """
    try:
        # Get organization ID for multi-tenant filtering
        org_id = get_org_id_from_user(current_user)
        
        # Create hybrid RAG service
        hybrid_service = create_hybrid_rag_service(db, vector_service=None)  # TODO: Pass vector service
        
        # Execute hybrid search
        search_results = await hybrid_service.retrieve_and_rank(
            query=request.query,
            strategy=request.strategy,
            top_k=request.top_k,
            org_id=org_id,
            domain=request.domain,
            content_type=request.content_type
        )
        
        return HybridSearchResponse(
            query=request.query,
            results=search_results["results"],
            retrieval_stats=search_results["retrieval_stats"],
            timestamp=datetime.utcnow().isoformat(),
            strategy_used=request.strategy
        )
        
    except Exception as e:
        logger.error(f"Hybrid search failed for user {current_user.user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )

@enhanced_rag_router.post("/generate", response_model=GenerateWithHybridResponse)
async def generate_with_hybrid_rag(
    request: GenerateWithHybridRequest,
    current_user: AuthUser = Depends(get_current_user_with_org),
    db = Depends(get_db)
):
    """
    Enhanced content generation using hybrid RAG for context retrieval.
    
    This endpoint uses the hybrid search to gather relevant context,
    then generates content using the retrieved information.
    """
    try:
        # Get organization ID for multi-tenant filtering
        org_id = get_org_id_from_user(current_user)
        
        # Create hybrid RAG service
        hybrid_service = create_hybrid_rag_service(db, vector_service=None)  # TODO: Pass vector service
        
        # Step 1: Retrieve relevant context using hybrid search
        context_results = await hybrid_service.retrieve_and_rank(
            query=request.query,
            strategy=request.strategy,
            top_k=request.top_k,
            org_id=org_id,
            domain=request.domain,
            content_type=request.content_type
        )
        
        # Step 2: Generate content using the retrieved context
        # TODO: Integrate with your existing content generation service
        # For now, we'll create a simple template-based response
        
        context_text = "\n\n".join([
            result["content"] for result in context_results["results"][:5]
        ])
        
        # Simple template-based generation (replace with your AI generation service)
        generated_content = await _generate_content_with_context(
            query=request.query,
            context=context_text,
            platform=request.platform,
            tone=request.tone
        )
        
        # Format context sources for response
        context_sources = []
        for result in context_results["results"]:
            context_sources.append({
                "content_preview": result["content"][:200] + "..." if len(result["content"]) > 200 else result["content"],
                "domain": result["metadata"].get("domain"),
                "title": result["metadata"].get("title"),
                "rerank_score": result["metadata"].get("rerank_score"),
                "search_type": result["metadata"].get("search_type"),
                "content_id": result["metadata"].get("content_id")
            })
        
        return GenerateWithHybridResponse(
            query=request.query,
            generated_content=generated_content,
            context_sources=context_sources,
            retrieval_stats=context_results["retrieval_stats"],
            generation_metadata={
                "platform": request.platform,
                "tone": request.tone,
                "strategy_used": request.strategy,
                "context_chunks_used": len(context_sources)
            },
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Hybrid content generation failed for user {current_user.user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Content generation failed: {str(e)}"
        )

@enhanced_rag_router.get("/strategies")
async def get_available_strategies():
    """
    Get information about available search strategies.
    """
    return {
        "strategies": {
            "hybrid": {
                "description": "Combines semantic, keyword, and domain search with reranking",
                "best_for": "Most queries - provides comprehensive results",
                "performance": "Slower but most accurate"
            },
            "semantic": {
                "description": "Vector similarity search using embeddings",
                "best_for": "Conceptual queries and meaning-based search",
                "performance": "Fast with good conceptual understanding"
            },
            "keyword": {
                "description": "PostgreSQL full-text search",
                "best_for": "Exact term matching and specific phrases",
                "performance": "Very fast for precise queries"
            },
            "domain": {
                "description": "Domain-aware semantic search",
                "best_for": "Queries mentioning specific websites or platforms",
                "performance": "Fast when domain hints are detected"
            }
        },
        "recommendation": "Use 'hybrid' for best results, 'semantic' for speed with conceptual queries, 'keyword' for exact matches"
    }

@enhanced_rag_router.get("/stats/{org_id}")
async def get_rag_statistics(
    org_id: str,
    current_user: AuthUser = Depends(get_current_user_with_org),
    db = Depends(get_db)
):
    """
    Get RAG statistics for an organization.
    
    Returns information about content availability, embeddings, and readiness.
    """
    try:
        # Verify user has access to this organization
        user_org_id = get_org_id_from_user(current_user)
        if user_org_id != org_id:
            raise HTTPException(status_code=403, detail="Access denied to organization data")
        
        # Query database for statistics
        stats = await _get_org_rag_stats(db, org_id)
        
        return {
            "org_id": org_id,
            "statistics": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get RAG statistics for org {org_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve statistics: {str(e)}"
        )

@enhanced_rag_router.post("/debug/search")
async def debug_search_strategies(
    query: str = Query(..., description="Search query to debug"),
    org_id: str = Query(..., description="Organization ID"),
    current_user: AuthUser = Depends(get_current_user_with_org),
    db = Depends(get_db)
):
    """
    Debug endpoint to test individual search strategies.
    
    Returns results from each strategy separately for comparison and debugging.
    """
    try:
        # Verify user has access to this organization
        user_org_id = get_org_id_from_user(current_user)
        if user_org_id != org_id:
            raise HTTPException(status_code=403, detail="Access denied to organization data")
        
        # Create hybrid RAG service
        hybrid_service = create_hybrid_rag_service(db, vector_service=None)
        
        # Test each strategy individually
        debug_results = {}
        strategies = ["semantic", "keyword", "domain"]
        
        for strategy in strategies:
            try:
                result = await hybrid_service.retrieve_and_rank(
                    query=query,
                    strategy=strategy,
                    top_k=5,
                    org_id=org_id
                )
                debug_results[strategy] = {
                    "results_count": len(result["results"]),
                    "results": result["results"][:3],  # Show only top 3 for debugging
                    "stats": result["retrieval_stats"]
                }
            except Exception as e:
                debug_results[strategy] = {
                    "error": str(e),
                    "results_count": 0,
                    "results": [],
                    "stats": {}
                }
        
        # Also test hybrid strategy
        try:
            hybrid_result = await hybrid_service.retrieve_and_rank(
                query=query,
                strategy="hybrid",
                top_k=10,
                org_id=org_id
            )
            debug_results["hybrid"] = {
                "results_count": len(hybrid_result["results"]),
                "results": hybrid_result["results"][:5],  # Show top 5 for hybrid
                "stats": hybrid_result["retrieval_stats"]
            }
        except Exception as e:
            debug_results["hybrid"] = {
                "error": str(e),
                "results_count": 0,
                "results": [],
                "stats": {}
            }
        
        return {
            "query": query,
            "org_id": org_id,
            "debug_results": debug_results,
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "total_strategies_tested": len(strategies) + 1,
                "successful_strategies": len([k for k, v in debug_results.items() if "error" not in v]),
                "best_strategy": max(debug_results.keys(), 
                                   key=lambda k: debug_results[k].get("results_count", 0))
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Debug search failed for query '{query}' in org {org_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Debug search failed: {str(e)}"
        )

# Helper functions

async def _generate_content_with_context(
    query: str, 
    context: str, 
    platform: str, 
    tone: str
) -> str:
    """
    Generate content using the provided context.
    
    This is a placeholder implementation. In production, this should
    integrate with your AI content generation service (OpenAI, etc.).
    """
    # Simple template-based generation (replace with actual AI service)
    templates = {
        "twitter": f"🚀 {query}\n\nBased on our research:\n{context[:200]}...\n\n#VoiceForge",
        "linkedin": f"**{query}**\n\nKey insights from our analysis:\n\n{context[:400]}...\n\nWhat are your thoughts?",
        "email": f"Subject: {query}\n\nDear Valued Customer,\n\n{context[:300]}...\n\nBest regards,\nThe VoiceForge Team",
        "blog": f"# {query}\n\n{context[:500]}...\n\n## Conclusion\n\nBased on our research, we can see that..."
    }
    
    template = templates.get(platform, templates["blog"])
    
    # Apply tone modifications
    if tone == "casual":
        template = template.replace("Dear Valued Customer", "Hey there!")
        template = template.replace("Best regards", "Cheers")
    elif tone == "enthusiastic":
        template = template.replace(".", "!")
        template = "🎉 " + template
    
    return template

async def _get_org_rag_stats(db, org_id: str) -> Dict[str, Any]:
    """
    Get comprehensive RAG statistics for an organization.
    """
    try:
        # Query for content statistics
        from sqlalchemy import text
        
        content_stats_query = text("""
            SELECT 
                COUNT(*) as total_content,
                COUNT(CASE WHEN is_processed = true THEN 1 END) as processed_content,
                COUNT(CASE WHEN embedding IS NOT NULL THEN 1 END) as content_with_embeddings
            FROM contents c
            JOIN crawls cr ON c.crawl_id = cr.id
            WHERE cr.org_id = :org_id
        """)
        
        chunk_stats_query = text("""
            SELECT 
                COUNT(*) as total_chunks,
                COUNT(CASE WHEN embedding IS NOT NULL THEN 1 END) as chunks_with_embeddings,
                AVG(LENGTH(text)) as avg_chunk_size
            FROM content_chunks cc
            WHERE cc.org_id = :org_id
        """)
        
        domain_stats_query = text("""
            SELECT 
                COUNT(DISTINCT c.domain) as unique_domains,
                COUNT(DISTINCT c.content_type) as content_types
            FROM contents c
            JOIN crawls cr ON c.crawl_id = cr.id
            WHERE cr.org_id = :org_id
        """)
        
        # Execute queries
        content_result = db.execute(content_stats_query, {"org_id": org_id}).fetchone()
        chunk_result = db.execute(chunk_stats_query, {"org_id": org_id}).fetchone()
        domain_result = db.execute(domain_stats_query, {"org_id": org_id}).fetchone()
        
        # Calculate readiness metrics
        total_content = content_result.total_content or 0
        processed_content = content_result.processed_content or 0
        content_with_embeddings = content_result.content_with_embeddings or 0
        total_chunks = chunk_result.total_chunks or 0
        chunks_with_embeddings = chunk_result.chunks_with_embeddings or 0
        
        processing_rate = (processed_content / total_content * 100) if total_content > 0 else 0
        embedding_rate = (content_with_embeddings / total_content * 100) if total_content > 0 else 0
        chunk_embedding_rate = (chunks_with_embeddings / total_chunks * 100) if total_chunks > 0 else 0
        
        # Determine RAG readiness
        is_ready = (
            total_content >= 5 and  # At least 5 pieces of content
            processing_rate >= 80 and  # At least 80% processed
            chunk_embedding_rate >= 80  # At least 80% of chunks have embeddings
        )
        
        readiness_issues = []
        if total_content < 5:
            readiness_issues.append("Insufficient content (need at least 5 pieces)")
        if processing_rate < 80:
            readiness_issues.append(f"Low processing rate ({processing_rate:.1f}%)")
        if chunk_embedding_rate < 80:
            readiness_issues.append(f"Low chunk embedding rate ({chunk_embedding_rate:.1f}%)")
        
        return {
            "content_statistics": {
                "total_content": total_content,
                "processed_content": processed_content,
                "content_with_embeddings": content_with_embeddings,
                "processing_rate_percent": round(processing_rate, 1),
                "embedding_rate_percent": round(embedding_rate, 1)
            },
            "chunk_statistics": {
                "total_chunks": total_chunks,
                "chunks_with_embeddings": chunks_with_embeddings,
                "chunk_embedding_rate_percent": round(chunk_embedding_rate, 1),
                "average_chunk_size": round(chunk_result.avg_chunk_size or 0, 1)
            },
            "domain_statistics": {
                "unique_domains": domain_result.unique_domains or 0,
                "content_types": domain_result.content_types or 0
            },
            "rag_readiness": {
                "is_ready": is_ready,
                "readiness_score": round((processing_rate + chunk_embedding_rate) / 2, 1),
                "issues": readiness_issues,
                "recommendations": [
                    "Crawl more websites" if total_content < 10 else None,
                    "Process existing content" if processing_rate < 90 else None,
                    "Generate embeddings for chunks" if chunk_embedding_rate < 90 else None
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to calculate RAG stats for org {org_id}: {e}")
        return {
            "error": str(e),
            "content_statistics": {},
            "chunk_statistics": {},
            "domain_statistics": {},
            "rag_readiness": {"is_ready": False, "issues": [str(e)]}
        }
