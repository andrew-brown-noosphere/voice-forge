"""
Database models for VoiceForge.
"""
import json
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, Boolean, JSON, ForeignKey, Index
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy.types import TypeDecorator

# Define a Vector type for pgvector
class Vector(TypeDecorator):
    impl = sa.ARRAY(sa.Float)
    cache_ok = True  # Fix SQLAlchemy warning about cache key
    
    def process_bind_param(self, value, dialect):
        return value
    
    def process_result_value(self, value, dialect):
        return value

from database.session import Base


# ============================================================================
# ABSTRACTED SIGNALS SYSTEM
# ============================================================================

class Signal(Base):
    """Abstracted signal model for all platforms (Reddit, Twitter, GitHub, LinkedIn)"""
    __tablename__ = "signals"

    signal_id = Column(String, primary_key=True)
    org_id = Column(String, nullable=False, index=True)
    platform = Column(String, nullable=False, index=True)  # 'reddit', 'twitter', 'github', 'linkedin'
    platform_id = Column(String, nullable=False)  # platform-specific ID
    title = Column(String, nullable=False)
    content = Column(Text)
    url = Column(String, nullable=False)
    author = Column(String)
    author_url = Column(String)
    created_at = Column(DateTime, nullable=False)  # when content was created on platform
    discovered_at = Column(DateTime, nullable=False)  # when we discovered it
    signal_type = Column(String, nullable=False, index=True)  # 'question', 'complaint', 'feature_request', etc.
    relevance_score = Column(Float, nullable=False, index=True)
    engagement_potential = Column(Float, nullable=False)
    sentiment_score = Column(Float)
    status = Column(String, nullable=False, default='active', index=True)  # 'active', 'archived', 'responded'
    platform_metadata = Column(MutableDict.as_mutable(JSONB), default={})  # platform-specific data
    keywords_matched = Column(MutableList.as_mutable(ARRAY(String)), default=[])
    engagement_metrics = Column(MutableDict.as_mutable(JSONB), default={})  # likes, shares, comments, etc.

    # Relationships
    responses = relationship("SignalResponse", back_populates="signal")

    __table_args__ = (
        Index('ix_signals_org_platform', 'org_id', 'platform'),
        Index('ix_signals_org_signal_type', 'org_id', 'signal_type'),
        Index('ix_signals_platform_id', 'platform', 'platform_id'),
        Index('ix_signals_discovered_at', 'discovered_at'),
    )

    def __repr__(self):
        return f"<Signal {self.signal_id}: {self.platform} - {self.title[:50]}>"

    @property
    def reddit_data(self):
        """Helper to get Reddit-specific data from platform_metadata"""
        if self.platform == 'reddit' and self.platform_metadata:
            return self.platform_metadata
        return {}

    @property
    def twitter_data(self):
        """Helper to get Twitter-specific data from platform_metadata"""
        if self.platform == 'twitter' and self.platform_metadata:
            return self.platform_metadata
        return {}

    @property
    def github_data(self):
        """Helper to get GitHub-specific data from platform_metadata"""
        if self.platform == 'github' and self.platform_metadata:
            return self.platform_metadata
        return {}

    @property
    def linkedin_data(self):
        """Helper to get LinkedIn-specific data from platform_metadata"""
        if self.platform == 'linkedin' and self.platform_metadata:
            return self.platform_metadata
        return {}


