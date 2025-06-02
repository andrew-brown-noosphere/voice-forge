"""
Analytics endpoints for VoiceForge including word cloud generation.
"""
import logging
from typing import List, Dict, Optional, Any
from collections import Counter
import re
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from auth.clerk_auth import get_current_user_with_org, AuthUser, get_org_id_from_user
from api.dependencies import get_db
from database.db import Database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["analytics"])

# Word Cloud Models
class WordCloudRequest(BaseModel):
    """Request for generating word cloud data."""
    domain: Optional[str] = Field(None, description="Filter by specific domain")
    content_type: Optional[str] = Field(None, description="Filter by content type")
    crawl_id: Optional[str] = Field(None, description="Filter by specific crawl")
    max_words: int = Field(100, ge=10, le=500, description="Maximum number of words to return")
    min_word_length: int = Field(3, ge=2, le=10, description="Minimum word length")
    exclude_common: bool = Field(True, description="Exclude common stop words")
    time_range_days: Optional[int] = Field(None, ge=1, le=365, description="Only include content from last N days")

class WordCloudWord(BaseModel):
    """A word in the word cloud with its frequency."""
    word: str = Field(..., description="The word")
    frequency: int = Field(..., description="How many times it appears")
    weight: float = Field(..., description="Normalized weight (0-1)")
    category: Optional[str] = Field(None, description="Word category (noun, verb, etc.)")

class WordCloudResponse(BaseModel):
    """Response containing word cloud data."""
    words: List[WordCloudWord] = Field(..., description="List of words with frequencies")
    total_words_processed: int = Field(..., description="Total number of words analyzed")
    unique_words: int = Field(..., description="Number of unique words found")
    content_sources: int = Field(..., description="Number of content pieces analyzed")
    domains_analyzed: List[str] = Field(..., description="List of domains included in analysis")
    generated_at: datetime = Field(..., description="When this word cloud was generated")

class ContentSummary(BaseModel):
    """Summary statistics for crawled content."""
    total_pages: int
    total_content_pieces: int
    total_words: int
    domains: List[str]
    content_types: Dict[str, int]
    crawl_count: int
    last_crawl_date: Optional[datetime]

# Stop words list - common English words to exclude
STOP_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
    'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him',
    'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'am', 'is', 'are',
    'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
    'would', 'should', 'could', 'can', 'may', 'might', 'must', 'shall', 'about', 'above',
    'across', 'after', 'against', 'along', 'among', 'around', 'as', 'before', 'behind',
    'below', 'beneath', 'beside', 'between', 'beyond', 'during', 'except', 'from', 'inside',
    'into', 'near', 'off', 'outside', 'over', 'since', 'through', 'throughout', 'till',
    'toward', 'under', 'until', 'up', 'upon', 'within', 'without', 'all', 'any', 'both',
    'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
    'own', 'same', 'so', 'than', 'too', 'very', 'just', 'now', 'here', 'there', 'when',
    'where', 'why', 'how', 'what', 'which', 'who', 'whom', 'whose', 'if', 'because',
    'while', 'although', 'though', 'unless', 'since', 'whether'
}

def clean_and_tokenize_text(text: str, min_length: int = 3, exclude_common: bool = True) -> List[str]:
    """Clean text and extract meaningful words."""
    if not text:
        return []
    
    # Convert to lowercase and remove special characters
    cleaned_text = re.sub(r'[^a-zA-Z\s]', ' ', text.lower())
    
    # Split into words and filter
    words = []
    for word in cleaned_text.split():
        word = word.strip()
        # Filter by length
        if len(word) < min_length:
            continue
        # Filter stop words if requested
        if exclude_common and word in STOP_WORDS:
            continue
        # Skip very common web words
        if word in {'www', 'com', 'org', 'net', 'html', 'http', 'https', 'page', 'site', 'link'}:
            continue
        words.append(word)
    
    return words

