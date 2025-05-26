#!/usr/bin/env python3
"""
Process Existing Content for RAG
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
    print("🔄 Processing Crawled Content for RAG")
    print("=" * 40)
    
    try:
        from database.session import get_db_session
        from database.models import Content, ContentChunk
        from database.db import Database
        from processor.rag import RAGSystem
        
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
        
        if not unprocessed_content:
            print("✅ All content is already processed for RAG!")
            
            # Check embeddings coverage
            total_chunks = session.query(ContentChunk).count()
            chunks_with_embeddings = session.query(ContentChunk).filter(
                ContentChunk.embedding.isnot(None)
            ).count()
            
            if chunks_with_embeddings < total_chunks:
                print(f"⚠️  Some chunks need embeddings: {chunks_with_embeddings}/{total_chunks}")
                print("🔄 Regenerating embeddings for all chunks...")
                
                # Process all content to ensure embeddings
                rag_system = RAGSystem(db)
                for content in all_content:
                    print(f"   🔄 Re-processing {content.title[:50] if content.title else 'No title'}...")
                    rag_system.process_content_for_rag(content.id)
            
            session.close()
            return True
        
        # Initialize RAG system
        rag_system = RAGSystem(db)
        
        print("\n🔄 Processing unprocessed content...")
        success_count = 0
        
        for i, content in enumerate(unprocessed_content, 1):
            title = content.title[:60] if content.title else 'No title'
            print(f"\n📄 Processing {i}/{len(unprocessed_content)}: {title}...")
            print(f"   URL: {content.url}")
            print(f"   Domain: {content.domain}")
            print(f"   Type: {content.content_type}")
            print(f"   Content length: {len(content.text or '')} chars")
            
            if not content.text or len(content.text.strip()) < 50:
                print("   ⚠️  Skipping - content too short or empty")
                continue
            
            try:
                success = rag_system.process_content_for_rag(content.id)
                if success:
                    print("   ✅ Processed successfully")
                    success_count += 1
                else:
                    print("   ❌ Processing failed")
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
        
        session.close()
        
        print(f"\n🎉 Processing Complete!")
        print(f"   Successfully processed: {success_count}/{len(unprocessed_content)}")
        
        if success_count > 0:
            print("\n✅ Your RAG system is now ready for content generation!")
            print("🔗 Test it at: http://localhost:5173 -> Content Generator")
        
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Failed to process content: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_content_preview():
    """Show a preview of what content is available"""
    try:
        from database.session import get_db_session
        from database.models import Content, ContentChunk
        
        session = get_db_session()
        
        # Show content overview
        contents = session.query(Content).limit(5).all()
        chunks = session.query(ContentChunk).limit(3).all()
        
        print("\n📖 Content Preview:")
        for content in contents:
            title = content.title[:60] if content.title else 'No title'
            print(f"   📄 {title}...")
            print(f"      Domain: {content.domain}")
            print(f"      URL: {content.url}")
            print(f"      Preview: {(content.text or '')[:100]}...")
            print()
        
        if chunks:
            print("📦 Sample Chunks:")
            for chunk in chunks:
                print(f"   🧩 Chunk: {chunk.text[:100]}...")
                has_embedding = chunk.embedding is not None
                print(f"      Has embedding: {'✅' if has_embedding else '❌'}")
                print()
        
        session.close()
        
    except Exception as e:
        print(f"❌ Could not show preview: {e}")

def main():
    print("🚀 VoiceForge RAG Content Processor")
    print("=" * 35)
    
    # Show current content
    show_content_preview()
    
    # Process content
    success = process_crawled_content()
    
    if success:
        print("\n🎯 Next Steps:")
        print("   1. Test content generation: http://localhost:5173")
        print("   2. Try queries related to your crawled content")
        print("   3. Check system status: python scripts/quick_status.py")
    else:
        print("\n🔧 Troubleshooting:")
        print("   • Check if you have crawled content")
        print("   • Verify database connection")
        print("   • Run: python scripts/quick_status.py")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
