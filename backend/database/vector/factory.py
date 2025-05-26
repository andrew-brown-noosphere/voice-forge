"""
Vector database factory for VoiceForge.
"""
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class VectorDBFactory:
    """
    Factory for creating vector database clients.
    Supports multiple vector database providers.
    """
    
    @staticmethod
    def get_client():
        """
        Get a vector database client based on environment configuration.
        
        Returns:
            A vector database client instance
        """
        provider = os.environ.get('VECTOR_DB_PROVIDER', 'pinecone').lower()
        
        if provider == 'pinecone':
            try:
                from database.vector.pinecone_client import PineconeClient
                return PineconeClient()
            except ImportError:
                logger.error("Pinecone client not available. Make sure pinecone-client is installed.")
                logger.info("Falling back to PostgreSQL pgvector extension")
                return None
            except Exception as e:
                logger.error(f"Failed to initialize Pinecone client: {e}")
                logger.info("Falling back to PostgreSQL pgvector extension")
                return None
        elif provider == 'pgvector':
            # For now, we'll use the database directly for pgvector
            # In a future version, we could create a dedicated client
            logger.info("Using PostgreSQL pgvector extension for vector database")
            return None
        else:
            logger.warning(f"Unknown vector database provider: {provider}")
            logger.info("Falling back to PostgreSQL pgvector extension")
            return None

# Create a singleton instance
_vector_db_client = None

def get_vector_db_client():
    """
    Get the vector database client singleton.
    
    Returns:
        Vector database client instance
    """
    global _vector_db_client
    
    if _vector_db_client is None:
        try:
            _vector_db_client = VectorDBFactory.get_client()
        except Exception as e:
            logger.error(f"Failed to get vector database client: {e}")
            _vector_db_client = None
    
    return _vector_db_client
