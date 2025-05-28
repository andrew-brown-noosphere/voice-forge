"""
Content processor service implementation.
"""
import logging
from typing import List, Optional, Dict, Any
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer

from api.models import ContentType, ContentResponse

logger = logging.getLogger(__name__)

class ProcessorService:
    """Service for processing and analyzing website content."""
    
    def __init__(self, db):
        """Initialize the processor service."""
        self.db = db
        
        # Initialize NLP models
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            # Download if not available
            spacy.cli.download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
        
        # Initialize vectorizer
        self.tfidf = TfidfVectorizer(
            max_features=10000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        # Initialize embeddings model
        self.embedding_model = None  # Lazy-loaded
    
    def get_embedding_model(self):
        """Lazy-load the embedding model."""
        if self.embedding_model is None:
            try:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                logger.error(f"Failed to load embedding model: {str(e)}")
                raise
        
        return self.embedding_model
    
    def process_content(self, content_id: str, org_id: str):
        """Process content to extract entities, vectors, etc."""
        try:
            # Get content from database
            content = self.db.get_content(content_id, org_id)
            if not content:
                logger.warning(f"Content {content_id} not found")
                return
            
            # Process text with spaCy
            doc = self.nlp(content["text"])
            
            # Extract entities
            entities = []
            for ent in doc.ents:
                entities.append({
                    "text": ent.text,
                    "label": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char
                })
            
            # Generate vector embedding
            model = self.get_embedding_model()
            embedding = model.encode(content["text"]).tolist()
            
            # Update content with processed data
            self.db.update_content_processing(
                content_id=content_id,
                entities=entities,
                embedding=embedding
            )
            
            logger.info(f"Processed content {content_id}: {len(entities)} entities, {len(embedding)} embedding dims")
            
        except Exception as e:
            logger.error(f"Failed to process content {content_id}: {str(e)}")
    
    def get_content(self, content_id: str, org_id: str) -> Optional[ContentResponse]:
        """Get content by ID."""
        content = self.db.get_content(content_id, org_id)
        if not content:
            return None
        
        return ContentResponse(**content)
    
    def search_content(
        self,
        query: str,
        domain: Optional[str] = None,
        content_type: Optional[ContentType] = None,
        limit: int = 10,
        offset: int = 0,
        org_id: str = None
    ) -> List[ContentResponse]:
        """
        Search for content based on query text and filters.
        
        Args:
            query: The search query
            domain: Filter by domain
            content_type: Filter by content type
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of ContentResponse objects
        """
        try:
            # Get embedding for query
            model = self.get_embedding_model()
            query_embedding = model.encode(query).tolist()
            
            # Search database with vector similarity
            results = self.db.search_content_by_vector(
                query_embedding=query_embedding,
                domain=domain,
                content_type=content_type,
                limit=limit,
                offset=offset,
                org_id=org_id
            )
            
            # Convert to response models
            responses = [ContentResponse(**result) for result in results]
            
            return responses
            
        except Exception as e:
            logger.error(f"Failed to search content: {str(e)}")
            return []
    
    def calculate_relevance(self, query: str, content_text: str) -> float:
        """
        Calculate relevance score between query and content.
        
        Args:
            query: The query text
            content_text: The content text
            
        Returns:
            Relevance score between 0 and 1
        """
        try:
            # Use embeddings to calculate similarity
            model = self.get_embedding_model()
            query_embedding = model.encode(query)
            content_embedding = model.encode(content_text)
            
            # Calculate cosine similarity
            from sklearn.metrics.pairwise import cosine_similarity
            similarity = cosine_similarity(
                [query_embedding],
                [content_embedding]
            )[0][0]
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Failed to calculate relevance: {str(e)}")
            return 0.0
