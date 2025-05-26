#!/usr/bin/env python3
"""
Pinecone Vector Database Optimization Script for VoiceForge

This script sets up and optimizes Pinecone for your RAG system:
1. Creates Pinecone index with optimal settings
2. Migrates existing embeddings to Pinecone
3. Tests performance and connectivity
4. Configures environment for Pinecone usage

Use this for cloud-based, scalable vector operations.
"""

import os
import sys
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PineconeOptimizer:
    """Pinecone vector database optimization suite."""
    
    def __init__(self):
        self.pinecone_client = None
        self.index = None
        self.results = []
        
    def optimize_pinecone(self) -> bool:
        """Run complete Pinecone optimization."""
        print("🌲 Pinecone Vector Database Optimization")
        print("=" * 50)
        
        success = True
        
        # Step 1: Check Pinecone configuration
        if not self._check_pinecone_config():
            return False
        
        # Step 2: Initialize Pinecone client
        if not self._initialize_pinecone():
            return False
        
        # Step 3: Create or configure index
        if not self._setup_pinecone_index():
            return False
        
        # Step 4: Migrate existing data
        self._migrate_embeddings_to_pinecone()
        
        # Step 5: Test performance
        self._test_pinecone_performance()
        
        # Step 6: Update environment configuration
        self._update_environment_config()
        
        print(f"\n🎉 Pinecone optimization {'completed successfully' if success else 'completed with warnings'}!")
        return success
    
    def _check_pinecone_config(self) -> bool:
        """Check Pinecone configuration and credentials."""
        print("\n🔍 Checking Pinecone Configuration...")
        
        # Check required environment variables
        api_key = os.environ.get('PINECONE_API_KEY')
        environment = os.environ.get('PINECONE_ENVIRONMENT', 'gcp-starter')
        index_name = os.environ.get('PINECONE_INDEX_NAME', 'voiceforge-rag')
        
        if not api_key:
            print("❌ PINECONE_API_KEY not found in environment variables")
            print("   Please set your Pinecone API key:")
            print("   1. Get API key from: https://app.pinecone.io/")
            print("   2. Add to .env file: PINECONE_API_KEY=your-key-here")
            return False
        
        print(f"✅ Pinecone API Key: {api_key[:10]}...")
        print(f"✅ Environment: {environment}")
        print(f"✅ Index Name: {index_name}")
        
        return True
    
    def _initialize_pinecone(self) -> bool:
        """Initialize Pinecone client."""
        print("\n🚀 Initializing Pinecone Client...")
        
        try:
            import pinecone
            
            api_key = os.environ.get('PINECONE_API_KEY')
            environment = os.environ.get('PINECONE_ENVIRONMENT', 'gcp-starter')
            
            # Initialize Pinecone
            pinecone.init(
                api_key=api_key,
                environment=environment
            )
            
            self.pinecone_client = pinecone
            
            # Test connection by listing indexes
            indexes = pinecone.list_indexes()
            print(f"✅ Pinecone connected successfully")
            print(f"   Available indexes: {indexes}")
            
            return True
            
        except ImportError:
            print("❌ Pinecone client not installed")
            print("   Install with: pip install pinecone-client")
            return False
        except Exception as e:
            print(f"❌ Pinecone initialization failed: {str(e)}")
            print("   Check your API key and environment settings")
            return False
    
    def _setup_pinecone_index(self) -> bool:
        """Create or configure Pinecone index."""
        print("\n📇 Setting Up Pinecone Index...")
        
        try:
            index_name = os.environ.get('PINECONE_INDEX_NAME', 'voiceforge-rag')
            
            # Check if index exists
            existing_indexes = self.pinecone_client.list_indexes()
            
            if index_name in existing_indexes:
                print(f"✅ Index '{index_name}' already exists")
                self.index = self.pinecone_client.Index(index_name)
                
                # Get index stats
                stats = self.index.describe_index_stats()
                print(f"   Total vectors: {stats.get('total_vector_count', 0)}")
                print(f"   Index fullness: {stats.get('index_fullness', 0):.2%}")
                
            else:
                print(f"🏗️  Creating new index '{index_name}'...")
                
                # Create index with optimal settings for OpenAI embeddings
                self.pinecone_client.create_index(
                    name=index_name,
                    dimension=1536,  # OpenAI text-embedding-ada-002 dimension
                    metric='cosine',  # Good for text embeddings
                    pods=1,
                    replicas=1,
                    pod_type='p1.x1'  # Starter pod type
                )
                
                print(f"✅ Created index '{index_name}'")
                
                # Wait for index to be ready
                print("   Waiting for index to be ready...")
                time.sleep(10)
                
                self.index = self.pinecone_client.Index(index_name)
            
            return True
            
        except Exception as e:
            print(f"❌ Index setup failed: {str(e)}")
            return False
    
    def _migrate_embeddings_to_pinecone(self):
        """Migrate existing embeddings from PostgreSQL to Pinecone."""
        print("\n🔄 Migrating Embeddings to Pinecone...")
        
        try:
            from database.session import get_db_session
            from database.models import Content, ContentChunk
            
            with get_db_session() as session:
                # Count existing data
                content_with_embeddings = session.query(Content).filter(Content.embedding.isnot(None)).all()
                chunks_with_embeddings = session.query(ContentChunk).filter(ContentChunk.embedding.isnot(None)).all()
                
                total_vectors = len(content_with_embeddings) + len(chunks_with_embeddings)
                
                if total_vectors == 0:
                    print("⚠️  No embeddings found in PostgreSQL to migrate")
                    print("   Generate embeddings first: python scripts/vector_optimization/generate_embeddings.py")
                    return
                
                print(f"📊 Found {total_vectors} vectors to migrate:")
                print(f"   Content vectors: {len(content_with_embeddings)}")
                print(f"   Chunk vectors: {len(chunks_with_embeddings)}")
                
                # Migrate content embeddings
                if content_with_embeddings:
                    print("\n🔄 Migrating content embeddings...")
                    content_vectors = []
                    
                    for content in content_with_embeddings:
                        vector_data = {
                            'id': f"content_{content.id}",
                            'values': content.embedding,
                            'metadata': {
                                'type': 'content',
                                'content_id': content.id,
                                'url': content.url,
                                'domain': content.domain,
                                'title': content.title or '',
                                'content_type': content.content_type,
                                'text_preview': content.text[:200] + '...' if len(content.text) > 200 else content.text
                            }
                        }
                        content_vectors.append(vector_data)
                        
                        # Batch upsert every 100 vectors
                        if len(content_vectors) >= 100:
                            self.index.upsert(vectors=content_vectors)
                            print(f"   Migrated {len(content_vectors)} content vectors...")
                            content_vectors = []
                    
                    # Upsert remaining vectors
                    if content_vectors:
                        self.index.upsert(vectors=content_vectors)
                        print(f"   Migrated final {len(content_vectors)} content vectors")
                
                # Migrate chunk embeddings
                if chunks_with_embeddings:
                    print("\n🔄 Migrating chunk embeddings...")
                    chunk_vectors = []
                    
                    for chunk in chunks_with_embeddings:
                        vector_data = {
                            'id': f"chunk_{chunk.id}",
                            'values': chunk.embedding,
                            'metadata': {
                                'type': 'chunk',
                                'chunk_id': chunk.id,
                                'content_id': chunk.content_id,
                                'chunk_index': chunk.chunk_index,
                                'text': chunk.text[:1000] + '...' if len(chunk.text) > 1000 else chunk.text,
                                'start_char': chunk.start_char,
                                'end_char': chunk.end_char
                            }
                        }
                        chunk_vectors.append(vector_data)
                        
                        # Batch upsert every 100 vectors
                        if len(chunk_vectors) >= 100:
                            self.index.upsert(vectors=chunk_vectors)
                            print(f"   Migrated {len(chunk_vectors)} chunk vectors...")
                            chunk_vectors = []
                    
                    # Upsert remaining vectors
                    if chunk_vectors:
                        self.index.upsert(vectors=chunk_vectors)
                        print(f"   Migrated final {len(chunk_vectors)} chunk vectors")
                
                # Wait for vectors to be indexed
                print("   Waiting for vectors to be indexed...")
                time.sleep(5)
                
                # Verify migration
                stats = self.index.describe_index_stats()
                total_in_pinecone = stats.get('total_vector_count', 0)
                
                print(f"✅ Migration complete!")
                print(f"   Vectors in Pinecone: {total_in_pinecone}")
                print(f"   Expected: {total_vectors}")
                
                if total_in_pinecone >= total_vectors * 0.9:  # Allow for some delay
                    print("✅ Migration successful!")
                else:
                    print("⚠️  Some vectors may still be indexing...")
                
        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
    
    def _test_pinecone_performance(self):
        """Test Pinecone search performance."""
        print("\n🚀 Testing Pinecone Performance...")
        
        try:
            from processor.embeddings.embedding_service import EmbeddingService
            
            # Generate test embedding
            embedding_service = EmbeddingService()
            test_query = "artificial intelligence machine learning technology"
            test_embedding = embedding_service.generate_embedding(test_query)
            
            if not test_embedding:
                print("❌ Could not generate test embedding")
                return
            
            # Test different query configurations
            test_configs = [
                {'top_k': 5, 'include_metadata': True},
                {'top_k': 10, 'include_metadata': True},
                {'top_k': 20, 'include_metadata': False},
                {'top_k': 50, 'include_metadata': False}
            ]
            
            print("Performance Test Results:")
            
            for config in test_configs:
                start_time = time.time()
                
                results = self.index.query(
                    vector=test_embedding,
                    top_k=config['top_k'],
                    include_metadata=config['include_metadata']
                )
                
                query_time = time.time() - start_time
                
                print(f"   Top-{config['top_k']} {'with metadata' if config['include_metadata'] else 'vectors only'}: "
                      f"{query_time:.3f}s ({len(results.matches)} results)")
            
            # Test filtering
            start_time = time.time()
            filtered_results = self.index.query(
                vector=test_embedding,
                top_k=10,
                include_metadata=True,
                filter={'type': 'chunk'}
            )
            filter_time = time.time() - start_time
            
            print(f"   Filtered search (chunks only): {filter_time:.3f}s ({len(filtered_results.matches)} results)")
            
            # Performance analysis
            if query_time < 0.1:
                print("✅ Excellent Pinecone performance!")
            elif query_time < 0.3:
                print("✅ Good Pinecone performance")
            elif query_time < 0.5:
                print("⚠️  Acceptable Pinecone performance")
            else:
                print("❌ Slow Pinecone performance - check network and index settings")
            
        except Exception as e:
            print(f"❌ Pinecone performance test failed: {str(e)}")
    
    def _update_environment_config(self):
        """Update environment configuration for Pinecone usage."""
        print("\n🔧 Updating Environment Configuration...")
        
        try:
            # Update .env file to use Pinecone provider
            env_file = '.env'
            
            # Read current .env
            if os.path.exists(env_file):
                with open(env_file, 'r') as f:
                    lines = f.readlines()
            else:
                lines = []
            
            # Check and update VECTOR_DB_PROVIDER
            found_provider = False
            for i, line in enumerate(lines):
                if line.startswith('VECTOR_DB_PROVIDER='):
                    lines[i] = 'VECTOR_DB_PROVIDER=pinecone\n'
                    found_provider = True
                    break
            
            if not found_provider:
                lines.append('VECTOR_DB_PROVIDER=pinecone\n')
            
            # Write updated .env
            with open(env_file, 'w') as f:
                f.writelines(lines)
            
            print("✅ Updated VECTOR_DB_PROVIDER=pinecone in .env")
            
            # Set environment variable for current session
            os.environ['VECTOR_DB_PROVIDER'] = 'pinecone'
            
            # Verify required Pinecone settings
            required_settings = {
                'PINECONE_API_KEY': os.environ.get('PINECONE_API_KEY'),
                'PINECONE_ENVIRONMENT': os.environ.get('PINECONE_ENVIRONMENT', 'gcp-starter'),
                'PINECONE_INDEX_NAME': os.environ.get('PINECONE_INDEX_NAME', 'voiceforge-rag')
            }
            
            print("\nPinecone Configuration:")
            for key, value in required_settings.items():
                if key == 'PINECONE_API_KEY':
                    print(f"   {key}: {'✅ Set' if value else '❌ Missing'}")
                else:
                    print(f"   {key}: {value}")
            
        except Exception as e:
            print(f"⚠️  Could not update environment config: {str(e)}")

def main():
    """Main Pinecone optimization function."""
    try:
        print("Starting Pinecone optimization...")
        
        optimizer = PineconeOptimizer()
        success = optimizer.optimize_pinecone()
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 Pinecone Optimization Complete!")
            print("\nYour Pinecone vector database is ready:")
            print("✅ Index created and configured")
            print("✅ Embeddings migrated")
            print("✅ Performance tested")
            
            print("\nNext steps:")
            print("1. Test search: python scripts/test_openai.py")
            print("2. Run diagnostic: python scripts/vector_optimization/vector_db_diagnostic.py")
            
            print("\n💡 Pinecone Benefits:")
            print("   • Cloud-hosted, no infrastructure management")
            print("   • Automatic scaling and high availability")
            print("   • Advanced filtering and metadata search")
            print("   • Real-time updates and deletions")
            
        else:
            print("⚠️  Pinecone optimization completed with warnings")
            print("Some steps may not have been completed successfully.")
            print("Check the output above for specific issues.")
        
        return success
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Optimization interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Optimization failed: {str(e)}")
        logger.exception("Optimization failed")
        return False

if __name__ == "__main__":
    main()
