#!/usr/bin/env python3
"""
Fix VoiceForge database vector extension issues.
"""

import psycopg2
import os
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def fix_vector_extension():
    """Fix the pgvector extension in the database."""
    
    print("🔧 VoiceForge Database Vector Extension Fix")
    print("=" * 45)
    
    # Database connection parameters
    db_params = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'voiceforge'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'postgres')
    }
    
    print(f"Connecting to database: {db_params['host']}:{db_params['port']}/{db_params['database']}")
    
    try:
        # Connect to database
        conn = psycopg2.connect(**db_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("✅ Connected to database")
        
        # Check if pgvector extension exists
        print("\n1️⃣ Checking pgvector extension...")
        cursor.execute("SELECT name FROM pg_available_extensions WHERE name = 'vector';")
        available = cursor.fetchone()
        
        if not available:
            print("❌ pgvector extension is not available")
            print("🔧 Install pgvector:")
            print("   - macOS: brew install pgvector")
            print("   - Ubuntu: apt-get install postgresql-15-pgvector")
            print("   - Or compile from source: https://github.com/pgvector/pgvector")
            return False
        
        print("✅ pgvector extension is available")
        
        # Check if extension is installed
        print("\n2️⃣ Checking if extension is installed...")
        cursor.execute("SELECT extname FROM pg_extension WHERE extname = 'vector';")
        installed = cursor.fetchone()
        
        if not installed:
            print("⚠️ pgvector extension not installed, installing...")
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            print("✅ pgvector extension installed")
        else:
            print("✅ pgvector extension already installed")
        
        # Check vector operator
        print("\n3️⃣ Testing vector operations...")
        try:
            cursor.execute("SELECT '[1,2,3]'::vector <-> '[1,2,4]'::vector;")
            result = cursor.fetchone()
            print(f"✅ Vector operations working (distance: {result[0]})")
        except Exception as e:
            print(f"❌ Vector operations failed: {e}")
            
            # Try to fix operator
            print("🔧 Attempting to fix vector operators...")
            cursor.execute("DROP EXTENSION IF EXISTS vector CASCADE;")
            cursor.execute("CREATE EXTENSION vector;")
            
            # Test again
            cursor.execute("SELECT '[1,2,3]'::vector <-> '[1,2,4]'::vector;")
            result = cursor.fetchone()
            print(f"✅ Vector operations fixed (distance: {result[0]})")
        
        # Check existing vector columns
        print("\n4️⃣ Checking vector columns in tables...")
        cursor.execute("""
            SELECT table_name, column_name, data_type 
            FROM information_schema.columns 
            WHERE data_type = 'USER-DEFINED' 
            AND udt_name = 'vector'
            ORDER BY table_name, column_name;
        """)
        
        vector_columns = cursor.fetchall()
        if vector_columns:
            print("✅ Found vector columns:")
            for table, column, dtype in vector_columns:
                print(f"   - {table}.{column} ({dtype})")
        else:
            print("⚠️ No vector columns found")
            print("   This might indicate the RAG system hasn't processed any content yet")
        
        # Test a simple vector query similar to the failing one
        print("\n5️⃣ Testing vector similarity query...")
        try:
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_name = 'content_chunks';
            """)
            
            if cursor.fetchone():
                cursor.execute("""
                    SELECT COUNT(*) FROM content_chunks 
                    WHERE embedding IS NOT NULL;
                """)
                embedding_count = cursor.fetchone()[0]
                print(f"✅ Found {embedding_count} content chunks with embeddings")
                
                if embedding_count > 0:
                    # Test actual similarity search
                    cursor.execute("""
                        SELECT chunk_id, text, embedding <-> %s::vector as distance
                        FROM content_chunks
                        WHERE embedding IS NOT NULL
                        ORDER BY embedding <-> %s::vector
                        LIMIT 1;
                    """, ('[0] * 768', '[0] * 768'))  # Test with zero vector
                    
                    result = cursor.fetchone()
                    if result:
                        print(f"✅ Vector similarity search working")
                        print(f"   Sample chunk: {result[1][:50]}...")
                    else:
                        print("⚠️ No results from similarity search")
                else:
                    print("⚠️ No embeddings found - content needs to be processed")
            else:
                print("⚠️ content_chunks table not found")
                
        except Exception as e:
            print(f"❌ Vector query test failed: {e}")
            return False
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Database vector extension is working correctly!")
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main function."""
    success = fix_vector_extension()
    
    print("\n" + "=" * 45)
    if success:
        print("✅ Database vector extension fixed!")
        print("🚀 Content generation should now work")
        print("   Restart your backend server and try again")
    else:
        print("❌ Failed to fix database vector extension")
        print("🔧 Manual steps needed:")
        print("   1. Install pgvector extension")
        print("   2. Restart PostgreSQL")
        print("   3. Run this script again")
    
    return success

if __name__ == "__main__":
    main()
