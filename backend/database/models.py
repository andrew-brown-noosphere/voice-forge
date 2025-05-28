"""
Database models for VoiceForge.
"""
import json
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
