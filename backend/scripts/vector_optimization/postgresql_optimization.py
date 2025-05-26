#!/usr/bin/env python3
"""
PostgreSQL + pgvector Optimization Script for VoiceForge

This script optimizes your PostgreSQL database for vector operations:
1. Installs pgvector extension
2. Creates optimized indexes
3. Configures database settings
4. Tests performance improvements

Use this for local development or production PostgreSQL deployments.
"""

import os
import sys
import logging
import subprocess
from typing import Dict, List, Any, Optional
from datetime import datetime

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

class PostgreSQLVectorOptimizer:
    """PostgreSQL + pgvector optimization suite."""
    
    def __init__(self):
        self.results = []
        
    def optimize_database(self) -> bool:
        """Run complete PostgreSQL optimization for vector operations."""
        print("🐘 PostgreSQL + pgvector Optimization")
        print("=" * 50)
        
        success = True
        
        # Step 1: Check PostgreSQL connection
        if not self._check_postgres_connection():
            return False
        
        # Step 2: Install pgvector extension
        if not self._install_pgvector():
            print("⚠️  Continuing without pgvector - will use Python fallbacks")
        
        # Step 3: Create/update database schema
        if not self._update_database_schema():
            success = False
        
        # Step 4: Create optimized indexes
        if not self._create_vector_indexes():
            print("⚠️  Some indexes may not be optimal")
        
        # Step 5: Configure PostgreSQL settings
        self._optimize_postgres_settings()
        
        # Step 6: Test performance
        self._test_vector_performance()
        
        # Step 7: Update environment configuration
        self._update_environment_config()
        
        print(f"\n🎉 PostgreSQL optimization {'completed successfully' if success else 'completed with warnings'}!")
        return success
    
    def _check_postgres_connection(self) -> bool:
        """Check PostgreSQL database connection."""
        print("\n🔍 Checking PostgreSQL Connection...")
        
        try:
            from database.session import get_db_session
            
            with get_db_session() as session:
                result = session.execute("SELECT version()").fetchone()
                version = result[0] if result else "Unknown"
                print(f"✅ PostgreSQL Connected: {version[:50]}...")
                
                # Check database name and size
                db_name = session.execute("SELECT current_database()").fetchone()[0]
                size_result = session.execute("SELECT pg_size_pretty(pg_database_size(current_database()))").fetchone()
                db_size = size_result[0] if size_result else "Unknown"
                
                print(f"   Database: {db_name} ({db_size})")
                return True
                
        except Exception as e:
            print(f"❌ PostgreSQL connection failed: {str(e)}")
            print("   Please ensure PostgreSQL is running and DATABASE_URL is correct")
            return False
    
    def _install_pgvector(self) -> bool:
        """Install pgvector extension."""
        print("\n📦 Installing pgvector Extension...")
        
        try:
            from database.session import get_db_session
            
            with get_db_session() as session:
                # Check if already installed
                result = session.execute("SELECT 1 FROM pg_extension WHERE extname = 'vector'").fetchone()
                
                if result:
                    print("✅ pgvector extension already installed")
                    return True
                
                # Try to install pgvector
                try:
                    session.execute("CREATE EXTENSION IF NOT EXISTS vector")
                    session.commit()
                    print("✅ pgvector extension installed successfully")
                    return True
                except Exception as e:
                    print(f"❌ Failed to install pgvector extension: {str(e)}")
                    print("   This might be because:")
                    print("   1. pgvector is not installed on the system")
                    print("   2. Insufficient privileges")
                    print("   3. Extension files are not available")
                    print()
                    print("   To install pgvector manually:")
                    print("   macOS: brew install pgvector")
                    print("   Ubuntu: apt install postgresql-15-pgvector")
                    print("   Or compile from source: https://github.com/pgvector/pgvector")
                    return False
                    
        except Exception as e:
            print(f"❌ Error checking pgvector: {str(e)}")
            return False
    
    def _update_database_schema(self) -> bool:
        """Update database schema for optimal vector storage."""
        print("\n🏗️  Updating Database Schema...")
        
        try:
            from database.session import get_db_session
            
            with get_db_session() as session:
                # Check if vector columns exist and are properly typed
                schema_updates = []
                
                # Check content table embedding column
                content_column = session.execute("""
                    SELECT data_type, udt_name
                    FROM information_schema.columns 
                    WHERE table_name = 'contents' AND column_name = 'embedding'
                """).fetchone()
                
                if content_column:
                    if content_column[1] != 'vector':  # udt_name for vector type
                        schema_updates.append("ALTER TABLE contents ALTER COLUMN embedding TYPE vector(768)")
                
                # Check content_chunks table embedding column
                chunk_column = session.execute("""
                    SELECT data_type, udt_name
                    FROM information_schema.columns 
                    WHERE table_name = 'content_chunks' AND column_name = 'embedding'
                """).fetchone()
                
                if chunk_column:
                    if chunk_column[1] != 'vector':  # udt_name for vector type
                        schema_updates.append("ALTER TABLE content_chunks ALTER COLUMN embedding TYPE vector(768)")
                
                # Apply schema updates
                for update in schema_updates:
                    try:
                        session.execute(update)
                        print(f"✅ Applied: {update}")
                    except Exception as e:
                        print(f"⚠️  Could not apply {update}: {str(e)}")
                
                if schema_updates:
                    session.commit()
                    print(f"✅ Applied {len(schema_updates)} schema updates")
                else:
                    print("✅ Database schema is up to date")
                
                return True
                
        except Exception as e:
            print(f"❌ Schema update failed: {str(e)}")
            return False
    
    def _create_vector_indexes(self) -> bool:
        """Create optimized indexes for vector operations."""
        print("\n📇 Creating Vector Indexes...")
        
        try:
            from database.session import get_db_session
            
            with get_db_session() as session:
                # Check if pgvector is available for advanced indexes
                has_pgvector = session.execute("SELECT 1 FROM pg_extension WHERE extname = 'vector'").fetchone()
                
                indexes_created = 0
                
                if has_pgvector:
                    # Create vector similarity indexes
                    vector_indexes = [
                        {
                            'name': 'ix_contents_embedding_cosine',
                            'table': 'contents',
                            'sql': 'CREATE INDEX IF NOT EXISTS ix_contents_embedding_cosine ON contents USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)'
                        },
                        {
                            'name': 'ix_content_chunks_embedding_cosine',
                            'table': 'content_chunks', 
                            'sql': 'CREATE INDEX IF NOT EXISTS ix_content_chunks_embedding_cosine ON content_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)'
                        },
                        {
                            'name': 'ix_contents_embedding_l2',
                            'table': 'contents',
                            'sql': 'CREATE INDEX IF NOT EXISTS ix_contents_embedding_l2 ON contents USING ivfflat (embedding vector_l2_ops) WITH (lists = 100)'
                        },
                        {
                            'name': 'ix_content_chunks_embedding_l2',
                            'table': 'content_chunks',
                            'sql': 'CREATE INDEX IF NOT EXISTS ix_content_chunks_embedding_l2 ON content_chunks USING ivfflat (embedding vector_l2_ops) WITH (lists = 100)'
                        }
                    ]
                    
                    for index in vector_indexes:
                        try:
                            session.execute(index['sql'])
                            print(f"✅ Created index: {index['name']}")
                            indexes_created += 1
                        except Exception as e:
                            print(f"⚠️  Could not create {index['name']}: {str(e)}")
                
                # Create standard indexes for filtering
                standard_indexes = [
                    'CREATE INDEX IF NOT EXISTS ix_contents_domain_type ON contents (domain, content_type)',
                    'CREATE INDEX IF NOT EXISTS ix_contents_is_processed ON contents (is_processed)',
                    'CREATE INDEX IF NOT EXISTS ix_content_chunks_content_metadata ON content_chunks USING gin (chunk_metadata)',
                    'CREATE INDEX IF NOT EXISTS ix_contents_extracted_at ON contents (extracted_at DESC)',
                    'CREATE INDEX IF NOT EXISTS ix_content_chunks_text_search ON content_chunks USING gin (to_tsvector(\\'english\\', text))'
                ]
                
                for index_sql in standard_indexes:
                    try:
                        session.execute(index_sql)
                        indexes_created += 1
                    except Exception as e:
                        print(f"⚠️  Index creation warning: {str(e)}")
                
                session.commit()
                print(f"✅ Created {indexes_created} database indexes")
                return True
                
        except Exception as e:
            print(f"❌ Index creation failed: {str(e)}")
            return False
    
    def _optimize_postgres_settings(self):
        """Optimize PostgreSQL settings for vector operations."""
        print("\n⚙️  Optimizing PostgreSQL Settings...")
        
        try:
            from database.session import get_db_session
            
            with get_db_session() as session:
                # Get current settings
                settings_to_check = [
                    'shared_buffers',
                    'effective_cache_size', 
                    'work_mem',
                    'maintenance_work_mem',
                    'random_page_cost'
                ]
                
                current_settings = {}
                for setting in settings_to_check:
                    try:
                        result = session.execute(f"SHOW {setting}").fetchone()
                        current_settings[setting] = result[0] if result else 'unknown'
                    except:
                        current_settings[setting] = 'unknown'
                
                print("Current PostgreSQL Configuration:")
                for setting, value in current_settings.items():
                    print(f"   {setting}: {value}")
                
                # Recommendations for vector workloads
                print("\n💡 Recommendations for postgresql.conf:")
                print("   # For vector workloads, consider:")
                print("   shared_buffers = 256MB          # Or 25% of RAM")
                print("   effective_cache_size = 1GB      # Or 75% of RAM") 
                print("   work_mem = 64MB                 # For large sorts")
                print("   maintenance_work_mem = 256MB    # For index builds")
                print("   random_page_cost = 1.1          # For SSD storage")
                print("   max_parallel_workers_per_gather = 4")
                print()
                print("   Note: Restart PostgreSQL after making changes")
                
        except Exception as e:
            print(f"❌ Settings optimization check failed: {str(e)}")
    
    def _test_vector_performance(self):
        """Test vector search performance after optimization."""
        print("\n🚀 Testing Vector Performance...")
        
        try:
            from database.session import get_db_session
            from database.db import Database
            from processor.embeddings.embedding_service import EmbeddingService
            import time
            
            # Initialize services
            embedding_service = EmbeddingService()
            
            # Test with a sample query
            test_query = "artificial intelligence machine learning technology innovation"
            test_embedding = embedding_service.generate_embedding(test_query)
            
            if not test_embedding:
                print("❌ Could not generate test embedding")
                return
            
            with get_db_session() as session:
                db = Database(session)
                
                # Test chunk search performance
                start_time = time.time()
                chunk_results = db.search_chunks_by_vector(
                    query_embedding=test_embedding,
                    top_k=10
                )
                chunk_time = time.time() - start_time
                
                print(f"Vector Search Performance:")
                print(f"   Chunk search: {chunk_time:.3f}s ({len(chunk_results)} results)")
                
                # Test with different k values
                for k in [5, 20, 50]:
                    start_time = time.time()
                    results = db.search_chunks_by_vector(
                        query_embedding=test_embedding,
                        top_k=k
                    )
                    search_time = time.time() - start_time
                    print(f"   Top-{k} search: {search_time:.3f}s")
                
                # Performance analysis
                if chunk_time < 0.1:
                    print("✅ Excellent performance!")
                elif chunk_time < 0.5:
                    print("✅ Good performance")
                elif chunk_time < 1.0:
                    print("⚠️  Acceptable performance - consider more optimization")
                else:
                    print("❌ Slow performance - check indexes and data size")
                
        except Exception as e:
            print(f"❌ Performance test failed: {str(e)}")
    
    def _update_environment_config(self):
        """Update environment configuration for optimal settings."""
        print("\n🔧 Updating Environment Configuration...")
        
        try:
            # Update .env file to use database provider
            env_file = '.env'
            env_updates = {}
            
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
                    lines[i] = 'VECTOR_DB_PROVIDER=database\\n'
                    found_provider = True
                    break
            
            if not found_provider:
                lines.append('VECTOR_DB_PROVIDER=database\\n')
            
            # Write updated .env
            with open(env_file, 'w') as f:
                f.writelines(lines)
            
            print("✅ Updated VECTOR_DB_PROVIDER=database in .env")
            
            # Set environment variable for current session
            os.environ['VECTOR_DB_PROVIDER'] = 'database'
            
        except Exception as e:
            print(f"⚠️  Could not update environment config: {str(e)}")