class SignalSource(Base):
    """Configuration for signal monitoring sources"""
    __tablename__ = "signal_sources"

    source_id = Column(String, primary_key=True)
    org_id = Column(String, nullable=False, index=True)
    platform = Column(String, nullable=False, index=True)  # 'reddit', 'twitter', 'github', 'linkedin'
    source_name = Column(String, nullable=False)  # subreddit name, hashtag, repo, etc.
    source_type = Column(String, nullable=False)  # 'subreddit', 'hashtag', 'repository', 'company_page'
    keywords = Column(MutableList.as_mutable(ARRAY(String)), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    last_crawled_at = Column(DateTime)
    crawl_frequency = Column(String, nullable=False, default='daily')  # 'hourly', 'daily', 'weekly'
    relevance_threshold = Column(Float, nullable=False, default=0.6)
    config = Column(MutableDict.as_mutable(JSONB), default={})  # platform-specific configuration
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    
    # AI Enhancement fields
    ai_suggested_sources = Column(MutableList.as_mutable(ARRAY(String)), default=[])
    ai_suggested_keywords = Column(MutableList.as_mutable(ARRAY(String)), default=[])
    business_context = Column(Text)
    target_goals = Column(MutableList.as_mutable(ARRAY(String)), default=[])
    performance_metrics = Column(MutableDict.as_mutable(JSONB), default={})
    ai_optimization_enabled = Column(Boolean, default=True)
    last_ai_analysis = Column(DateTime)

    __table_args__ = (
        Index('ix_signal_sources_org_platform', 'org_id', 'platform'),
    )

    def __repr__(self):
        return f"<SignalSource {self.source_id}: {self.platform}/{self.source_name}>"


class SignalResponse(Base):
    """Generated responses to signals"""
    __tablename__ = "signal_responses"

    response_id = Column(String, primary_key=True)
    signal_id = Column(String, ForeignKey('signals.signal_id'), nullable=False, index=True)
    org_id = Column(String, nullable=False, index=True)
    generated_content = Column(Text, nullable=False)
    response_type = Column(String, nullable=False)  # 'comment_reply', 'thread_start', 'dm', 'quote_tweet'
    platform = Column(String, nullable=False)
    tone = Column(String, nullable=False)
    confidence_score = Column(Float, nullable=False, index=True)
    response_metadata = Column(MutableDict.as_mutable(JSONB), default={})
    generated_at = Column(DateTime, nullable=False, index=True)
    status = Column(String, nullable=False, default='generated', index=True)  # 'generated', 'published', 'failed'
    published_at = Column(DateTime)
    platform_response_id = Column(String)  # ID from platform after posting
    engagement_metrics = Column(MutableDict.as_mutable(JSONB), default={})

    # Relationships
    signal = relationship("Signal", back_populates="responses")

    __table_args__ = (
        Index('ix_signal_responses_org_id', 'org_id'),
        Index('ix_signal_responses_signal_id', 'signal_id'),
        Index('ix_signal_responses_generated_at', 'generated_at'),
        Index('ix_signal_responses_confidence_score', 'confidence_score'),
    )

    def __repr__(self):
        return f"<SignalResponse {self.response_id}: {self.platform} - {self.tone}>"


class SignalRecommendation(Base):
    """AI-generated recommendations for signal source optimization"""
    __tablename__ = "signal_recommendations"
    
    recommendation_id = Column(String, primary_key=True)
    source_id = Column(String, ForeignKey('signal_sources.source_id'), nullable=False)
    org_id = Column(String, nullable=False, index=True)
    
    recommendation_type = Column(String, nullable=False)  # 'source', 'keyword', 'optimization'
    platform = Column(String, nullable=False)
    recommended_item = Column(String, nullable=False)
    current_performance = Column(MutableDict.as_mutable(JSONB), default={})
    predicted_improvement = Column(MutableDict.as_mutable(JSONB), default={})
    
    confidence_score = Column(Float, nullable=False)
    reasoning = Column(Text, nullable=False)
    supporting_data = Column(MutableDict.as_mutable(JSONB), default={})
    
    status = Column(String, default='pending')  # 'pending', 'accepted', 'rejected', 'applied'
    user_feedback = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    applied_at = Column(DateTime)

    __table_args__ = (
        Index('ix_signal_recommendations_org_id', 'org_id'),
        Index('ix_signal_recommendations_source_id', 'source_id'),
        Index('ix_signal_recommendations_status', 'status'),
    )

    def __repr__(self):
        return f"<SignalRecommendation {self.recommendation_id}: {self.recommendation_type} - {self.recommended_item}>"


class PlatformConfiguration(Base):
    """Configuration and credentials for platform integrations"""
    __tablename__ = "platform_configurations"
    
    config_id = Column(String, primary_key=True)
    org_id = Column(String, nullable=False, index=True)
    platform = Column(String, nullable=False, index=True)  # 'reddit', 'twitter', 'github', 'linkedin'
    
    # Encrypted configuration data
    configuration = Column(MutableDict.as_mutable(JSONB), nullable=False)  # Stores encrypted credentials
    
    # Status and metadata
    is_active = Column(Boolean, nullable=False, default=True)
    last_tested_at = Column(DateTime)
    last_test_status = Column(String)  # 'success', 'failed', 'partial'
    last_test_error = Column(Text)
    
    # Configuration metadata
    configured_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    configured_by = Column(String)  # User ID who configured it
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Rate limiting and quota information
    rate_limit_info = Column(MutableDict.as_mutable(JSONB), default={})
    quota_usage = Column(MutableDict.as_mutable(JSONB), default={})
    
    __table_args__ = (
        # Ensure one config per platform per org
        sa.UniqueConstraint('org_id', 'platform', name='uq_platform_config_org_platform'),
        Index('ix_platform_configurations_org_platform', 'org_id', 'platform'),
        Index('ix_platform_configurations_platform', 'platform'),
    )

    def __repr__(self):
        return f"<PlatformConfiguration {self.config_id}: {self.platform} for org {self.org_id}>"


# ============================================================================
# BACKWARDS COMPATIBILITY MODELS (for migration)
# ============================================================================

class RedditSignal(Base):
    """DEPRECATED: Old Reddit-specific model - kept for migration purposes"""
    __tablename__ = "reddit_signals"
    
    signal_id = Column(String, primary_key=True)
    org_id = Column(String, nullable=False, index=True)
    platform = Column(String, nullable=False, default='reddit')
    thread_id = Column(String, nullable=False, index=True)
    subreddit = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    url = Column(String, nullable=False)
    author = Column(String, nullable=True)
    score = Column(Integer, nullable=False, default=0)
    num_comments = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False)
    relevance_score = Column(Float, nullable=False)
    signal_type = Column(String, nullable=False, index=True)
    engagement_potential = Column(Float, nullable=False)
    top_comments = Column(MutableList.as_mutable(ARRAY(Text)), default=[])
    discovered_at = Column(DateTime, nullable=False)
    status = Column(String, nullable=False, default='active')
    signal_metadata = Column(MutableDict.as_mutable(JSONB), default={})


