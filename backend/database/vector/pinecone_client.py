"""
Pinecone vector database client for VoiceForge.
"""
import os
import logging
from typing import List, Dict, Any, Optional, Union
import time
import json
import numpy as np

logger = logging.getLogger(__name__)

class PineconeClient:
    """
    Client for the Pinecone vector database.
    Handles index creation, vector storage, and similarity search.
    """
    
    def __init__(self):
        """Initialize the Pinecone client."""
        try:
            self.api_key = os.environ.get('PINECONE_API_KEY')
            self.environment = os.environ.get('PINECONE_ENVIRONMENT', 'gcp-starter')
            self.index_name = os.environ.get('PINECONE_INDEX_NAME', 'voiceforge-rag')
            self.namespace = os.environ.get('PINECONE_NAMESPACE', 'content')
            self.dimension = int(os.environ.get('VECTOR_DIMENSION', '768'))
            
            if not self.api_key:
                raise ValueError("PINECONE_API_KEY environment variable not set")
            
            # Try to import and initialize Pinecone client
            try:
                from pinecone import Pinecone, ServerlessSpec
                # Initialize Pinecone client
                self.pc = Pinecone(api_key=self.api_key)
                
                # Ensure index exists
                self._ensure_index_exists()
                
                # Get the index
                self.index = self.pc.Index(self.index_name)
                
                logger.info(f"Pinecone client initialized with index '{self.index_name}'")
            except ImportError:
                logger.error("Pinecone client not available. Make sure pinecone-client is installed.")
                raise
            
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone client: {str(e)}")
            raise
    
    def _ensure_index_exists(self):
        """Create index if it doesn't exist."""
        try:
            from pinecone import ServerlessSpec
            
            # List existing indexes
            existing_indexes = [index.name for index in self.pc.list_indexes()]
            
            if self.index_name not in existing_indexes:
                logger.info(f"Creating new Pinecone index '{self.index_name}'")
                
                # Configure serverless spec based on environment
                if self.environment == 'gcp-starter':
                    spec = ServerlessSpec(
                        cloud='gcp',
                        region='us-central1'  # GCP starter is in us-central1
                    )
                else:
                    # For other environments, you might need to specify the region
                    cloud = 'aws'  # Default to AWS if not specified
                    region = 'us-west-2'  # Default region
                    
                    # Extract cloud and region from environment if possible
                    if '-' in self.environment:
                        parts = self.environment.split('-')
                        region = '-'.join(parts[:-1])
                        cloud = parts[-1]
                    
                    spec = ServerlessSpec(
                        cloud=cloud,
                        region=region
                    )
                
                # Create the index with metric='cosine' for text embeddings
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric='cosine',
                    spec=spec
                )
                
                # Wait for index to be ready
                logger.info(f"Waiting for index '{self.index_name}' to be ready...")
                time.sleep(10)  # Give it some time to initialize
                
                logger.info(f"Successfully created Pinecone index '{self.index_name}'")
            else:
                logger.info(f"Pinecone index '{self.index_name}' already exists")
        
        except Exception as e:
            logger.error(f"Failed to ensure index exists: {str(e)}")
            raise
    
    def store_vectors(
        self, 
        vectors: List[Dict[str, Any]], 
        namespace: Optional[str] = None
    ) -> bool:
        """
        Store vectors in Pinecone.
        
        Args:
            vectors: List of vectors to store. Each vector must have 'id', 'values', and 'metadata'.
            namespace: Optional namespace to store vectors in.
            
        Returns:
            bool: Success status
        """
        if not vectors:
            logger.warning("No vectors provided to store")
            return False
        
        try:
            # Use provided namespace or default
            ns = namespace or self.namespace
            
            # Pinecone has a limit on batch size, so we need to split into batches
            batch_size = 100
            
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i+batch_size]
                
                # Upsert vectors
                self.index.upsert(
                    vectors=batch,
                    namespace=ns
                )
            
            logger.info(f"Successfully stored {len(vectors)} vectors in namespace '{ns}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store vectors in Pinecone: {str(e)}")
            return False
    
    def search_vectors(
        self,
        query_vector: List[float],
        top_k: int = 5,
        namespace: Optional[str] = None,
        filter: Optional[Dict[str, Any]] = None,
        include_metadata: bool = True,
        include_values: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors in Pinecone.
        
        Args:
            query_vector: Query vector
            top_k: Number of results to return
            namespace: Optional namespace to search in
            filter: Optional metadata filter
            include_metadata: Whether to include metadata in results
            include_values: Whether to include vector values in results
            
        Returns:
            List of similar vectors with similarity scores
        """
        try:
            # Use provided namespace or default
            ns = namespace or self.namespace
            
            # Query the index
            results = self.index.query(
                vector=query_vector,
                top_k=top_k,
                namespace=ns,
                include_metadata=include_metadata,
                include_values=include_values,
                filter=filter
            )
            
            # Process and format results
            matches = []
            for match in results.get('matches', []):
                # Extract match data
                item = {
                    'id': match['id'],
                    'score': match['score']  # Score is the cosine similarity
                }
                
                # Include metadata if available
                if include_metadata and 'metadata' in match:
                    item['metadata'] = match['metadata']
                
                # Include vector values if requested
                if include_values and 'values' in match:
                    item['values'] = match['values']
                
                matches.append(item)
            
            logger.info(f"Found {len(matches)} similar vectors in namespace '{ns}'")
            return matches
            
        except Exception as e:
            logger.error(f"Error searching vectors in Pinecone: {str(e)}")
            return []
    
    def delete_vectors(
        self,
        ids: Optional[List[str]] = None,
        filter: Optional[Dict[str, Any]] = None,
        namespace: Optional[str] = None,
        delete_all: bool = False
    ) -> bool:
        """
        Delete vectors from Pinecone.
        
        Args:
            ids: List of vector IDs to delete
            filter: Metadata filter to select vectors to delete
            namespace: Optional namespace to delete from
            delete_all: Whether to delete all vectors in the namespace
            
        Returns:
            bool: Success status
        """
        try:
            # Use provided namespace or default
            ns = namespace or self.namespace
            
            if delete_all:
                # Delete all vectors in namespace
                self.index.delete(delete_all=True, namespace=ns)
                logger.info(f"Deleted all vectors in namespace '{ns}'")
            elif ids:
                # Delete by IDs
                self.index.delete(ids=ids, namespace=ns)
                logger.info(f"Deleted {len(ids)} vectors by ID in namespace '{ns}'")
            elif filter:
                # Delete by filter
                self.index.delete(filter=filter, namespace=ns)
                logger.info(f"Deleted vectors matching filter in namespace '{ns}'")
            else:
                logger.warning("No deletion criteria provided")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting vectors from Pinecone: {str(e)}")
            return False
    
    def get_stats(self, namespace: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics about the index.
        
        Args:
            namespace: Optional namespace to get stats for
            
        Returns:
            Dict with index statistics
        """
        try:
            # Get index stats
            stats = self.index.describe_index_stats()
            
            # If namespace is specified, filter stats
            if namespace and 'namespaces' in stats and namespace in stats['namespaces']:
                return {
                    'namespace': namespace,
                    'vector_count': stats['namespaces'][namespace]['vector_count'],
                    'total_vector_count': stats['total_vector_count']
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting Pinecone stats: {str(e)}")
            return {}
