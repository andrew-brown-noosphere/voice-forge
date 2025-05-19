"""
API data models using Pydantic for request and response validation.
"""
from pydantic import BaseModel, Field, HttpUrl, validator
from typing import List, Dict, Optional, Union, Any
from datetime import datetime
from enum import Enum

class CrawlState(str, Enum):
    """Possible states for a crawl job."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ContentType(str, Enum):
    """Types of content that can be extracted."""
    BLOG_POST = "blog_post"
    PRODUCT_DESCRIPTION = "product_description"
    ABOUT_PAGE = "about_page"
    LANDING_PAGE = "landing_page"
    ARTICLE = "article"
    NEWS = "news"
    PRESS_RELEASE = "press_release"
    DOCUMENTATION = "documentation"
    FAQ = "faq"
    OTHER = "other"

class CrawlConfig(BaseModel):
    """Configuration for a crawl job."""
    max_depth: int = Field(3, ge=1, le=10, description="Maximum depth to crawl")
    max_pages: Optional[int] = Field(None, ge=1, description="Maximum number of pages to crawl (unlimited if None)")
    respect_robots_txt: bool = Field(True, description="Whether to respect robots.txt")
    delay: float = Field(1.0, ge=0, description="Delay between requests in seconds")
    timeout: int = Field(30, ge=1, description="Request timeout in seconds")
    follow_external_links: bool = Field(False, description="Whether to follow links to external domains")
    exclude_patterns: List[str] = Field(default_factory=list, description="URL patterns to exclude")
    include_patterns: List[str] = Field(default_factory=list, description="URL patterns to include (others will be excluded)")
    user_agent: str = Field("VoiceForge Crawler (+https://voiceforge.example.com)", description="User agent string")

class CrawlRequest(BaseModel):
    """Request to start a new crawl job."""
    domain: str = Field(..., description="Domain URL to crawl")
    config: CrawlConfig = Field(default_factory=CrawlConfig, description="Crawl configuration")
    
    @validator('domain')
    def validate_domain(cls, v):
        """Validate domain format."""
        if not v.startswith(('http://', 'https://')):
            v = 'https://' + v
        return v

class CrawlProgress(BaseModel):
    """Progress of a crawl job."""
    pages_crawled: int = Field(0, description="Number of pages crawled")
    pages_discovered: int = Field(0, description="Number of pages discovered")
    pages_failed: int = Field(0, description="Number of pages that failed to crawl")
    current_depth: int = Field(0, description="Current crawl depth")
    content_extracted: int = Field(0, description="Number of content pieces extracted")

class CrawlStatus(BaseModel):
    """Status of a crawl job."""
    crawl_id: str = Field(..., description="Unique identifier for the crawl job")
    domain: str = Field(..., description="Domain being crawled")
    state: CrawlState = Field(..., description="Current state of the crawl")
    progress: CrawlProgress = Field(default_factory=CrawlProgress, description="Progress of the crawl")
    start_time: Optional[datetime] = Field(None, description="When the crawl started")
    end_time: Optional[datetime] = Field(None, description="When the crawl ended")
    error: Optional[str] = Field(None, description="Error message if the crawl failed")
    config: CrawlConfig = Field(..., description="Configuration used for the crawl")

class ContentMetadata(BaseModel):
    """Metadata for extracted content."""
    title: Optional[str] = Field(None, description="Title of the content")
    author: Optional[str] = Field(None, description="Author of the content")
    publication_date: Optional[datetime] = Field(None, description="When the content was published")
    last_modified: Optional[datetime] = Field(None, description="When the content was last modified")
    categories: List[str] = Field(default_factory=list, description="Categories of the content")
    tags: List[str] = Field(default_factory=list, description="Tags associated with the content")
    language: Optional[str] = Field(None, description="Language of the content")
    content_type: ContentType = Field(ContentType.OTHER, description="Type of content")

class ContentResponse(BaseModel):
    """Response model for content retrieval."""
    content_id: str = Field(..., description="Unique identifier for the content")
    url: str = Field(..., description="URL where the content was found")
    domain: str = Field(..., description="Domain of the content")
    text: str = Field(..., description="Extracted text content")
    html: Optional[str] = Field(None, description="Original HTML of the content")
    metadata: ContentMetadata = Field(..., description="Metadata for the content")
    relevance_score: Optional[float] = Field(None, description="Relevance score (if this is a search result)")
    crawl_id: str = Field(..., description="ID of the crawl that found this content")
    extracted_at: datetime = Field(..., description="When the content was extracted")

class ContentSearchRequest(BaseModel):
    """Request to search for content."""
    query: str = Field(..., description="Search query")
    domain: Optional[str] = Field(None, description="Filter by domain")
    content_type: Optional[ContentType] = Field(None, description="Filter by content type")
    limit: int = Field(10, ge=1, le=100, description="Maximum number of results")
    offset: int = Field(0, ge=0, description="Offset for pagination")