# ============================================================================
# CONTENT CRAWLING SYSTEM
# ============================================================================

class Crawl(Base):
    """Database model for crawl jobs."""
    __tablename__ = "crawls"
    
    id = Column(String, primary_key=True)
    org_id = Column(String, nullable=False, index=True)  # Multi-tenant organization ID
    domain = Column(String, nullable=False, index=True)
    state = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    error = Column(Text, nullable=True)
    config = Column(JSONB, nullable=False)
    
    # Progress tracking
    pages_crawled = Column(Integer, default=0)
    pages_discovered = Column(Integer, default=0)
    pages_failed = Column(Integer, default=0)
    current_depth = Column(Integer, default=0)
    content_extracted = Column(Integer, default=0)
    
    # Relationships
    contents = relationship("Content", back_populates="crawl")
    
    __table_args__ = (
        # Multi-tenant indexes for better query performance
        Index('ix_crawls_org_id_domain', 'org_id', 'domain'),
        Index('ix_crawls_org_id_state', 'org_id', 'state'),
    )

class Content(Base):
    """Database model for website content."""
    __tablename__ = "contents"
    
    id = Column(String, primary_key=True)
    org_id = Column(String, nullable=False, index=True)  # Multi-tenant organization ID
    url = Column(String, nullable=False, index=True)
    domain = Column(String, nullable=False, index=True)
    crawl_id = Column(String, ForeignKey("crawls.id"), nullable=False)
    extracted_at = Column(DateTime, nullable=False)
    
    # Content data
    text = Column(Text, nullable=False)
    html = Column(Text, nullable=True)
    
    # Metadata
    title = Column(String, nullable=True)
    author = Column(String, nullable=True)
    publication_date = Column(DateTime, nullable=True)
    last_modified = Column(DateTime, nullable=True)
    categories = Column(MutableList.as_mutable(ARRAY(String)), default=[])
    tags = Column(MutableList.as_mutable(ARRAY(String)), default=[])
    language = Column(String, nullable=True)
    content_type = Column(String, nullable=False)
    
    # Processing fields
    is_processed = Column(Boolean, default=False)
    entities = Column(MutableList.as_mutable(JSONB), default=[])
    embedding = Column(Vector, nullable=True)
    
    # Relationships
    crawl = relationship("Crawl", back_populates="contents")
    chunks = relationship("ContentChunk", back_populates="content")
    
    __table_args__ = (
        # Multi-tenant indexes for better query performance
        Index('ix_contents_org_id_domain', 'org_id', 'domain'),
        Index('ix_contents_org_id_content_type', 'org_id', 'content_type'),
        Index('ix_contents_org_id_url', 'org_id', 'url'),
    )

