"""
Celery tasks for content processing operations.

This module defines distributed tasks for handling content processing
operations that can run asynchronously across multiple workers.
"""
import logging
from typing import Dict, Any, List
from celery import current_task
from celery_app import celery_app
from database.session import get_db_session

logger = logging.getLogger(__name__)

@celery_app.task(bind=True)
def process_content_task(self, content_id: str, org_id: str):
    """
    Celery task to process a single content item.
    
    Args:
        content_id: Content ID to process
        org_id: Organization ID for multi-tenant isolation
    
    Returns:
        Processing status dictionary
    """
    try:
        logger.info(f"🔄 Starting content processing for {content_id}")
        
        # Get database session
        db_session = get_db_session()
        
        try:
            # Initialize processor service
            from processor.service import ProcessorService
            processor_service = ProcessorService(db_session)
            
            # Process the content
            result = processor_service.process_single_content(
                content_id=content_id,
                org_id=org_id,
                task_callback=None
            )
            
            logger.info(f"✅ Content processing completed for {content_id}")
            return result
            
        finally:
            db_session.close()
            
    except Exception as exc:
        error_msg = str(exc)
        logger.error(f"❌ Content processing failed for {content_id}: {error_msg}", exc_info=True)
        
        return {
            "status": "failed",
            "error": error_msg,
            "content_id": content_id
        }

@celery_app.task(bind=True)
def batch_process_content_task(self, content_ids: List[str], org_id: str):
    """
    Celery task to process multiple content items in batch.
    
    Args:
        content_ids: List of content IDs to process
        org_id: Organization ID for multi-tenant isolation
    
    Returns:
        Batch processing status dictionary
    """
    try:
        logger.info(f"🔄 Starting batch content processing for {len(content_ids)} items")
        
        # Get database session
        db_session = get_db_session()
        
        try:
            # Initialize processor service
            from processor.service import ProcessorService
            processor_service = ProcessorService(db_session)
            
            # Process content in batch
            results = []
            for i, content_id in enumerate(content_ids):
                try:
                    # Process single content
                    result = processor_service.process_single_content(content_id, org_id)
                    results.append({"content_id": content_id, "status": "success", "result": result})
                    
                except Exception as e:
                    logger.error(f"Failed to process content {content_id}: {str(e)}")
                    results.append({"content_id": content_id, "status": "error", "error": str(e)})
            
            summary = {
                "total": len(content_ids),
                "successful": len([r for r in results if r["status"] == "success"]),
                "failed": len([r for r in results if r["status"] == "error"]),
                "results": results
            }
            
            logger.info(f"✅ Batch processing completed: {summary['successful']}/{summary['total']} successful")
            return summary
            
        finally:
            db_session.close()
            
    except Exception as exc:
        error_msg = str(exc)
        logger.error(f"❌ Batch processing failed: {error_msg}", exc_info=True)
        
        return {
            "status": "failed",
            "error": error_msg,
            "total": len(content_ids)
        }

@celery_app.task(bind=True)
def extract_entities_task(self, content_ids: List[str], org_id: str):
    """
    Celery task to extract entities from content.
    
    Args:
        content_ids: List of content IDs to extract entities from
        org_id: Organization ID for multi-tenant isolation
    
    Returns:
        Entity extraction results
    """
    try:
        logger.info(f"🔍 Starting entity extraction for {len(content_ids)} items")
        
        # Get database session
        db_session = get_db_session()
        
        try:
            # Initialize processor service
            from processor.service import ProcessorService
            processor_service = ProcessorService(db_session)
            
            # Extract entities
            result = processor_service.extract_entities_batch(
                content_ids=content_ids,
                org_id=org_id,
                task_callback=None
            )
            
            logger.info(f"✅ Entity extraction completed for {len(content_ids)} items")
            return result
            
        finally:
            db_session.close()
            
    except Exception as exc:
        error_msg = str(exc)
        logger.error(f"❌ Entity extraction failed: {error_msg}", exc_info=True)
        
        return {
            "status": "failed",
            "error": error_msg,
            "total": len(content_ids)
        }

@celery_app.task(bind=True)
def generate_embeddings_task(self, content_ids: List[str], org_id: str):
    """
    Celery task to generate embeddings for content.
    
    Args:
        content_ids: List of content IDs to generate embeddings for
        org_id: Organization ID for multi-tenant isolation
    
    Returns:
        Embedding generation results
    """
    try:
        logger.info(f"🧠 Starting embedding generation for {len(content_ids)} items")
        
        # Get database session
        db_session = get_db_session()
        
        try:
            # Initialize processor service
            from processor.service import ProcessorService
            processor_service = ProcessorService(db_session)
            
            # Generate embeddings
            result = processor_service.generate_embeddings_batch(
                content_ids=content_ids,
                org_id=org_id,
                task_callback=None
            )
            
            logger.info(f"✅ Embedding generation completed for {len(content_ids)} items")
            return result
            
        finally:
            db_session.close()
            
    except Exception as exc:
        error_msg = str(exc)
        logger.error(f"❌ Embedding generation failed: {error_msg}", exc_info=True)
        
        return {
            "status": "failed",
            "error": error_msg,
            "total": len(content_ids)
        }
