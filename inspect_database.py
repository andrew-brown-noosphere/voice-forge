#!/usr/bin/env python3
"""
Direct Database Inspection - See exactly what's in the database
"""

import os
import sys

# Load environment
def load_env_file():
    backend_path = '/Users/andrewbrown/Sites/noosphere/github/voice-forge/backend'
    env_path = os.path.join(backend_path, '.env')
    
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env_file()

# Add backend to path
backend_path = '/Users/andrewbrown/Sites/noosphere/github/voice-forge/backend'
sys.path.append(backend_path)

def inspect_database():
    """Direct inspection of database contents"""
    print("🔍 Direct Database Inspection")
    print("=" * 30)
    
    try:
        from database.session import get_db_session
        from database.models import Content, ContentChunk
        from sqlalchemy import text
        
        session = get_db_session()
        
        print("1️⃣ Checking Content Table...")
        try:
            content_count = session.query(Content).count()
            print(f"   Content items: {content_count}")
            
            if content_count > 0:
                # Show first few content items
                contents = session.query(Content).limit(3).all()
                for i, content in enumerate(contents, 1):
                    print(f"   {i}. ID: {content.id[:8]}...")
                    print(f"      Title: {content.title or 'No title'}")
                    print(f"      Domain: {content.domain}")
                    print(f"      Text length: {len(content.text or '')} chars")
                    if content.text:
                        print(f"      Text sample: {content.text[:100]}...")
                    print()
            else:
                print("   ❌ NO CONTENT FOUND!")
                session.close()
                return False
                
        except Exception as e:
            print(f"   ❌ Error reading content: {e}")
            session.rollback()
        
        print("2️⃣ Checking ContentChunk Table...")
        try:
            chunk_count = session.query(ContentChunk).count()
            print(f"   Chunk items: {chunk_count}")
            
            if chunk_count == 0:
                print("   ❌ NO CHUNKS FOUND!")
                print("   🔧 This is the problem - content needs to be processed!")
                session.close()
                return False
            
            # Show first few chunks
            chunks = session.query(ContentChunk).limit(3).all()
            for i, chunk in enumerate(chunks, 1):
                print(f"   {i}. Chunk ID: {chunk.id[:8]}...")
                print(f"      Content ID: {chunk.content_id[:8]}...")
                print(f"      Text: {chunk.text[:80]}...")
                print(f"      Has embedding: {'✅' if chunk.embedding else '❌'}")
                print()
                
        except Exception as e:
            print(f"   ❌ Error reading chunks: {e}")
            session.rollback()
        
        print("3️⃣ Testing Raw SQL...")
        try:
            # Try direct SQL to bypass ORM issues
            result = session.execute(text("SELECT COUNT(*) FROM content_chunks"))
            count = result.scalar()
            print(f"   Raw SQL chunk count: {count}")
            
            if count > 0:
                # Try to get a sample chunk
                result = session.execute(text("SELECT text FROM content_chunks LIMIT 1"))
                sample = result.scalar()
                print(f"   Sample chunk text: {sample[:100] if sample else 'NULL'}...")
            
        except Exception as e:
            print(f"   ❌ Raw SQL error: {e}")
            session.rollback()
        
        session.close()
        return chunk_count > 0
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def process_if_needed():
    """Process content if chunks are missing"""
    print("\n🔄 Processing Content for RAG")
    print("=" * 30)
    
    try:
        from database.session import get_db_session
        from database.models import Content, ContentChunk
        from database.db import Database
        from processor.rag import RAGSystem
        import uuid
        from datetime import datetime
        
        session = get_db_session()
        db = Database(session)
        
        # Get all content
        all_content = session.query(Content).all()
        print(f"📄 Found {len(all_content)} content items to process")
        
        if not all_content:
            print("❌ No content to process!")
            session.close()
            return False
        
        # Process each content item manually
        success_count = 0
        for i, content_obj in enumerate(all_content, 1):
            print(f"\n📄 Processing {i}/{len(all_content)}: {content_obj.title or 'No title'}...")
            
            if not content_obj.text or len(content_obj.text.strip()) < 50:
                print("   ⚠️  Skipping - content too short")
                continue
            
            try:
                # Simple chunking (no NLTK)
                text = content_obj.text
                chunk_size = 500
                words = text.split()
                
                chunks_created = 0
                for j in range(0, len(words), chunk_size):
                    chunk_words = words[j:j + chunk_size]
                    chunk_text = ' '.join(chunk_words)
                    
                    if len(chunk_text.strip()) < 50:
                        continue
                    
                    # Create chunk manually
                    chunk = ContentChunk(
                        id=str(uuid.uuid4()),
                        content_id=content_obj.id,
                        chunk_index=j // chunk_size,
                        text=chunk_text,
                        start_char=0,  # Simplified
                        end_char=len(chunk_text),
                        embedding=None,  # Will add later
                        chunk_metadata={
                            "title": content_obj.title,
                            "domain": content_obj.domain,
                            "created_at": datetime.utcnow().isoformat()
                        }
                    )
                    
                    session.add(chunk)
                    chunks_created += 1
                
                session.commit()
                print(f"   ✅ Created {chunks_created} chunks")
                success_count += 1
                
            except Exception as e:
                print(f"   ❌ Error processing: {e}")
                session.rollback()
        
        session.close()
        
        print(f"\n🎉 Processed {success_count}/{len(all_content)} content items")
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Processing failed: {e}")
        return False

def main():
    print("🚀 Database Inspection & Fix")
    print("=" * 28)
    
    # Step 1: Inspect what's there
    has_chunks = inspect_database()
    
    if not has_chunks:
        print("\n🔧 No chunks found - processing content...")
        success = process_if_needed()
        
        if success:
            print("\n✅ Content processed! Now test:")
            print("   1. Restart backend server")
            print("   2. Try content generation again")
        else:
            print("\n❌ Processing failed")
            print("🔧 You may need to crawl content first")
    else:
        print("\n✅ Chunks exist! The issue might be:")
        print("   1. Database connection problems")
        print("   2. Search query issues")
        print("   3. Restart backend: cd backend && python -m uvicorn api.main:app --reload")

if __name__ == "__main__":
    main()
