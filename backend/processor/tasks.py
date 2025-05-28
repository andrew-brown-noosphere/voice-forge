"""
Celery tasks for content processing operations.

This module defines distributed tasks for handling content processing
operations that can run asynchronously across multiple workers.
"""
import logging
from typing import Dict, Any, List
from celery import current_task
from celery_app import celery_app, RETRY_KWARGS
from database.session import get_db_session

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, **RETRY_KWARGS)
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
        
        # Update task state
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "Processing content", "progress": 0}
        )
        
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
                task_callback=lambda state, meta: current_task.update_state(state=state, meta=meta)
            )
            
            logger.info(f"✅ Content processing completed for {content_id}")
            return result
            
        finally:
            db_session.close()
            
    except Exception as exc:
        logger.error(f"❌ Content processing failed for {content_id}: {str(exc)}")
        
        # Update task state to failed
        current_task.update_state(
            state="FAILURE",
            meta={"status": f"Processing failed: {str(exc)}", "error": str(exc)}
        )
        
        raise exc

@celery_app.task(bind=True, **RETRY_KWARGS)
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
        
        # Update task state
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "Processing content batch", "progress": 0, "total": len(content_ids)}
        )
        
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
                    # Update progress
                    progress = int((i / len(content_ids)) * 100)
                    current_task.update_state(
                        state="PROGRESS",
                        meta={
                            "status": f"Processing content {i+1}/{len(content_ids)}",
                            "progress": progress,
                            "current_content": content_id
                        }
                    )
                    
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
        logger.error(f"❌ Batch processing failed: {str(exc)}")
        
        # Update task state to failed
        current_task.update_state(
            state="FAILURE",
            meta={"status": f"Batch processing failed: {str(exc)}", "error": str(exc)}
        )
        
        raise exc

@celery_app.task(bind=True, **RETRY_KWARGS)
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
        
        # Update task state
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "Extracting entities", "progress": 0}
        )
        
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
                task_callback=lambda state, meta: current_task.update_state(state=state, meta=meta)
            )
            
            logger.info(f"✅ Entity extraction completed for {len(content_ids)} items")
            return result
            
        finally:
            db_session.close()
            
    except Exception as exc:
        logger.error(f"❌ Entity extraction failed: {str(exc)}")
        
        # Update task state to failed
        current_task.update_state(
            state="FAILURE",
            meta={"status": f"Entity extraction failed: {str(exc)}", "error": str(exc)}
        )
        
        raise exc

@celery_app.task(bind=True, **RETRY_KWARGS)
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
        
        # Update task state
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "Generating embeddings", "progress": 0}
        )
        
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
                task_callback=lambda state, meta: current_task.update_state(state=state, meta=meta)
            )
            
            logger.info(f"✅ Embedding generation completed for {len(content_ids)} items")
            return result
            
        finally:
            db_session.close()
            
    except Exception as exc:
        logger.error(f"❌ Embedding generation failed: {str(exc)}")
        
        # Update task state to failed
        current_task.update_state(
            state="FAILURE",
            meta={"status": f"Embedding generation failed: {str(exc)}", "error": str(exc)}
        )
        
        raise exc