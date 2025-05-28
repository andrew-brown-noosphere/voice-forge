"""
Automated RAG Pipeline Integration for VoiceForge
Seamlessly integrates RAG optimization into your org creation and content processing workflows
"""

import logging
import os
import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum

# Celery imports (assuming you're using Celery for background tasks)
try:
    from celery import Celery
    from celery.result import AsyncResult
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    logging.warning("Celery not available - using synchronous processing")

from database.session import get_db_session
from database.models import Content, ContentChunk
from database.db import Database
from optimized_processing_pipeline import OptimizedContentProcessor

logger = logging.getLogger(__name__)

class OptimizationStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class AutomatedRAGService:
    """
    Service that automatically handles RAG optimization for organizations
    with minimal manual intervention.
    """
    
    def __init__(self, celery_app=None):
        """
        Initialize the automated RAG service.
        
        Args:
            celery_app: Optional Celery app instance for background processing
        """
        self.celery_app = celery_app
        self.processor = OptimizedContentProcessor()
        
        # Configuration
        self.config = {
            'auto_optimize_new_orgs': True,
            'auto_optimize_on_content_threshold': 10,  # Auto-optimize when org gets 10+ new pieces of content
            'min_optimization_interval': timedelta(hours=6),  # Don't re-optimize more than every 6 hours
            'background_processing': CELERY_AVAILABLE and celery_app is not None,
            'max_concurrent_optimizations': 3,
        }
        
        # Track optimization status
        self._optimization_status = {}  # org_id -> status info
    
    def should_auto_optimize(self, org_id: str) -> tuple[bool, str]:
        """
        Determine if an organization should be auto-optimized.
        
        Args:
            org_id: Organization ID
            
        Returns:
            Tuple of (should_optimize, reason)
        """
        try:
            session = get_db_session()
            if hasattr(session, '__next__'):
                session = next(session)
            
            db = Database(session)
            
            # Check if already processing
            if self._is_currently_processing(org_id):
                return False, "Already processing"
            
            # Check minimum interval
            last_optimization = self._get_last_optimization_time(org_id)
            if last_optimization:
                time_since_last = datetime.utcnow() - last_optimization
                if time_since_last < self.config['min_optimization_interval']:
                    return False, f"Optimized {time_since_last} ago (too recent)"
            
            # Get current statistics
            stats = self.processor.get_processing_statistics(org_id)
            
            if not stats:
                return False, "Could not get org statistics"
            
            # Check if org has content
            if stats['content_stats']['total_content'] == 0:
                return False, "No content to optimize"
            
            # Check if optimization is needed
            reasons_to_optimize = []
            
            # New content threshold
            unprocessed_content = stats['content_stats']['content_without_chunks']
            if unprocessed_content >= self.config['auto_optimize_on_content_threshold']:
                reasons_to_optimize.append(f"{unprocessed_content} unprocessed items")
            
            # Low embedding coverage
            embedding_coverage = float(stats['chunk_stats']['embedding_coverage'].replace('%', ''))
            if embedding_coverage < 80:
                reasons_to_optimize.append(f"Low embedding coverage ({embedding_coverage:.1f}%)")
            
            # Missing embeddings
            missing_embeddings = stats['chunk_stats']['chunks_without_embeddings']
            if missing_embeddings > 50:  # Threshold for missing embeddings
                reasons_to_optimize.append(f"{missing_embeddings} chunks need embeddings")
            
            if reasons_to_optimize:
                return True, "; ".join(reasons_to_optimize)
            else:
                return False, "Already optimized"
                
        except Exception as e:
            logger.error(f"Error checking optimization need for org {org_id}: {e}")
            return False, f"Error checking: {str(e)}"
        finally:
            if 'session' in locals():
                session.close()
    
    def trigger_optimization(self, org_id: str, force: bool = False, **kwargs) -> Dict[str, Any]:
        """
        Trigger RAG optimization for an organization.
        
        Args:
            org_id: Organization ID
            force: Force optimization even if not needed
            **kwargs: Additional options for optimization
            
        Returns:
            Dictionary with optimization status and details
        """
        logger.info(f"🚀 Triggering RAG optimization for org {org_id}")
        
        # Check if optimization is needed (unless forced)
        if not force:
            should_optimize, reason = self.should_auto_optimize(org_id)
            if not should_optimize:
                logger.info(f"⏭️  Skipping optimization for org {org_id}: {reason}")
                return {
                    'status': OptimizationStatus.SKIPPED.value,
                    'org_id': org_id,
                    'reason': reason,
                    'timestamp': datetime.utcnow().isoformat()
                }
        
        # Use background processing if available
        if self.config['background_processing']:
            return self._trigger_background_optimization(org_id, **kwargs)
        else:
            return self._trigger_synchronous_optimization(org_id, **kwargs)
    
    def _trigger_background_optimization(self, org_id: str, **kwargs) -> Dict[str, Any]:
        """Trigger background optimization using Celery."""
        try:
            # Create Celery task
            task = optimize_org_rag_task.delay(org_id, **kwargs)
            
            # Track status
            self._optimization_status[org_id] = {
                'status': OptimizationStatus.PROCESSING.value,
                'task_id': task.id,
                'started_at': datetime.utcnow(),
                'org_id': org_id
            }
            
            logger.info(f"📋 Queued background optimization for org {org_id} (task: {task.id})")
            
            return {
                'status': OptimizationStatus.PROCESSING.value,
                'org_id': org_id,
                'task_id': task.id,
                'message': 'Optimization queued for background processing',
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to queue background optimization for org {org_id}: {e}")
            return {
                'status': OptimizationStatus.FAILED.value,
                'org_id': org_id,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _trigger_synchronous_optimization(self, org_id: str, **kwargs) -> Dict[str, Any]:
        """Trigger synchronous optimization."""
        try:
            logger.info(f"🔄 Running synchronous optimization for org {org_id}")
            
            # Update status
            self._optimization_status[org_id] = {
                'status': OptimizationStatus.PROCESSING.value,
                'started_at': datetime.utcnow(),
                'org_id': org_id
            }
            
            # Run optimization
            results = self.processor.run_full_optimization(org_id, **kwargs)
            
            # Update status
            final_status = OptimizationStatus.COMPLETED if results['success'] else OptimizationStatus.FAILED
            self._optimization_status[org_id].update({
                'status': final_status.value,
                'completed_at': datetime.utcnow(),
                'results': results
            })
            
            logger.info(f"✅ Completed synchronous optimization for org {org_id}: {final_status.value}")
            
            return {
                'status': final_status.value,
                'org_id': org_id,
                'results': results,
                'message': 'Optimization completed synchronously',
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Synchronous optimization failed for org {org_id}: {e}")
            
            # Update status
            self._optimization_status[org_id].update({
                'status': OptimizationStatus.FAILED.value,
                'completed_at': datetime.utcnow(),
                'error': str(e)
            })
            
            return {
                'status': OptimizationStatus.FAILED.value,
                'org_id': org_id,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def get_optimization_status(self, org_id: str) -> Optional[Dict[str, Any]]:
        """Get the current optimization status for an organization."""
        return self._optimization_status.get(org_id)
    
    def _is_currently_processing(self, org_id: str) -> bool:
        """Check if an organization is currently being optimized."""
        status_info = self._optimization_status.get(org_id)
        if not status_info:
            return False
        
        if status_info['status'] != OptimizationStatus.PROCESSING.value:
            return False
        
        # Check if it's been processing too long (safety check)
        started_at = status_info.get('started_at')
        if started_at:
            processing_time = datetime.utcnow() - started_at
            if processing_time > timedelta(hours=2):  # 2 hour timeout
                logger.warning(f"Optimization for org {org_id} has been processing for {processing_time} - marking as failed")
                status_info['status'] = OptimizationStatus.FAILED.value
                status_info['error'] = 'Processing timeout'
                return False
        
        return True
    
    def _get_last_optimization_time(self, org_id: str) -> Optional[datetime]:
        """Get the timestamp of the last optimization for an org."""
        status_info = self._optimization_status.get(org_id)
        if status_info and status_info.get('completed_at'):
            return status_info['completed_at']
        return None

# Initialize the automated service
automated_rag_service = AutomatedRAGService()

# Celery task definition (only if Celery is available)
if CELERY_AVAILABLE:
    # You'll need to configure this with your existing Celery app
    celery_app = Celery('voiceforge_rag')
    
    @celery_app.task(bind=True, max_retries=3)
    def optimize_org_rag_task(self, org_id: str, **kwargs):
        """
        Celery task for background RAG optimization.
        
        Args:
            org_id: Organization ID to optimize
            **kwargs: Additional optimization options
            
        Returns:
            Optimization results
        """
        try:
            logger.info(f"🚀 Starting background RAG optimization for org {org_id}")
            
            # Create processor instance
            processor = OptimizedContentProcessor(
                chunk_size=kwargs.get('chunk_size', 400),
                chunk_overlap=kwargs.get('chunk_overlap', 80),
                batch_size=kwargs.get('batch_size', 32)
            )
            
            # Run optimization
            results = processor.run_full_optimization(
                org_id=org_id,
                max_content=kwargs.get('max_content')
            )
            
            # Update service status
            automated_rag_service._optimization_status[org_id].update({
                'status': OptimizationStatus.COMPLETED.value if results['success'] else OptimizationStatus.FAILED.value,
                'completed_at': datetime.utcnow(),
                'results': results
            })
            
            logger.info(f"✅ Completed background RAG optimization for org {org_id}: success={results['success']}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Background RAG optimization failed for org {org_id}: {e}")
            
            # Update service status
            automated_rag_service._optimization_status[org_id].update({
                'status': OptimizationStatus.FAILED.value,
                'completed_at': datetime.utcnow(),
                'error': str(e)
            })
            
            # Retry logic
            if self.request.retries < self.max_retries:
                logger.info(f"🔄 Retrying optimization for org {org_id} (attempt {self.request.retries + 1})")
                raise self.retry(countdown=60 * (2 ** self.request.retries))  # Exponential backoff
            
            raise e

# Integration hooks for your existing codebase
class RAGIntegrationHooks:
    """
    Integration hooks to add to your existing VoiceForge codebase.
    """
    
    @staticmethod
    def on_organization_created(org_id: str, org_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Hook to call when a new organization is created.
        
        Args:
            org_id: New organization ID
            org_data: Organization data
            
        Returns:
            Optimization trigger result
        """
        logger.info(f"🏢 New organization created: {org_id}")
        
        if automated_rag_service.config['auto_optimize_new_orgs']:
            # Don't optimize immediately - wait for content
            logger.info(f"⏳ Will auto-optimize org {org_id} when content is added")
            return {'status': 'waiting_for_content', 'org_id': org_id}
        else:
            return {'status': 'auto_optimization_disabled', 'org_id': org_id}
    
    @staticmethod
    def on_crawl_completed(crawl_id: str, org_id: str, crawl_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Hook to call when a content crawl is completed.
        
        Args:
            crawl_id: Crawl ID
            org_id: Organization ID
            crawl_results: Crawl results
            
        Returns:
            Optimization trigger result
        """
        logger.info(f"🕷️ Crawl completed for org {org_id}: {crawl_results.get('pages_crawled', 0)} pages")
        
        # Check if we should trigger optimization
        should_optimize, reason = automated_rag_service.should_auto_optimize(org_id)
        
        if should_optimize:
            logger.info(f"🚀 Triggering RAG optimization for org {org_id}: {reason}")
            return automated_rag_service.trigger_optimization(org_id)
        else:
            logger.info(f"⏭️ Not triggering optimization for org {org_id}: {reason}")
            return {'status': 'not_needed', 'reason': reason, 'org_id': org_id}
    
    @staticmethod
    def on_content_added(org_id: str, content_count: int) -> Dict[str, Any]:
        """
        Hook to call when content is added to an organization.
        
        Args:
            org_id: Organization ID
            content_count: Number of content items added
            
        Returns:
            Optimization trigger result
        """
        logger.info(f"📄 Content added to org {org_id}: {content_count} items")
        
        # Check if we've hit the threshold for auto-optimization
        should_optimize, reason = automated_rag_service.should_auto_optimize(org_id)
        
        if should_optimize:
            logger.info(f"🚀 Auto-triggering RAG optimization for org {org_id}: {reason}")
            return automated_rag_service.trigger_optimization(org_id)
        else:
            logger.debug(f"⏳ Not yet ready for optimization for org {org_id}: {reason}")
            return {'status': 'waiting', 'reason': reason, 'org_id': org_id}
    
    @staticmethod
    def on_rag_query_requested(org_id: str, query: str) -> Dict[str, Any]:
        """
        Hook to call when a RAG query is requested (lazy optimization).
        
        Args:
            org_id: Organization ID
            query: Query string
            
        Returns:
            Optimization status or trigger result
        """
        # Check if org has been optimized recently
        should_optimize, reason = automated_rag_service.should_auto_optimize(org_id)
        
        if should_optimize and "no content" not in reason.lower():
            logger.info(f"🔍 RAG query for unoptimized org {org_id} - triggering optimization")
            return automated_rag_service.trigger_optimization(org_id, force=True)
        
        return {'status': 'ready', 'org_id': org_id}

# Convenience functions for easy integration
def auto_optimize_org(org_id: str, **kwargs) -> Dict[str, Any]:
    """Convenience function to trigger optimization for an org."""
    return automated_rag_service.trigger_optimization(org_id, **kwargs)

def check_org_optimization_status(org_id: str) -> Optional[Dict[str, Any]]:
    """Convenience function to check optimization status."""
    return automated_rag_service.get_optimization_status(org_id)

def is_org_ready_for_rag(org_id: str) -> tuple[bool, str]:
    """Convenience function to check if org is ready for RAG queries."""
    should_optimize, reason = automated_rag_service.should_auto_optimize(org_id)
    return not should_optimize, reason
