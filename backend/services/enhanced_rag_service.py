# Simplified RAG Service Patch
# This replaces the complex enhanced_rag_service with a working version
# that bypasses the crawls table complexity causing empty context retrieval.

from services.simplified_rag_service import create_simplified_rag_service

def create_hybrid_rag_service(db, vector_service=None, **kwargs):
    """
    Drop-in replacement that returns simplified RAG service.
    This bypasses the crawls table complexity.
    """
    from database.session import get_db_session
    
    # Use the db session from the Database object
    if hasattr(db, 'session'):
        db_session = db.session
    else:
        # Fallback to getting a new session
        db_session = get_db_session()
    
    return create_simplified_rag_service(db_session)

# Keep the existing imports for compatibility
class KeywordSearchStrategy:
    """Compatibility wrapper - not used in simplified version."""
    def __init__(self, *args, **kwargs):
        pass

class VectorSearchStrategy:
    """Compatibility wrapper - not used in simplified version."""
    def __init__(self, *args, **kwargs):
        pass

# Keep other compatibility classes if needed by other parts of the system
class SemanticSearchStrategy:
    """Compatibility wrapper - not used in simplified version."""
    def __init__(self, *args, **kwargs):
        pass

class DomainFilteredSearchStrategy:
    """Compatibility wrapper - not used in simplified version."""
    def __init__(self, *args, **kwargs):
        pass

class CrossEncoderReranker:
    """Compatibility wrapper - not used in simplified version."""
    def __init__(self, *args, **kwargs):
        pass

class HybridRAGService:
    """Compatibility wrapper - not used in simplified version."""
    def __init__(self, *args, **kwargs):
        pass

class KeywordExtractor:
    """Compatibility wrapper - not used in simplified version."""
    @staticmethod
    def extract_keywords(*args, **kwargs):
        return []
