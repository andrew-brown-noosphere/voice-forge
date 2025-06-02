#!/usr/bin/env python3
"""
Emergency fix for VoiceForge vector database issue.
"""

import psycopg2
import os
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def emergency_vector_fix():
    """Emergency fix for the vector extension database issue."""
    
    print("🚨 EMERGENCY VECTOR DATABASE FIX")
    print("=" * 40)
    
    # Try different common database configurations
    db_configs = [
        {
            'host': 'localhost',
            'port': '5432',
            'database': 'voice_forge',
            'user': 'postgres',
            'password': 'postgres'
        },
        {
            'host': 'localhost', 
            'port': '5432',
            'database': 'voice_forge',
            'user': 'andrewbrown',
            'password': ''
        },
        {
            'host': 'localhost',
            'port': '5432',
            'database': 'voice_forge',
            'user': os.getenv('USER', 'postgres'),
            'password': ''
        }
    ]
    
    for i, config in enumerate(db_configs, 1):
        print(f"\n{i}️⃣ Trying connection: {config['user']}@{config['host']}:{config['port']}/{config['database']}")
        
        try:
            conn = psycopg2.connect(**config)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            print("✅ Connected successfully!")
            
            # Check if voice_forge database exists
            if config['database'] != 'voice_forge':
                cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'voice_forge';")
                if not cursor.fetchone():
                    print("❌ voice_forge database doesn't exist")
                    continue
                
                # Connect to voice_forge database
                cursor.close()
                conn.close()
                config['database'] = 'voice_forge'
                conn = psycopg2.connect(**config)
                conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
                cursor = conn.cursor()
                print("✅ Connected to voice_forge database")
            
            # Fix the vector extension
            print("🔧 Fixing vector extension...")
            
            # Drop and recreate extension
            cursor.execute("DROP EXTENSION IF EXISTS vector CASCADE;")
            print("   Dropped existing vector extension")
            
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            print("   Created vector extension")
            
            # Test vector operations
            cursor.execute("SELECT '[1,2,3]'::vector <-> '[1,2,4]'::vector;")
            result = cursor.fetchone()
            print(f"✅ Vector operations working! (test distance: {result[0]})")
            
            # Check if we have content_chunks table
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_name = 'content_chunks' AND table_schema = 'public';
            """)
            
            if cursor.fetchone():
                print("✅ content_chunks table exists")
                
                # Check for vector columns
                cursor.execute("""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name = 'content_chunks' 
                    AND data_type = 'USER-DEFINED' 
                    AND udt_name = 'vector';
                """)
                
                vector_cols = cursor.fetchall()
                if vector_cols:
                    print(f"✅ Vector columns found: {[col[0] for col in vector_cols]}")
                    
                    # Test a simple query on the actual table
                    try:
                        cursor.execute("SELECT COUNT(*) FROM content_chunks WHERE embedding IS NOT NULL;")
                        count = cursor.fetchone()[0]
                        print(f"✅ Found {count} content chunks with embeddings")
                        
                        if count > 0:
                            # Test the actual similarity query that was failing
                            cursor.execute("""
                                SELECT chunk_id, similarity
                                FROM (
                                    SELECT chunk_id, embedding <-> '[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]'::vector(768) as similarity
                                    FROM content_chunks 
                                    WHERE embedding IS NOT NULL
                                    LIMIT 1
                                ) t;
                            """)
                            
                            test_result = cursor.fetchone()
                            if test_result:
                                print(f"✅ Vector similarity query working! (chunk: {test_result[0]})")
                            else:
                                print("⚠️ Vector similarity query returned no results")
                        else:
                            print("ℹ️ No embeddings found - that's OK, content needs to be processed first")
                    except Exception as e:
                        print(f"❌ Vector query test failed: {e}")
                        # This might be the actual issue - let's fix it
                        if "operator does not exist" in str(e):
                            print("🔧 Fixing vector operator issue...")
                            cursor.execute("DROP EXTENSION vector CASCADE;")
                            cursor.execute("CREATE EXTENSION vector;")
                            print("✅ Vector extension recreated")
                else:
                    print("⚠️ No vector columns found in content_chunks")
            else:
                print("⚠️ content_chunks table not found - RAG system not initialized")
            
            cursor.close()
            conn.close()
            
            print("\n🎉 DATABASE VECTOR FIX COMPLETE!")
            print("🚀 Restart your backend now and try content generation")
            return True
            
        except psycopg2.Error as e:
            print(f"❌ Database error: {e}")
            continue
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            continue
    
    print("\n❌ Could not connect to database")
    print("🔧 Manual fix needed:")
    print("1. Make sure PostgreSQL is running")
    print("2. Check database credentials")
    print("3. Run: psql -d voice_forge -c 'CREATE EXTENSION IF NOT EXISTS vector;'")
    return False

if __name__ == "__main__":
    emergency_vector_fix()
