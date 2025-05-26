"""
Pinecone integration for the RAG system.
"""
import logging
import uuid
from typing import List, Dict, Any, Optional
import numpy as np

from database.vector.factory import get_vector_db_client

logger = logging.getLogger(__name__)

class PineconeRAGStore:
    """
    Pinecone vector store implementation for the RAG system.
    Handles storage and retrieval of content chunks using Pinecone.
    """
    
    def __init__(self, db=None):
        """
        Initialize the Pinecone RAG store.
        
        Args:
            db: Optional database interface for hybrid search
        """
        self.vector_client = get_vector_db_client()
        self.db = db
    
    def store_chunks(self, chunks: List[Dict[str, Any]]) -> bool:
        """
        Store chunks in the vector database.
        
        Args:
            chunks: List of chunk dictionaries with text, embedding, etc.
            
        Returns:
            bool: Success status
        """
        if not chunks:
            logger.warning("No chunks provided to store")
            return False
        
        if not self.vector_client:
            # If Pinecone client not available, use the database
            if self.db:
                return self.db.store_content_chunks(chunks)
            else:
                logger.error("No vector store available")
                return False
        
        try:
            # Convert chunks to Pinecone format
            vectors = []
            
            for chunk in chunks:
                # Skip chunks without embeddings
                if 'embedding' not in chunk:
                    logger.warning(f"Chunk missing embedding, skipping: {chunk.get('id', 'unknown')}")
                    continue
                
                # Create metadata (excluding the embedding field)
                metadata = {}
                
                # Add content_id and chunk_index
                metadata['content_id'] = chunk.get('content_id')
                metadata['chunk_index'] = chunk.get('chunk_index')
                
                # Add text for retrieval
                metadata['text'] = chunk.get('text', '')
                
                # Add position information
                metadata['start_char'] = chunk.get('start_char', 0)
                metadata['end_char'] = chunk.get('end_char', 0)
                
                # Add other metadata
                if 'chunk_metadata' in chunk:
                    for key, value in chunk['chunk_metadata'].items():
                        # Skip complex objects Pinecone can't handle
                        if isinstance(value, (str, int, float, bool)):
                            metadata[key] = value
                
                # Add to vectors batch
                vectors.append({
                    'id': chunk.get('id', str(uuid.uuid4())),
                    'values': chunk['embedding'],
                    'metadata': metadata
                })
            
            # Store vectors in Pinecone
            if vectors:
                success = self.vector_client.store_vectors(vectors)
                if success:
                    logger.info(f"Successfully stored {len(vectors)} chunks in Pinecone")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error storing chunks in Pinecone: {str(e)}")
            return False
    
    def search_chunks(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar chunks using a query embedding.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            filters: Optional filters to apply
            
        Returns:
            List of chunk dictionaries with similarity scores
        """
        if not self.vector_client:
            # If Pinecone client not available, use the database
            if self.db:
                # Convert filters to kwargs
                kwargs = {}
                if filters:
                    if 'domain' in filters:
                        kwargs['domain'] = filters['domain']
                    if 'content_type' in filters:
                        kwargs['content_type'] = filters['content_type']
                return self.db.search_chunks_by_vector(query_embedding, top_k, **kwargs)
            else:
                logger.error("No vector store available")
                return []
        
        try:
            # Convert filters to Pinecone format
            pinecone_filter = None
            if filters:
                pinecone_filter = {}
                if 'domain' in filters and filters['domain']:
                    pinecone_filter['domain'] = {'$eq': filters['domain']}
                if 'content_type' in filters and filters['content_type']:
                    pinecone_filter['content_type'] = {'$eq': filters['content_type']}
            
            # Search Pinecone
            results = self.vector_client.search_vectors(
                query_vector=query_embedding,
                top_k=top_k,
                filter=pinecone_filter,
                include_metadata=True
            )
            
            # Convert results to chunk format
            chunks = []
            for result in results:
                metadata = result.get('metadata', {})
                
                chunk = {
                    'id': result['id'],
                    'content_id': metadata.get('content_id'),
                    'chunk_index': metadata.get('chunk_index'),
                    'text': metadata.get('text', ''),
                    'start_char': metadata.get('start_char', 0),
                    'end_char': metadata.get('end_char', 0),
                    'similarity': result['score'],
                    'metadata': {}
                }
                
                # Add remaining metadata
                for key, value in metadata.items():
                    if key not in ['content_id', 'chunk_index', 'text', 'start_char', 'end_char']:
                        chunk['metadata'][key] = value
                
                chunks.append(chunk)
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error searching chunks in Pinecone: {str(e)}")
            return []
    
    def calculate_similarity(self, query_embedding: List[float], chunk_embedding: List[float]) -> float:
        """
        Calculate similarity between query and chunk embeddings.
        
        Args:
            query_embedding: Query embedding vector
            chunk_embedding: Chunk embedding vector
            
        Returns:
            Similarity score (cosine similarity)
        """
        try:
            similarity = cosine_similarity(
                [np.array(query_embedding)],
                [np.array(chunk_embedding)]
            )[0][0]
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0
