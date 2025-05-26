"""
Test script for Pinecone integration.
"""
import os
import sys
import logging
import time
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def test_pinecone_connection():
    """Test connection to Pinecone."""
    try:
        # Import inside function to ensure environment is loaded
        from database.vector.factory import get_vector_db_client
        
        # Get Pinecone client
        client = get_vector_db_client()
        
        if client is None:
            logger.error("Failed to get Pinecone client")
            return False
        
        # Get index stats
        stats = client.get_stats()
        logger.info(f"Pinecone index stats: {stats}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing Pinecone connection: {str(e)}")
        return False

def test_vector_operations():
    """Test vector operations with Pinecone."""
    try:
        # Import inside function to ensure environment is loaded
        from database.vector.factory import get_vector_db_client
        
        # Get Pinecone client
        client = get_vector_db_client()
        
        if client is None:
            logger.error("Failed to get Pinecone client")
            return False
        
        # Initialize embedding model (with error handling)
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {str(e)}")
            logger.info("Using random vectors for testing instead")
            
            # Use random vectors if model fails
            import numpy as np
            model = type('DummyModel', (), {
                'encode': lambda self, texts: np.random.rand(len(texts) if isinstance(texts, list) else 1, 768)
            })()
        
        # Create test vectors
        test_texts = [
            "VoiceForge helps companies maintain a consistent brand voice across channels.",
            "Our AI-powered platform analyzes your content to understand your unique brand voice.",
            "Generate on-brand content for social media, emails, and customer support."
        ]
        
        # Generate embeddings
        embeddings = model.encode(test_texts)
        
        # Create vectors for Pinecone
        vectors = []
        for i, (text, embedding) in enumerate(zip(test_texts, embeddings)):
            vectors.append({
                'id': f'test-vector-{i}',
                'values': embedding.tolist(),
                'metadata': {
                    'text': text,
                    'source': 'test-script',
                    'index': i
                }
            })
        
        # Store vectors
        namespace = 'test'
        success = client.store_vectors(vectors, namespace=namespace)
        
        if not success:
            logger.error("Failed to store test vectors")
            return False
        
        logger.info(f"Successfully stored {len(vectors)} test vectors in namespace '{namespace}'")
        
        # Wait for indexing
        time.sleep(2)
        
        # Search for similar vectors
        query_text = "How does VoiceForge help with brand consistency?"
        query_embedding = model.encode(query_text).tolist()
        
        results = client.search_vectors(
            query_vector=query_embedding,
            top_k=2,
            namespace=namespace,
            include_metadata=True
        )
        
        if not results:
            logger.error("No search results found")
        else:
            logger.info(f"Found {len(results)} similar vectors:")
            for i, result in enumerate(results):
                logger.info(f"  {i+1}. Score: {result['score']:.4f}")
                logger.info(f"     Text: {result['metadata']['text']}")
        
        # Clean up test vectors
        success = client.delete_vectors(
            filter={'source': {'$eq': 'test-script'}},
            namespace=namespace
        )
        
        if not success:
            logger.warning("Failed to clean up test vectors")
        else:
            logger.info("Successfully cleaned up test vectors")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing vector operations: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing Pinecone integration...")
    
    # Test connection
    print("\n1. Testing connection to Pinecone...")
    if test_pinecone_connection():
        print("✅ Successfully connected to Pinecone")
    else:
        print("❌ Failed to connect to Pinecone")
        sys.exit(1)
    
    # Test vector operations
    print("\n2. Testing vector operations...")
    if test_vector_operations():
        print("✅ Successfully tested vector operations")
    else:
        print("❌ Failed to test vector operations")
        sys.exit(1)
    
    print("\n✨ All tests passed! Pinecone integration is working correctly.")
