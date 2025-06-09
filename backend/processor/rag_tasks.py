"""
Celery tasks for RAG (Retrieval-Augmented Generation) operations.

This module defines distributed tasks for handling RAG-specific processing
operations that can run asynchronously across multiple workers.
"""
import logging
from typing import Dict, Any, List, Optional
from celery import current_task
from celery_app import celery_app
from database.session import get_db_session

logger = logging.getLogger(__name__)

@celery_app.task(bind=True)
def chunk_content_task(self, content_id: str, org_id: str):
    """
    Celery task to chunk content for RAG.
    
    Args:
        content_id: Content ID to chunk
        org_id: Organization ID for multi-tenant isolation
    
    Returns:
        Chunking results
    """
    try:
        logger.info(f"✂️ Starting content chunking for {content_id}")
        
        # Get database session
        db_session = get_db_session()
        
        try:
            # Initialize RAG service
            from processor.rag_service import RAGService
            rag_service = RAGService(db_session)
            
            # Chunk the content
            result = rag_service.chunk_content_for_rag(
                content_id=content_id,
                org_id=org_id,
                task_callback=None
            )
            
            logger.info(f"✅ Content chunking completed for {content_id}")
            return result
            
        finally:
            db_session.close()
            
    except Exception as exc:
        error_msg = str(exc)
        logger.error(f"❌ Content chunking failed for {content_id}: {error_msg}", exc_info=True)
        
        return {
            "status": "failed",
            "error": error_msg,
            "content_id": content_id
        }

@celery_app.task(bind=True)
def generate_chunk_embeddings_task(self, content_id: str, org_id: str):
    """
    Celery task to generate embeddings for content chunks.
    
    Args:
        content_id: Content ID whose chunks need embeddings
        org_id: Organization ID for multi-tenant isolation
    
    Returns:
        Embedding generation results
    """
    try:
        logger.info(f"🧠 Starting chunk embedding generation for {content_id}")
        
        # Get database session
        db_session = get_db_session()
        
        try:
            # Initialize RAG service
            from processor.rag_service import RAGService
            rag_service = RAGService(db_session)
            
            # Generate embeddings for chunks
            result = rag_service.generate_chunk_embeddings(
                content_id=content_id,
                org_id=org_id,
                task_callback=None
            )
            
            logger.info(f"✅ Chunk embedding generation completed for {content_id}")
            return result
            
        finally:
            db_session.close()
            
    except Exception as exc:
        error_msg = str(exc)
        logger.error(f"❌ Chunk embedding generation failed for {content_id}: {error_msg}", exc_info=True)
        
        return {
            "status": "failed",
            "error": error_msg,
            "content_id": content_id
        }

@celery_app.task(bind=True)
def process_crawl_for_rag_task(self, crawl_id: str, org_id: str):
    """
    Celery task to process an entire crawl for RAG.
    
    Args:
        crawl_id: Crawl ID to process
        org_id: Organization ID for multi-tenant isolation
    
    Returns:
        RAG processing results
    """
    try:
        logger.info(f"🤖 Starting RAG processing for crawl {crawl_id}")
        
        # Get database session
        db_session = get_db_session()
        
        try:
            # Initialize RAG service
            from processor.rag_service import RAGService
            rag_service = RAGService(db_session)
            
            # Process entire crawl for RAG
            result = rag_service.process_crawl_for_rag(
                crawl_id=crawl_id,
                org_id=org_id,
                task_callback=None
            )
            
            logger.info(f"✅ RAG processing completed for crawl {crawl_id}")
            return result
            
        finally:
            db_session.close()
            
    except Exception as exc:
        error_msg = str(exc)
        logger.error(f"❌ RAG processing failed for crawl {crawl_id}: {error_msg}", exc_info=True)
        
        return {
            "status": "failed",
            "error": error_msg,
            "crawl_id": crawl_id
        }

@celery_app.task(bind=True)
def optimize_vector_index_task(self, org_id: str):
    """
    Celery task to optimize vector indexes for better search performance.
    
    Args:
        org_id: Organization ID for multi-tenant isolation
    
    Returns:
        Optimization results
    """
    try:
        logger.info(f"⚡ Starting vector index optimization for org {org_id}")
        
        # Get database session
        db_session = get_db_session()
        
        try:
            # Initialize RAG service
            from processor.rag_service import RAGService
            rag_service = RAGService(db_session)
            
            # Optimize indexes
            result = rag_service.optimize_vector_indexes(
                org_id=org_id,
                task_callback=None
            )
            
            logger.info(f"✅ Vector index optimization completed for org {org_id}")
            return result
            
        finally:
            db_session.close()
            
    except Exception as exc:
        error_msg = str(exc)
        logger.error(f"❌ Vector index optimization failed for org {org_id}: {error_msg}", exc_info=True)
        
        return {
            "status": "failed",
            "error": error_msg,
            "org_id": org_id
        }

@celery_app.task(bind=True)
def generate_content_summary_task(self, content_ids: List[str], org_id: str):
    """
    Celery task to generate AI summaries for content.
    
    Args:
        content_ids: List of content IDs to summarize
        org_id: Organization ID for multi-tenant isolation
    
    Returns:
        Summary generation results
    """
    try:
        logger.info(f"📝 Starting content summarization for {len(content_ids)} items")
        
        # Get database session
        db_session = get_db_session()
        
        try:
            # Initialize RAG service
            from processor.rag_service import RAGService
            rag_service = RAGService(db_session)
            
            # Generate summaries
            result = rag_service.generate_content_summaries(
                content_ids=content_ids,
                org_id=org_id,
                task_callback=None
            )
            
            logger.info(f"✅ Content summarization completed for {len(content_ids)} items")
            return result
            
        finally:
            db_session.close()
            
    except Exception as exc:
        error_msg = str(exc)
        logger.error(f"❌ Content summarization failed: {error_msg}", exc_info=True)
        
        return {
            "status": "failed",
            "error": error_msg,
            "total": len(content_ids)
        }

@celery_app.task(bind=True)
def rag_health_check_task(self):
    """
    Health check task specifically for RAG functionality.
    
    Returns:
        RAG health status
    """
    try:
        logger.info("🔍 Running RAG health check")
        
        # Get database session
        db_session = get_db_session()
        
        try:
            # Initialize RAG service
            from processor.rag_service import RAGService
            rag_service = RAGService(db_session)
            
            # Perform health checks
            health_status = rag_service.health_check()
            
            result = {
                "status": "healthy",
                "rag_status": health_status,
                "task_id": str(current_task.request.id)
            }
            
            logger.info("✅ RAG health check passed")
            return result
            
        finally:
            db_session.close()
            
    except Exception as exc:
        error_msg = str(exc)
        logger.error(f"❌ RAG health check failed: {error_msg}", exc_info=True)
        
        return {
            "status": "failed",
            "error": error_msg
        }
