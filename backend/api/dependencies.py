"""
FastAPI dependency injection functions.
"""
from fastapi import Depends
from crawler.service import CrawlerService
from processor.service import ProcessorService
from processor.rag_service import RAGService
from database.session import get_db_session
from database.db import Database

# Singleton services
_crawler_service = None
_processor_service = None
_rag_service = None

def get_db():
    """Get a database session."""
    db_session = get_db_session()
    db = Database(db_session)
    try:
        yield db
    except Exception as e:
        # Rollback on any exception to ensure clean state
        try:
            db_session.rollback()
        except Exception:
            pass
        raise e
    finally:
        try:
            db_session.close()
        except Exception:
            pass

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

def get_rag_service(
    db = Depends(get_db),
    processor_service = Depends(get_processor_service)
):
    """Get the RAG service singleton."""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService(db, processor_service)
    return _rag_service
