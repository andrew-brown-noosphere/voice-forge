"""
Database models for VoiceForge.
"""
import json
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.ext.mutable import MutableDict, MutableList

from database.session import Base

class Crawl(Base):
    """Database model for crawl jobs."""
    __tablename__ = "crawls"
    
    id = Column(String, primary_key=True)
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

class Content(Base):
    """Database model for website content."""
    __tablename__ = "contents"
    
    id = Column(String, primary_key=True)
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
    embedding = Column(MutableList.as_mutable(ARRAY(Float)), nullable=True)
    
    # Relationships
    crawl = relationship("Crawl", back_populates="contents")