@router.post("/word-cloud", response_model=WordCloudResponse)
async def generate_word_cloud(
    request: WordCloudRequest,
    current_user: AuthUser = Depends(get_current_user_with_org),
    db: Database = Depends(get_db),
):
    """
    Generate word cloud data from crawled content.
    
    This endpoint analyzes all crawled content text to generate
    a word frequency analysis suitable for word cloud visualization.
    """
    try:
        # Get organization ID for multi-tenant isolation
        org_id = get_org_id_from_user(current_user)
        
        logger.info(f"Generating word cloud for org {org_id} with filters: {request.dict()}")
        
        # Build database query to get content
        from database.models import Content, Crawl
        session = db.session
        
        # Start with base query
        query = session.query(Content).filter(Content.org_id == org_id)
        
        # Apply filters
        if request.domain:
            query = query.filter(Content.domain == request.domain)
        
        if request.content_type:
            query = query.filter(Content.content_type == request.content_type)
        
        if request.crawl_id:
            query = query.filter(Content.crawl_id == request.crawl_id)
        
        if request.time_range_days:
            cutoff_date = datetime.now() - timedelta(days=request.time_range_days)
            query = query.filter(Content.extracted_at >= cutoff_date)
        
        # Get content pieces
        content_pieces = query.all()
        
        if not content_pieces:
            logger.warning(f"No content found for word cloud generation with given filters")
            return WordCloudResponse(
                words=[],
                total_words_processed=0,
                unique_words=0,
                content_sources=0,
                domains_analyzed=[],
                generated_at=datetime.now()
            )
        
        logger.info(f"Processing {len(content_pieces)} content pieces for word cloud")
        
        # Extract and count words
        all_words = []
        domains_analyzed = set()
        
        for content in content_pieces:
            domains_analyzed.add(content.domain)
            
            # Combine title and text for analysis
            text_to_analyze = ""
            if content.title:
                text_to_analyze += content.title + " "
            if content.text:
                text_to_analyze += content.text
            
            # Extract words
            words = clean_and_tokenize_text(
                text_to_analyze,
                min_length=request.min_word_length,
                exclude_common=request.exclude_common
            )
            all_words.extend(words)
        
        # Count word frequencies
        word_counts = Counter(all_words)
        
        # Get top words
        top_words = word_counts.most_common(request.max_words)
        
        if not top_words:
            logger.warning("No words found after filtering")
            return WordCloudResponse(
                words=[],
                total_words_processed=len(all_words),
                unique_words=len(word_counts),
                content_sources=len(content_pieces),
                domains_analyzed=list(domains_analyzed),
                generated_at=datetime.now()
            )
        
        # Calculate weights (normalize to 0-1 scale)
        max_frequency = top_words[0][1]  # Highest frequency
        min_frequency = top_words[-1][1] if len(top_words) > 1 else max_frequency
        
        # Create word cloud words
        cloud_words = []
        for word, frequency in top_words:
            # Normalize weight between 0.1 and 1.0
            if max_frequency == min_frequency:
                weight = 1.0
            else:
                weight = 0.1 + (0.9 * (frequency - min_frequency) / (max_frequency - min_frequency))
            
            cloud_words.append(WordCloudWord(
                word=word,
                frequency=frequency,
                weight=weight,
                category=None  # Could be enhanced with NLP tagging
            ))
        
        result = WordCloudResponse(
            words=cloud_words,
            total_words_processed=len(all_words),
            unique_words=len(word_counts),
            content_sources=len(content_pieces),
            domains_analyzed=list(domains_analyzed),
            generated_at=datetime.now()
        )
        
        logger.info(f"Generated word cloud with {len(cloud_words)} words from {len(content_pieces)} content pieces")
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to generate word cloud: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate word cloud: {str(e)}"
        )

@router.get("/content-summary", response_model=ContentSummary)
async def get_content_summary(
    current_user: AuthUser = Depends(get_current_user_with_org),
    db: Database = Depends(get_db),
):
    """Get a summary of all crawled content."""
    try:
        # Get organization ID for multi-tenant isolation
        org_id = get_org_id_from_user(current_user)
        
        from database.models import Content, Crawl
        session = db.session
        
        # Get basic stats
        total_content = session.query(Content).filter(Content.org_id == org_id).count()
        
        # Get domains
        domains = session.query(Content.domain).filter(
            Content.org_id == org_id
        ).distinct().all()
        domain_list = [domain[0] for domain in domains]
        
        # Get content types
        content_types = session.query(Content.content_type).filter(
            Content.org_id == org_id
        ).all()
        content_type_counts = Counter([ct[0] for ct in content_types])
        
        # Get crawl count and last crawl
        crawl_count = session.query(Crawl).filter(Crawl.org_id == org_id).count()
        last_crawl = session.query(Crawl).filter(
            Crawl.org_id == org_id
        ).order_by(Crawl.start_time.desc()).first()
        
        # Calculate total words (rough estimate)
        content_pieces = session.query(Content.text).filter(
            Content.org_id == org_id,
            Content.text.isnot(None)
        ).limit(100).all()  # Sample for word count estimate
        
        total_words = 0
        for content in content_pieces:
            if content[0]:
                total_words += len(content[0].split())
        
        # Extrapolate if we sampled
        if len(content_pieces) == 100 and total_content > 100:
            total_words = int(total_words * (total_content / 100))
        
        return ContentSummary(
            total_pages=total_content,
            total_content_pieces=total_content,
            total_words=total_words,
            domains=domain_list,
            content_types=dict(content_type_counts),
            crawl_count=crawl_count,
            last_crawl_date=last_crawl.start_time if last_crawl else None
        )
        
    except Exception as e:
        logger.error(f"Failed to get content summary: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get content summary: {str(e)}"
        )

@router.get("/top-domains", response_model=List[Dict[str, Any]])
async def get_top_domains(
    limit: int = Query(10, ge=1, le=50),
    current_user: AuthUser = Depends(get_current_user_with_org),
    db: Database = Depends(get_db),
):
    """Get domains with the most content."""
    try:
        # Get organization ID for multi-tenant isolation
        org_id = get_org_id_from_user(current_user)
        
        from database.models import Content
        from sqlalchemy import func
        session = db.session
        
        # Query to get domain counts
        domain_counts = session.query(
            Content.domain,
            func.count(Content.id).label('content_count')
        ).filter(
            Content.org_id == org_id
        ).group_by(
            Content.domain
        ).order_by(
            func.count(Content.id).desc()
        ).limit(limit).all()
        
        result = []
        for domain, count in domain_counts:
            result.append({
                "domain": domain,
                "content_count": count
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to get top domains: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get top domains: {str(e)}"
        )
