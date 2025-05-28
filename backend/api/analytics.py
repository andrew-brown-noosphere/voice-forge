"""
Analytics endpoints for the VoiceForge API.
Provides comprehensive analytics and insights about crawled data.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from collections import Counter
import re
from datetime import datetime, timedelta

from auth.clerk_auth import get_current_user_with_org, AuthUser, get_org_id_from_user
from database.session import get_db_session
from database.models import Crawl, Content, ContentChunk, MarketingTemplate

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/dashboard", response_model=Dict[str, Any])
async def get_dashboard_analytics(
    current_user: AuthUser = Depends(get_current_user_with_org),
    db: Session = Depends(get_db_session)
):
    """
    Get comprehensive analytics for the dashboard.
    
    Returns metrics including:
    - Total pages crawled
    - Dataset size metrics
    - Content distribution
    - Word frequency analysis
    - Processing statistics
    - Recent activity trends
    """
    try:
        org_id = get_org_id_from_user(current_user)
        
        # Basic counts
        total_crawls = db.query(func.count(Crawl.id)).filter(Crawl.org_id == org_id).scalar() or 0
        total_pages = db.query(func.sum(Crawl.pages_crawled)).filter(Crawl.org_id == org_id).scalar() or 0
        total_content_items = db.query(func.count(Content.id)).filter(Content.org_id == org_id).scalar() or 0
        total_chunks = db.query(func.count(ContentChunk.id)).filter(ContentChunk.org_id == org_id).scalar() or 0
        total_templates = db.query(func.count(MarketingTemplate.id)).filter(MarketingTemplate.org_id == org_id).scalar() or 0
        
        # Dataset size metrics
        total_text_length = db.query(func.sum(func.length(Content.text))).filter(Content.org_id == org_id).scalar() or 0
        avg_content_length = db.query(func.avg(func.length(Content.text))).filter(Content.org_id == org_id).scalar() or 0
        
        # Content type distribution
        content_types = db.query(
            Content.content_type,
            func.count(Content.id).label('count')
        ).filter(Content.org_id == org_id).group_by(Content.content_type).all()
        
        content_type_distribution = {ct.content_type: ct.count for ct in content_types}
        
        # Domain distribution
        domains = db.query(
            Content.domain,
            func.count(Content.id).label('count')
        ).filter(Content.org_id == org_id).group_by(Content.domain).all()
        
        domain_distribution = {d.domain: d.count for d in domains}
        
        # Processing statistics
        processed_content = db.query(func.count(Content.id)).filter(
            Content.org_id == org_id,
            Content.is_processed == True
        ).scalar() or 0
        
        unprocessed_content = total_content_items - processed_content
        processing_rate = (processed_content / total_content_items * 100) if total_content_items > 0 else 0
        
        # Embeddings statistics
        content_with_embeddings = db.query(func.count(Content.id)).filter(
            Content.org_id == org_id,
            Content.embedding.isnot(None)
        ).scalar() or 0
        
        chunks_with_embeddings = db.query(func.count(ContentChunk.id)).filter(
            ContentChunk.org_id == org_id,
            ContentChunk.embedding.isnot(None)
        ).scalar() or 0
        
        # Recent activity (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_crawls = db.query(func.count(Crawl.id)).filter(
            Crawl.org_id == org_id,
            Crawl.start_time >= week_ago
        ).scalar() or 0
        
        recent_content = db.query(func.count(Content.id)).filter(
            Content.org_id == org_id,
            Content.extracted_at >= week_ago
        ).scalar() or 0
        
        # Crawl status distribution
        crawl_statuses = db.query(
            Crawl.state,
            func.count(Crawl.id).label('count')
        ).filter(Crawl.org_id == org_id).group_by(Crawl.state).all()
        
        crawl_status_distribution = {cs.state: cs.count for cs in crawl_statuses}
        
        # Language distribution (if available)
        languages = db.query(
            Content.language,
            func.count(Content.id).label('count')
        ).filter(
            Content.org_id == org_id,
            Content.language.isnot(None)
        ).group_by(Content.language).all()
        
        language_distribution = {lang.language or 'unknown': lang.count for lang in languages}
        
        return {
            "overview": {
                "total_crawls": total_crawls,
                "total_pages_crawled": int(total_pages),
                "total_content_items": total_content_items,
                "total_chunks": total_chunks,
                "total_templates": total_templates
            },
            "dataset_metrics": {
                "total_text_characters": int(total_text_length),
                "total_text_mb": round(total_text_length / (1024 * 1024), 2),
                "average_content_length": int(avg_content_length) if avg_content_length else 0,
                "processing_rate_percent": round(processing_rate, 1)
            },
            "embeddings": {
                "content_with_embeddings": content_with_embeddings,
                "chunks_with_embeddings": chunks_with_embeddings,
                "embedding_coverage_percent": round(
                    (content_with_embeddings / total_content_items * 100) if total_content_items > 0 else 0, 1
                )
            },
            "distributions": {
                "content_types": content_type_distribution,
                "domains": domain_distribution,
                "crawl_statuses": crawl_status_distribution,
                "languages": language_distribution
            },
            "processing": {
                "processed_content": processed_content,
                "unprocessed_content": unprocessed_content,
                "processing_rate_percent": round(processing_rate, 1)
            },
            "recent_activity": {
                "crawls_last_7_days": recent_crawls,
                "content_added_last_7_days": recent_content
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analytics: {str(e)}"
        )

@router.get("/wordcloud", response_model=Dict[str, Any])
async def get_wordcloud_data(
    limit: int = 100,
    min_length: int = 3,
    domain: Optional[str] = None,
    content_type: Optional[str] = None,
    current_user: AuthUser = Depends(get_current_user_with_org),
    db: Session = Depends(get_db_session)
):
    """
    Get word frequency data for word cloud visualization.
    
    Args:
        limit: Maximum number of words to return
        min_length: Minimum word length to include
        domain: Filter by specific domain
        content_type: Filter by content type
    
    Returns word frequency data suitable for word cloud libraries.
    """
    try:
        org_id = get_org_id_from_user(current_user)
        
        # Build query with filters
        query = db.query(Content.text).filter(Content.org_id == org_id)
        
        if domain:
            query = query.filter(Content.domain == domain)
        if content_type:
            query = query.filter(Content.content_type == content_type)
        
        # Get all text content
        content_texts = query.limit(1000).all()  # Limit to prevent memory issues
        
        if not content_texts:
            return {"words": [], "total_words": 0, "unique_words": 0}
        
        # Combine all text
        combined_text = " ".join([content.text for content in content_texts])
        
        # Extract words (basic text processing)
        # Remove HTML tags, special characters, and normalize
        clean_text = re.sub(r'<[^>]+>', ' ', combined_text)  # Remove HTML
        clean_text = re.sub(r'[^\w\s]', ' ', clean_text)     # Remove punctuation
        clean_text = clean_text.lower()                       # Lowercase
        
        # Split into words and filter
        words = [
            word for word in clean_text.split()
            if len(word) >= min_length and word.isalpha()
        ]
        
        # Common stop words to filter out
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before',
            'after', 'above', 'below', 'between', 'among', 'within', 'without',
            'under', 'over', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'shall', 'this', 'that',
            'these', 'those', 'a', 'an', 'as', 'if', 'each', 'when', 'where',
            'why', 'how', 'all', 'any', 'both', 'either', 'neither', 'not',
            'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'now'
        }
        
        # Filter out stop words
        filtered_words = [word for word in words if word not in stop_words]
        
        # Count word frequencies
        word_counts = Counter(filtered_words)
        
        # Get top words
        top_words = word_counts.most_common(limit)
        
        # Format for word cloud (word, frequency)
        word_data = [{"text": word, "value": count} for word, count in top_words]
        
        return {
            "words": word_data,
            "total_words": len(words),
            "unique_words": len(word_counts),
            "filtered_unique_words": len(top_words)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get word cloud data: {str(e)}"
        )

@router.get("/content-trends", response_model=Dict[str, Any])
async def get_content_trends(
    days: int = 30,
    current_user: AuthUser = Depends(get_current_user_with_org),
    db: Session = Depends(get_db_session)
):
    """
    Get content creation trends over time.
    
    Args:
        days: Number of days to look back
    
    Returns daily content creation statistics.
    """
    try:
        org_id = get_org_id_from_user(current_user)
        
        # Calculate date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Get daily content counts
        daily_content = db.execute(
            text("""
                SELECT 
                    DATE(extracted_at) as date,
                    COUNT(*) as content_count,
                    COUNT(DISTINCT domain) as unique_domains
                FROM contents 
                WHERE org_id = :org_id 
                    AND DATE(extracted_at) >= :start_date 
                    AND DATE(extracted_at) <= :end_date
                GROUP BY DATE(extracted_at)
                ORDER BY DATE(extracted_at)
            """),
            {"org_id": org_id, "start_date": start_date, "end_date": end_date}
        ).fetchall()
        
        # Get daily crawl counts
        daily_crawls = db.execute(
            text("""
                SELECT 
                    DATE(start_time) as date,
                    COUNT(*) as crawl_count,
                    SUM(pages_crawled) as total_pages
                FROM crawls 
                WHERE org_id = :org_id 
                    AND DATE(start_time) >= :start_date 
                    AND DATE(start_time) <= :end_date
                GROUP BY DATE(start_time)
                ORDER BY DATE(start_time)
            """),
            {"org_id": org_id, "start_date": start_date, "end_date": end_date}
        ).fetchall()
        
        # Format data for charts
        content_trend = [
            {
                "date": str(row.date),
                "content_count": row.content_count,
                "unique_domains": row.unique_domains
            }
            for row in daily_content
        ]
        
        crawl_trend = [
            {
                "date": str(row.date),
                "crawl_count": row.crawl_count,
                "total_pages": int(row.total_pages or 0)
            }
            for row in daily_crawls
        ]
        
        return {
            "content_trend": content_trend,
            "crawl_trend": crawl_trend,
            "date_range": {
                "start_date": str(start_date),
                "end_date": str(end_date),
                "days": days
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get content trends: {str(e)}"
        )

@router.get("/top-domains", response_model=List[Dict[str, Any]])
async def get_top_domains(
    limit: int = 10,
    current_user: AuthUser = Depends(get_current_user_with_org),
    db: Session = Depends(get_db_session)
):
    """Get top domains by content volume with detailed statistics."""
    try:
        org_id = get_org_id_from_user(current_user)
        
        domain_stats = db.execute(
            text("""
                SELECT 
                    domain,
                    COUNT(*) as content_count,
                    SUM(LENGTH(text)) as total_characters,
                    AVG(LENGTH(text)) as avg_content_length,
                    COUNT(DISTINCT CASE WHEN is_processed = true THEN id END) as processed_count,
                    MAX(extracted_at) as last_updated
                FROM contents 
                WHERE org_id = :org_id
                GROUP BY domain
                ORDER BY content_count DESC
                LIMIT :limit
            """),
            {"org_id": org_id, "limit": limit}
        ).fetchall()
        
        return [
            {
                "domain": row.domain,
                "content_count": row.content_count,
                "total_characters": int(row.total_characters or 0),
                "total_mb": round((row.total_characters or 0) / (1024 * 1024), 2),
                "avg_content_length": int(row.avg_content_length or 0),
                "processed_count": row.processed_count,
                "processing_rate": round(
                    (row.processed_count / row.content_count * 100) if row.content_count > 0 else 0, 1
                ),
                "last_updated": row.last_updated.isoformat() if row.last_updated else None
            }
            for row in domain_stats
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get top domains: {str(e)}"
        )