class ContentChunk(Base):
    """Database model for content chunks used in RAG."""
    __tablename__ = "content_chunks"
    
    id = Column(String, primary_key=True)
    org_id = Column(String, nullable=False, index=True)  # Multi-tenant organization ID
    content_id = Column(String, ForeignKey("contents.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    
    # Chunk text and position
    text = Column(Text, nullable=False)
    start_char = Column(Integer, nullable=False)
    end_char = Column(Integer, nullable=False)
    
    # Embedding for retrieval
    embedding = Column(Vector, nullable=True)
    
    # Metadata
    chunk_metadata = Column(JSONB, default={})
    
    # Relationships
    content = relationship("Content", back_populates="chunks")
    
    __table_args__ = (
        # Create an index on content_id and chunk_index
        # This will help with retrieving chunks in order
        Index('ix_content_chunks_content_id_chunk_index', 'content_id', 'chunk_index'),
        # Multi-tenant indexes
        Index('ix_content_chunks_org_id', 'org_id'),
        Index('ix_content_chunks_org_id_content_id', 'org_id', 'content_id'),
    )

class MarketingTemplate(Base):
    """Database model for predefined marketing response templates."""
    __tablename__ = "marketing_templates"
    
    id = Column(String, primary_key=True)
    org_id = Column(String, nullable=False, index=True)  # Multi-tenant organization ID
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Template content with placeholders
    template_text = Column(Text, nullable=False)
    
    # Platform and usage metadata
    platform = Column(String, nullable=False)  # e.g., "twitter", "instagram", "email"
    tone = Column(String, nullable=False)  # e.g., "professional", "casual", "enthusiastic"
    purpose = Column(String, nullable=False)  # e.g., "promotion", "announcement", "response"
    
    # Configuration
    parameters = Column(MutableList.as_mutable(JSONB), default=[])
    
    # Creation and update tracking
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)
    created_by = Column(String, nullable=True)
    
    __table_args__ = (
        # Multi-tenant indexes for better query performance
        Index('ix_marketing_templates_org_id_platform', 'org_id', 'platform'),
        Index('ix_marketing_templates_org_id_tone', 'org_id', 'tone'),
        Index('ix_marketing_templates_org_id_purpose', 'org_id', 'purpose'),
    )


# ============================================================================
# HELPER FUNCTIONS FOR CREATING PLATFORM-SPECIFIC SIGNALS
# ============================================================================

def create_reddit_signal(signal_id: str, org_id: str, thread_id: str, subreddit: str, 
                        title: str, content: str, url: str, author: str, score: int, 
                        num_comments: int, created_at, relevance_score: float,
                        signal_type: str, engagement_potential: float, 
                        top_comments: list = None) -> Signal:
    """Create a Signal instance with Reddit-specific data"""
    reddit_metadata = {
        'thread_id': thread_id,
        'subreddit': subreddit,
        'score': score,
        'num_comments': num_comments,
        'top_comments': top_comments or []
    }
    
    engagement_metrics = {
        'upvotes': score,
        'comments': num_comments,
        'engagement_rate': min(1.0, (score + num_comments) / 100)  # Simple calculation
    }
    
    return Signal(
        signal_id=signal_id,
        org_id=org_id,
        platform='reddit',
        platform_id=thread_id,
        title=title,
        content=content,
        url=url,
        author=author,
        author_url=f"https://reddit.com/u/{author}" if author else None,
        created_at=created_at,
        discovered_at=sa.func.now(),
        signal_type=signal_type,
        relevance_score=relevance_score,
        engagement_potential=engagement_potential,
        platform_metadata=reddit_metadata,
        engagement_metrics=engagement_metrics
    )


def create_twitter_signal(signal_id: str, org_id: str, tweet_id: str, 
                         content: str, url: str, author: str, retweets: int,
                         likes: int, replies: int, created_at, 
                         relevance_score: float, signal_type: str, 
                         engagement_potential: float) -> Signal:
    """Create a Signal instance with Twitter-specific data"""
    twitter_metadata = {
        'tweet_id': tweet_id,
        'retweets': retweets,
        'likes': likes,
        'replies': replies,
        'hashtags': [],  # Would extract from content
        'mentions': []   # Would extract from content
    }
    
    engagement_metrics = {
        'likes': likes,
        'retweets': retweets,
        'replies': replies,
        'engagement_rate': min(1.0, (likes + retweets + replies) / 1000)
    }
    
    return Signal(
        signal_id=signal_id,
        org_id=org_id,
        platform='twitter',
        platform_id=tweet_id,
        title=content[:100] + '...' if len(content) > 100 else content,  # Twitter doesn't have titles
        content=content,
        url=url,
        author=author,
        author_url=f"https://twitter.com/{author}" if author else None,
        created_at=created_at,
        discovered_at=sa.func.now(),
        signal_type=signal_type,
        relevance_score=relevance_score,
        engagement_potential=engagement_potential,
        platform_metadata=twitter_metadata,
        engagement_metrics=engagement_metrics
    )


def create_github_signal(signal_id: str, org_id: str, issue_id: str, repo: str,
                        title: str, content: str, url: str, author: str,
                        created_at, relevance_score: float,
                        signal_type: str, engagement_potential: float,
                        issue_type: str = 'issue') -> Signal:
    """Create a Signal instance with GitHub-specific data"""
    github_metadata = {
        'issue_id': issue_id,
        'repository': repo,
        'issue_type': issue_type,  # 'issue', 'pr', 'discussion'
        'labels': [],  # Would get from GitHub API
        'assignees': [],
        'milestone': None,
        'state': 'open'  # Would get from GitHub API
    }
    
    engagement_metrics = {
        'comments': 0,  # Would get from GitHub API
        'reactions': 0,
        'watchers': 0
    }
    
    return Signal(
        signal_id=signal_id,
        org_id=org_id,
        platform='github',
        platform_id=issue_id,
        title=title,
        content=content,
        url=url,
        author=author,
        author_url=f"https://github.com/{author}" if author else None,
        created_at=created_at,
        discovered_at=sa.func.now(),
        signal_type=signal_type,
        relevance_score=relevance_score,
        engagement_potential=engagement_potential,
        platform_metadata=github_metadata,
        engagement_metrics=engagement_metrics
    )


def create_linkedin_signal(signal_id: str, org_id: str, post_id: str,
                          title: str, content: str, url: str, author: str,
                          created_at, relevance_score: float,
                          signal_type: str, engagement_potential: float) -> Signal:
    """Create a Signal instance with LinkedIn-specific data"""
    linkedin_metadata = {
        'post_id': post_id,
        'post_type': 'post',  # 'post', 'article', 'comment'
        'company_page': False,  # Whether it's from a company page
        'industry': None,
        'seniority': None
    }
    
    engagement_metrics = {
        'likes': 0,  # Would get from LinkedIn API
        'comments': 0,
        'shares': 0,
        'views': 0
    }
    
    return Signal(
        signal_id=signal_id,
        org_id=org_id,
        platform='linkedin',
        platform_id=post_id,
        title=title,
        content=content,
        url=url,
        author=author,
        author_url=f"https://linkedin.com/in/{author}" if author else None,
        created_at=created_at,
        discovered_at=sa.func.now(),
        signal_type=signal_type,
        relevance_score=relevance_score,
        engagement_potential=engagement_potential,
        platform_metadata=linkedin_metadata,
        engagement_metrics=engagement_metrics
    )
