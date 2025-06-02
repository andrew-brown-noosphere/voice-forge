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
    
    # Enhanced user agent configuration for whitelisting
    user_agent_mode: str = Field("default", description="User agent mode: default, custom, stealth")
    custom_user_agent: Optional[str] = Field(None, description="Custom user agent string for whitelisting")
    organization_name: Optional[str] = Field(None, description="Organization name for default user agent")
    contact_email: Optional[str] = Field(None, description="Contact email for default user agent")
    
    # Legacy field for backward compatibility
    user_agent: str = Field("VoiceForge-Crawler/1.0 (+https://voiceforge.ai/bot)", description="User agent string (deprecated, use user_agent_mode)")

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
    task_id: Optional[str] = Field(None, description="Celery task ID for background processing")

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

# New models for RAG features

class ChunkResponse(BaseModel):
    """Response model for content chunk retrieval."""
    id: str = Field(..., description="Unique identifier for the chunk")
    content_id: str = Field(..., description="ID of the parent content")
    chunk_index: int = Field(..., description="Index of this chunk in the content")
    text: str = Field(..., description="Chunk text")
    start_char: int = Field(..., description="Start position in the original content")
    end_char: int = Field(..., description="End position in the original content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Chunk metadata")
    similarity: Optional[float] = Field(None, description="Similarity score (if this is a search result)")

class ChunkSearchRequest(BaseModel):
    """Request to search for content chunks."""
    query: str = Field(..., description="Search query")
    domain: Optional[str] = Field(None, description="Filter by domain")
    content_type: Optional[ContentType] = Field(None, description="Filter by content type")
    top_k: int = Field(5, ge=1, le=50, description="Number of chunks to retrieve")

class ContentTone(str, Enum):
    """Tones for generated content."""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FRIENDLY = "friendly"
    ENTHUSIASTIC = "enthusiastic"
    INFORMATIVE = "informative"
    PERSUASIVE = "persuasive"
    AUTHORITATIVE = "authoritative"

class ContentPlatform(str, Enum):
    """Platforms for content generation."""
    TWITTER = "twitter"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    EMAIL = "email"
    BLOG = "blog"
    WEBSITE = "website"
    CUSTOMER_SUPPORT = "customer_support"

class GenerateContentRequest(BaseModel):
    """Request to generate content using RAG."""
    query: str = Field(..., description="Question or topic for content generation")
    platform: ContentPlatform = Field(..., description="Target platform")
    tone: ContentTone = Field(..., description="Desired tone")
    domain: Optional[str] = Field(None, description="Filter by domain")
    content_type: Optional[ContentType] = Field(None, description="Filter by content type")
    top_k: int = Field(5, ge=1, le=20, description="Number of chunks to retrieve")

class SourceChunk(BaseModel):
    """Source chunk information for generated content."""
    chunk_id: str = Field(..., description="ID of the source chunk")
    text: str = Field(..., description="Snippet of the chunk text")
    similarity: float = Field(..., description="Similarity score")
    content_id: str = Field(..., description="ID of the parent content")

class GeneratedContent(BaseModel):
    """Response model for generated content."""
    text: str = Field(..., description="Generated content text")
    source_chunks: List[SourceChunk] = Field(..., description="Source chunks used for generation")
    template_id: Optional[str] = Field(None, description="ID of the template used")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Generation metadata")

class TemplateParameter(BaseModel):
    """Parameter for a marketing template."""
    name: str = Field(..., description="Parameter name")
    description: str = Field(..., description="Parameter description")
    default_value: Optional[str] = Field(None, description="Default value")

class MarketingTemplateCreate(BaseModel):
    """Request to create a marketing template."""
    name: str = Field(..., description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    template_text: str = Field(..., description="Template text with placeholders")
    platform: ContentPlatform = Field(..., description="Target platform")
    tone: ContentTone = Field(..., description="Tone of the template")
    purpose: str = Field(..., description="Purpose of the template")
    parameters: List[TemplateParameter] = Field(default_factory=list, description="Template parameters")
    created_by: Optional[str] = Field(None, description="User who created the template")

class MarketingTemplateResponse(BaseModel):
    """Response model for marketing template."""
    id: str = Field(..., description="Template ID")
    name: str = Field(..., description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    template_text: str = Field(..., description="Template text with placeholders")
    platform: ContentPlatform = Field(..., description="Target platform")
    tone: ContentTone = Field(..., description="Tone of the template")
    purpose: str = Field(..., description="Purpose of the template")
    parameters: List[TemplateParameter] = Field(default_factory=list, description="Template parameters")
    created_at: datetime = Field(..., description="When the template was created")
    updated_at: Optional[datetime] = Field(None, description="When the template was last updated")
    created_by: Optional[str] = Field(None, description="User who created the template")

class TemplateSearchRequest(BaseModel):
    """Request to search for templates."""
    platform: Optional[ContentPlatform] = Field(None, description="Filter by platform")
    tone: Optional[ContentTone] = Field(None, description="Filter by tone")
    purpose: Optional[str] = Field(None, description="Filter by purpose")
    limit: int = Field(10, ge=1, le=100, description="Maximum number of results")
    offset: int = Field(0, ge=0, description="Offset for pagination")
