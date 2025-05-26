#!/usr/bin/env python3
"""
Vector Database Optimization Script
Optimizes PostgreSQL with pgvector for production-ready vector search
"""

import os
import sys
import time
import logging
from typing import List, Dict, Any

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.session import get_db_session
from database.models import ContentChunk, Content
from processor.rag import RAGSystem
from sqlalchemy import text, func
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorDBOptimizer:
    """Optimizes vector database performance and structure"""
    
    def __init__(self):
        self.session = get_db_session()
        
    def check_pgvector_extension(self) -> bool:
        """Check if pgvector extension is installed"""
        try:
            result = self.session.execute(
                text("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
            ).fetchone()
            return bool(result)
        except Exception as e:
            logger.error(f"Error checking pgvector: {e}")
            return False
    
    def install_pgvector_extension(self) -> bool:
        """Install pgvector extension if not present"""
        try:
            if not self.check_pgvector_extension():
                logger.info("Installing pgvector extension...")
                self.session.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                self.session.commit()
                logger.info("✅ pgvector extension installed")
                return True
            else:
                logger.info("✅ pgvector extension already installed")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to install pgvector: {e}")
            return False
    
    def check_embedding_column(self) -> Dict[str, Any]:
        """Check if embedding column exists and its properties"""
        try:
            # Check if embedding column exists
            result = self.session.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'content_chunks' AND column_name = 'embedding'
            """)).fetchone()
            
            if not result:
                return {'exists': False}
            
            # Get embedding statistics
            stats = self.session.execute(text("""
                SELECT 
                    COUNT(*) as total_chunks,
                    COUNT(embedding) as chunks_with_embeddings,
                    CASE 
                        WHEN COUNT(*) > 0 THEN ROUND((COUNT(embedding)::float / COUNT(*)) * 100, 2)
                        ELSE 0 
                    END as coverage_percentage
                FROM content_chunks
            """)).fetchone()
            
            return {
                'exists': True,
                'data_type': result[1],
                'is_nullable': result[2],
                'total_chunks': stats[0],
                'chunks_with_embeddings': stats[1],
                'coverage_percentage': stats[2]
            }
            
        except Exception as e:
            logger.error(f"Error checking embedding column: {e}")
            return {'exists': False, 'error': str(e)}
    
    def add_embedding_column(self) -> bool:
        """Add embedding column if it doesn't exist"""
        try:
            column_info = self.check_embedding_column()
            
            if not column_info['exists']:
                logger.info("Adding embedding column to content_chunks table...")
                self.session.execute(text("""
                    ALTER TABLE content_chunks 
                    ADD COLUMN embedding vector(1536)
                """))
                self.session.commit()
                logger.info("✅ Embedding column added")
                return True
            else:
                logger.info("✅ Embedding column already exists")
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to add embedding column: {e}")
            return False
    
    def create_vector_indexes(self) -> bool:
        """Create optimized vector indexes for fast similarity search"""
        try:
            # Check existing indexes
            existing_indexes = self.session.execute(text("""
                SELECT indexname 
                FROM pg_indexes 
                WHERE tablename = 'content_chunks' 
                AND indexname LIKE '%embedding%'
            """)).fetchall()
            
            if existing_indexes:
                logger.info(f"✅ Vector indexes already exist: {[idx[0] for idx in existing_indexes]}")
                return True
            
            # Create HNSW index for vector similarity search
            logger.info("Creating HNSW vector index...")
            self.session.execute(text("""
                CREATE INDEX CONCURRENTLY IF NOT EXISTS content_chunks_embedding_hnsw_idx 
                ON content_chunks 
                USING hnsw (embedding vector_cosine_ops)
                WITH (m = 16, ef_construction = 64)
            """))
            
            # Create IVFFlat index as backup
            logger.info("Creating IVFFlat vector index...")
            self.session.execute(text("""
                CREATE INDEX CONCURRENTLY IF NOT EXISTS content_chunks_embedding_ivfflat_idx 
                ON content_chunks 
                USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100)
            """))
            
            self.session.commit()
            logger.info("✅ Vector indexes created")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create vector indexes: {e}")
            return False
    
    def analyze_vector_performance(self) -> Dict[str, Any]:
        """Analyze current vector search performance"""
        try:
            # Get table statistics
            stats = self.session.execute(text("""
                SELECT 
                    COUNT(*) as total_chunks,
                    COUNT(embedding) as chunks_with_embeddings,
                    AVG(LENGTH(content)) as avg_content_length,
                    MIN(LENGTH(content)) as min_content_length,
                    MAX(LENGTH(content)) as max_content_length
                FROM content_chunks
            """)).fetchone()
            
            # Check index usage
            index_stats = self.session.execute(text("""
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    idx_scan,
                    idx_tup_read,
                    idx_tup_fetch
                FROM pg_stat_user_indexes 
                WHERE tablename = 'content_chunks'
                AND indexname LIKE '%embedding%'
            """)).fetchall()
            
            return {
                'total_chunks': stats[0],
                'chunks_with_embeddings': stats[1],
                'avg_content_length': float(stats[2]) if stats[2] else 0,
                'min_content_length': stats[3],
                'max_content_length': stats[4],
                'vector_indexes': [
                    {
                        'name': idx[2],
                        'scans': idx[3],
                        'tuples_read': idx[4],
                        'tuples_fetched': idx[5]
                    } for idx in index_stats
                ]
            }
            
        except Exception as e:
            logger.error(f"Error analyzing vector performance: {e}")
            return {}
    
    def test_vector_search_performance(self) -> Dict[str, Any]:
        """Test vector search performance with timing"""
        try:
            # Generate a test embedding
            rag_system = RAGSystem()
            embedding_model = rag_system.get_embedding_model()
            test_embedding = embedding_model.encode("test query for performance")
            
            # Convert to list for SQL
            embedding_list = test_embedding.tolist()
            
            # Test cosine similarity search
            start_time = time.time()
            
            results = self.session.execute(text("""
                SELECT id, content, (embedding <=> :test_embedding) as distance
                FROM content_chunks 
                WHERE embedding IS NOT NULL
                ORDER BY embedding <=> :test_embedding
                LIMIT 5
            """), {'test_embedding': embedding_list}).fetchall()
            
            search_time = time.time() - start_time
            
            return {
                'search_time_ms': round(search_time * 1000, 2),
                'results_found': len(results),
                'test_successful': True
            }
            
        except Exception as e:
            logger.error(f"Error testing vector search: {e}")
            return {
                'test_successful': False,
                'error': str(e)
            }
    
    def optimize_database_settings(self) -> bool:
        """Optimize PostgreSQL settings for vector operations"""
        try:
            # Get current settings
            current_settings = {}
            for setting in ['shared_buffers', 'work_mem', 'maintenance_work_mem', 'effective_cache_size']:
                result = self.session.execute(text(f"SHOW {setting}")).fetchone()
                current_settings[setting] = result[0]
            
            logger.info("Current PostgreSQL settings:")
            for key, value in current_settings.items():
                logger.info(f"  {key}: {value}")
            
            # Note: These require database restart and superuser privileges
            recommendations = {
                'shared_buffers': '256MB',  # For vector caching
                'work_mem': '64MB',         # For vector operations
                'maintenance_work_mem': '512MB',  # For index creation
                'effective_cache_size': '1GB'    # Adjust based on available RAM
            }
            
            logger.info("\n📋 Recommended settings for better vector performance:")
            logger.info("   Add these to postgresql.conf and restart PostgreSQL:")
            for key, value in recommendations.items():
                logger.info(f"   {key} = {value}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking database settings: {e}")
            return False
    
    def generate_missing_embeddings(self, batch_size: int = 50) -> bool:
        """Generate embeddings for content chunks that don't have them"""
        try:
            # Get chunks without embeddings
            chunks_without_embeddings = self.session.query(ContentChunk).filter(
                ContentChunk.embedding.is_(None)
            ).limit(batch_size).all()
            
            if not chunks_without_embeddings:
                logger.info("✅ All chunks already have embeddings")
                return True
            
            logger.info(f"Generating embeddings for {len(chunks_without_embeddings)} chunks...")
            
            # Initialize RAG system for embedding generation
            rag_system = RAGSystem()
            embedding_model = rag_system.get_embedding_model()
            
            for i, chunk in enumerate(chunks_without_embeddings):
                try:
                    # Generate embedding
                    embedding = embedding_model.encode(chunk.content)
                    
                    # Store embedding
                    chunk.embedding = embedding.tolist()
                    
                    if (i + 1) % 10 == 0:
                        logger.info(f"  Processed {i + 1}/{len(chunks_without_embeddings)} chunks")
                        
                except Exception as e:
                    logger.error(f"Error generating embedding for chunk {chunk.id}: {e}")
                    continue
            
            # Commit changes
            self.session.commit()
            logger.info(f"✅ Generated embeddings for {len(chunks_without_embeddings)} chunks")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to generate embeddings: {e}")
            return False
    
    def run_full_optimization(self) -> None:
        """Run complete vector database optimization"""
        logger.info("🚀 Starting Vector Database Optimization")
        logger.info("=" * 50)
        
        # Step 1: Check and install pgvector
        logger.info("\n1️⃣ Checking pgvector extension...")
        if not self.install_pgvector_extension():
            logger.error("❌ Cannot proceed without pgvector extension")
            return
        
        # Step 2: Check and add embedding column
        logger.info("\n2️⃣ Checking embedding column...")
        if not self.add_embedding_column():
            logger.error("❌ Cannot proceed without embedding column")
            return
        
        # Step 3: Generate missing embeddings
        logger.info("\n3️⃣ Generating missing embeddings...")
        self.generate_missing_embeddings()
        
        # Step 4: Create vector indexes
        logger.info("\n4️⃣ Creating vector indexes...")
        self.create_vector_indexes()
        
        # Step 5: Analyze performance
        logger.info("\n5️⃣ Analyzing vector performance...")
        performance_stats = self.analyze_vector_performance()
        if performance_stats:
            logger.info(f"   Total chunks: {performance_stats['total_chunks']}")
            logger.info(f"   Chunks with embeddings: {performance_stats['chunks_with_embeddings']}")
            logger.info(f"   Average content length: {performance_stats['avg_content_length']:.0f} chars")
            logger.info(f"   Vector indexes: {len(performance_stats['vector_indexes'])}")
        
        # Step 6: Test vector search
        logger.info("\n6️⃣ Testing vector search performance...")
        search_stats = self.test_vector_search_performance()
        if search_stats['test_successful']:
            logger.info(f"   Search time: {search_stats['search_time_ms']}ms")
            logger.info(f"   Results found: {search_stats['results_found']}")
        else:
            logger.error(f"   Search test failed: {search_stats.get('error', 'Unknown error')}")
        
        # Step 7: Database optimization recommendations
        logger.info("\n7️⃣ Database optimization recommendations...")
        self.optimize_database_settings()
        
        logger.info("\n🎉 Vector Database Optimization Complete!")
        logger.info("\n📋 Next Steps:")
        logger.info("   1. Test your RAG system: python scripts/test_full_rag_pipeline.py")
        logger.info("   2. Process more content: python scripts/process_content_for_rag.py")
        logger.info("   3. Monitor performance with: python scripts/diagnose_vector_db.py")
    
    def __del__(self):
        """Clean up database session"""
        if hasattr(self, 'session'):
            self.session.close()

def main():
    """Main optimization function"""
    try:
        optimizer = VectorDBOptimizer()
        optimizer.run_full_optimization()
    except Exception as e:
        logger.error(f"Optimization failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
