#!/usr/bin/env python3
"""
Process Existing Content for RAG - FIXED VERSION
Takes your crawled content and processes it into chunks with embeddings
"""

import os
import sys
from datetime import datetime

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

def process_crawled_content():
    """Process all crawled content for RAG"""
    print("🔄 Processing Crawled Content for RAG - Fixed Version")
    print("=" * 50)
    
    try:
        from database.session import get_db_session
        from database.models import Content, ContentChunk
        from database.db import Database
        from processor.rag import RAGSystem
        from processor.chunker import ContentChunker
        
        session = get_db_session()
        db = Database(session)
        
        # Get all content that hasn't been processed yet
        all_content = session.query(Content).all()
        processed_content_ids = session.query(ContentChunk.content_id).distinct().all()
        processed_ids = [row[0] for row in processed_content_ids]
        
        unprocessed_content = [c for c in all_content if c.id not in processed_ids]
        
        print(f"📊 Content Status:")
        print(f"   Total content items: {len(all_content)}")
        print(f"   Already processed: {len(processed_ids)}")
        print(f"   Need processing: {len(unprocessed_content)}")
        
        if len(all_content) == 0:
            print("\n❌ NO CONTENT FOUND!")
            print("🔧 You need to crawl some websites first.")
            session.close()
            return False
        
        # Show content preview
        print(f"\n📖 Content Preview:")
        for i, content in enumerate(all_content[:3], 1):
            title = content.title[:60] if content.title else 'No title'
            print(f"   {i}. {title}...")
            print(f"      Domain: {content.domain}")
            print(f"      Text length: {len(content.text or '')} chars")
        
        if not unprocessed_content:
            print("✅ All content is already processed for RAG!")
            
            # Check embeddings coverage
            total_chunks = session.query(ContentChunk).count()
            chunks_with_embeddings = session.query(ContentChunk).filter(
                ContentChunk.embedding.isnot(None)
            ).count()
            
            print(f"📦 Chunk Status:")
            print(f"   Total chunks: {total_chunks}")
            print(f"   Chunks with embeddings: {chunks_with_embeddings}")
            
            if chunks_with_embeddings == 0 and total_chunks > 0:
                print("⚠️  Chunks exist but have no embeddings! Re-processing...")
                # Re-process all content to generate embeddings
                unprocessed_content = all_content
            else:
                session.close()
                return True
        
        # Initialize chunker and RAG system
        chunker = ContentChunker(chunk_size=500, chunk_overlap=100)
        rag_system = RAGSystem(db)
        
        print(f"\n🔄 Processing content for RAG...")
        success_count = 0
        
        for i, content_obj in enumerate(unprocessed_content, 1):
            title = content_obj.title[:60] if content_obj.title else 'No title'
            print(f"\n📄 Processing {i}/{len(unprocessed_content)}: {title}...")
            print(f"   URL: {content_obj.url}")
            print(f"   Domain: {content_obj.domain}")
            print(f"   Type: {content_obj.content_type}")
            print(f"   Text length: {len(content_obj.text or '')} chars")
            
            if not content_obj.text or len(content_obj.text.strip()) < 50:
                print("   ⚠️  Skipping - content too short or empty")
                continue
            
            try:
                # Format content for the chunker
                content_for_chunker = {
                    "content_id": content_obj.id,
                    "text": content_obj.text,
                    "domain": content_obj.domain,
                    "url": content_obj.url,
                    "metadata": {
                        "title": content_obj.title,
                        "content_type": content_obj.content_type,
                        "domain": content_obj.domain
                    }
                }
                
                # Generate chunks
                chunks = chunker.process_content(content_for_chunker)
                print(f"   📦 Generated {len(chunks)} chunks")
                
                if not chunks:
                    print("   ⚠️  No chunks generated")
                    continue
                
                # Get embedding model
                embedding_model = rag_system.get_embedding_model()
                
                # Generate embeddings for chunks
                texts = [chunk["text"] for chunk in chunks]
                embeddings = embedding_model.encode(texts)
                
                # Add embeddings to chunks
                for j, embedding in enumerate(embeddings):
                    chunks[j]["embedding"] = embedding.tolist()
                
                print(f"   🧠 Generated embeddings for {len(chunks)} chunks")
                
                # Store chunks in database
                db.store_content_chunks(chunks)
                print(f"   💾 Stored chunks in database")
                
                success_count += 1
                print("   ✅ Processed successfully")
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
                import traceback
                traceback.print_exc()
        
        session.close()
        
        print(f"\n🎉 Processing Complete!")
        print(f"   Successfully processed: {success_count}/{len(unprocessed_content)}")
        
        if success_count > 0:
            print("\n✅ Your RAG system is now ready for content generation!")
            print("🔗 Test it at: http://localhost:5173 -> Content Generator")
            print("💡 Try queries related to your crawled content topics")
        
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Failed to process content: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🚀 VoiceForge RAG Content Processor - Fixed")
    print("=" * 42)
    
    # Process content
    success = process_crawled_content()
    
    if success:
        print("\n🎯 Next Steps:")
        print("   1. Test content generation: http://localhost:5173")
        print("   2. Try queries like 'code signing' or 'digital certificates'")
        print("   3. Check system status: python diagnose_content.py")
    else:
        print("\n🔧 Troubleshooting:")
        print("   • Check if you have crawled content")
        print("   • Verify database connection")
        print("   • Run: python diagnose_content.py")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
