"""
FastAPI dependency injection functions.
"""
from fastapi import Depends
from crawler.service import CrawlerService
from processor.service import ProcessorService
from processor.rag_service import RAGService
from services.enhanced_rag_service import create_hybrid_rag_service
from database.session import get_db_session
from database.db import Database

import logging

logger = logging.getLogger(__name__)

def get_db():
    """Get a database session with proper transaction management."""
    db_session = get_db_session()
    db = Database(db_session)
    try:
        yield db
    except Exception as e:
        logger.error(f"Database error occurred: {str(e)}")
        # Always rollback on any exception to ensure clean state
        try:
            db_session.rollback()
            logger.info("Transaction rolled back successfully")
        except Exception as rollback_error:
            logger.error(f"Failed to rollback transaction: {str(rollback_error)}")
        # Re-raise the original exception
        raise e
    finally:
        # Always close the session
        try:
            db_session.close()
        except Exception as close_error:
            logger.error(f"Failed to close database session: {str(close_error)}")

def get_crawler_service(db = Depends(get_db)):
    """Get a new crawler service instance (not singleton)."""
    return CrawlerService(db)

def get_processor_service(db = Depends(get_db)):
    """Get a new processor service instance (not singleton)."""
    return ProcessorService(db)

def get_rag_service(
    db = Depends(get_db),
    processor_service = Depends(get_processor_service)
):
    """Get a new RAG service instance (not singleton)."""
    return RAGService(db, processor_service)

def get_enhanced_rag_service(
    db = Depends(get_db)
):
    """Get a new enhanced hybrid RAG service instance."""
    # TODO: Pass vector service when available
    return create_hybrid_rag_service(db, vector_service=None)
