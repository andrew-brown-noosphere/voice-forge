from celery_app import celery_app
from datetime import datetime, timedelta
import uuid
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=3)
def execute_automated_signal_scan(self, source_id: str):
    """Automated daily signal scanning for a configured source"""
    try:
        from database.session import get_db_session
        from database.models import SignalSource, Signal
        from api.signals import SignalService
        
        db = get_db_session()
        source = db.query(SignalSource).filter(SignalSource.source_id == source_id).first()
        
        if not source or not source.is_active:
            logger.info(f"Source {source_id} is inactive, skipping scan")
            return
        
        # Combine user keywords with AI suggestions
        all_keywords = list(set(source.keywords + (source.ai_suggested_keywords or [])))
        all_sources = [source.source_name] + (source.ai_suggested_sources or [])
        
        # Execute signal discovery
        signal_service = SignalService(db)
        discovery_request = {
            'platform': source.platform,
            'sources': all_sources,
            'keywords': all_keywords,
            'time_filter': 'day',
            'max_items_per_source': 50,
            'relevance_threshold': source.relevance_threshold
        }
        
        result = signal_service.discover_signals(discovery_request, source.org_id)
        
        # Update source performance
        update_source_performance.delay(source_id, result.signals_found)
        
        # Schedule AI analysis if significant signals found
        if result.signals_found >= 5:
            analyze_source_performance_and_recommend.delay(source_id)
        
        # Update last crawl time
        source.last_crawled_at = datetime.utcnow()
        db.commit()
        db.close()
        
        # Schedule next scan
        schedule_next_scan.delay(source_id)
        
        logger.info(f"Automated scan completed for {source_id}: {result.signals_found} signals found")
        return {'source_id': source_id, 'signals_found': result.signals_found, 'status': 'completed'}
        
    except Exception as exc:
        logger.error(f"Automated scan failed for {source_id}: {exc}")
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))

@celery_app.task
def schedule_next_scan(source_id: str):
    """Schedule the next automated scan based on frequency"""
    from database.session import get_db_session
    from database.models import SignalSource
    
    db = get_db_session()
    source = db.query(SignalSource).filter(SignalSource.source_id == source_id).first()
    
    if source and source.is_active:
        if source.crawl_frequency == 'daily':
            next_scan = datetime.utcnow() + timedelta(days=1)
        elif source.crawl_frequency == 'weekly':
            next_scan = datetime.utcnow() + timedelta(weeks=1)
        else:  # hourly
            next_scan = datetime.utcnow() + timedelta(hours=1)
        
        execute_automated_signal_scan.apply_async(args=[source_id], eta=next_scan)
        logger.info(f"Next scan scheduled for {source_id} at {next_scan}")
    
    db.close()

@celery_app.task
def update_source_performance(source_id: str, signals_found: int):
    """Update performance metrics for a signal source"""
    from database.session import get_db_session
    from database.models import SignalSource
    
    db = get_db_session()
    source = db.query(SignalSource).filter(SignalSource.source_id == source_id).first()
    
    if source:
        metrics = source.performance_metrics or {}
        today = datetime.utcnow().date().isoformat()
        
        metrics[today] = {
            'signals_found': signals_found,
            'scan_time': datetime.utcnow().isoformat()
        }
        
        # Keep only last 30 days
        cutoff_date = (datetime.utcnow() - timedelta(days=30)).date().isoformat()
        metrics = {k: v for k, v in metrics.items() if k >= cutoff_date}
        
        source.performance_metrics = metrics
        db.commit()
    
    db.close()

@celery_app.task
def analyze_source_performance_and_recommend(source_id: str):
    """AI-powered analysis of source performance with recommendations"""
    try:
        from database.session import get_db_session
        from database.models import SignalSource, Signal, SignalRecommendation
        from signals.ai_service import SignalIntelligenceService
        
        db = get_db_session()
        source = db.query(SignalSource).filter(SignalSource.source_id == source_id).first()
        
        if not source or not source.ai_optimization_enabled:
            return
        
        # Get recent signals for analysis
        recent_signals = db.query(Signal).filter(
            Signal.org_id == source.org_id,
            Signal.platform == source.platform,
            Signal.discovered_at >= datetime.utcnow() - timedelta(days=7)
        ).all()
        
        # AI analysis
        ai_service = SignalIntelligenceService()
        recommendations = ai_service.analyze_and_recommend_optimizations(source, recent_signals)
        
        # Store recommendations
        for rec in recommendations:
            recommendation = SignalRecommendation(
                recommendation_id=str(uuid.uuid4()),
                source_id=source_id,
                org_id=source.org_id,
                recommendation_type=rec['type'],
                platform=source.platform,
                recommended_item=rec['item'],
                confidence_score=rec['confidence'],
                reasoning=rec['reasoning'],
                supporting_data=rec.get('data', {}),
                predicted_improvement=rec.get('predicted_improvement', {})
            )
            db.add(recommendation)
        
        source.last_ai_analysis = datetime.utcnow()
        db.commit()
        db.close()
        
        logger.info(f"AI analysis completed for {source_id}: {len(recommendations)} recommendations")
        
    except Exception as e:
        logger.error(f"AI analysis failed for {source_id}: {e}")
