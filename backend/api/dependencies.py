"""
FastAPI dependency injection functions.
"""
from fastapi import Depends
from crawler.service import CrawlerService
from processor.service import ProcessorService
from database.session import get_db_session
from database.db import Database

# Singleton services
_crawler_service = None
_processor_service = None

def get_db():
    """Get a database session."""
    db_session = get_db_session()
    db = Database(db_session)
    try:
        yield db
    finally:
        db_session.close()

def get_crawler_service(db = Depends(get_db)):
    """Get the crawler service singleton."""
    global _crawler_service
    if _crawler_service is None:
        _crawler_service = CrawlerService(db)
    return _crawler_service

def get_processor_service(db = Depends(get_db)):
    """Get the processor service singleton."""
    global _processor_service
    if _processor_service is None:
        _processor_service = ProcessorService(db)
    return _processor_service