def create_optimization_scripts():
    """Create additional optimization helper scripts."""
    print("📝 Creating Additional Optimization Scripts...")
    
    # Create embedding optimization script
    embedding_script = '''#!/usr/bin/env python3
"""
Generate embeddings for existing content and chunks.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from database.session import get_db_session
from database.models import Content, ContentChunk
from processor.embeddings.embedding_service import EmbeddingService
import time

def generate_missing_embeddings():
    """Generate embeddings for content and chunks that don't have them."""
    embedding_service = EmbeddingService()
    
    with get_db_session() as session:
        # Process content without embeddings
        content_without_embeddings = session.query(Content).filter(Content.embedding.is_(None)).all()
        
        print(f"Processing {len(content_without_embeddings)} content items...")
        for i, content in enumerate(content_without_embeddings):
            try:
                embedding = embedding_service.generate_embedding(content.text[:8000])  # Limit text length
                if embedding:
                    content.embedding = embedding
                    content.is_processed = True
                    
                if i % 10 == 0:
                    session.commit()
                    print(f"  Processed {i+1}/{len(content_without_embeddings)}")
                    
            except Exception as e:
                print(f"  Error processing content {content.id}: {str(e)}")
        
        session.commit()
        
        # Process chunks without embeddings
        chunks_without_embeddings = session.query(ContentChunk).filter(ContentChunk.embedding.is_(None)).all()
        
        print(f"Processing {len(chunks_without_embeddings)} chunks...")
        for i, chunk in enumerate(chunks_without_embeddings):
            try:
                embedding = embedding_service.generate_embedding(chunk.text)
                if embedding:
                    chunk.embedding = embedding
                    
                if i % 10 == 0:
                    session.commit()
                    print(f"  Processed {i+1}/{len(chunks_without_embeddings)}")
                    
            except Exception as e:
                print(f"  Error processing chunk {chunk.id}: {str(e)}")
        
        session.commit()
        print("✅ Embedding generation complete!")

if __name__ == "__main__":
    generate_missing_embeddings()
'''
    
    with open('scripts/vector_optimization/generate_embeddings.py', 'w') as f:
        f.write(embedding_script)
    
    print("✅ Created generate_embeddings.py")

def main():
    """Main optimization function."""
    try:
        print("Starting PostgreSQL + pgvector optimization...")
        
        optimizer = PostgreSQLVectorOptimizer()
        success = optimizer.optimize_database()
        
        # Create additional helper scripts
        create_optimization_scripts()
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 PostgreSQL Optimization Complete!")
            print("\nYour database is now optimized for vector operations:")
            print("✅ pgvector extension installed (if possible)")
            print("✅ Vector indexes created")
            print("✅ Database schema updated")
            print("✅ Performance tested")
            
            print("\nNext steps:")
            print("1. Generate embeddings: python scripts/vector_optimization/generate_embeddings.py")
            print("2. Test your system: python scripts/test_openai.py")
            print("3. Run diagnostic again: python scripts/vector_optimization/vector_db_diagnostic.py")
            
        else:
            print("⚠️  PostgreSQL optimization completed with warnings")
            print("Some optimizations may not have been applied.")
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
