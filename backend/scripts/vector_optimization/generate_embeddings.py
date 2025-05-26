#!/usr/bin/env python3
"""
Generate embeddings for existing content and chunks.

This script processes content that doesn't have embeddings yet,
generating them using your configured embedding service.
"""

import sys
import os
import time
import logging
from typing import Optional

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def generate_missing_embeddings():
    """Generate embeddings for content and chunks that don't have them."""
    print("🧠 Generating Missing Embeddings")
    print("=" * 40)
    
    try:
        from database.session import get_db_session
        from database.models import Content, ContentChunk
        from processor.embeddings.embedding_service import EmbeddingService
        
        # Initialize embedding service
        print("Initializing embedding service...")
        embedding_service = EmbeddingService()
        
        with get_db_session() as session:
            # Process content without embeddings
            content_without_embeddings = session.query(Content).filter(Content.embedding.is_(None)).all()
            
            if content_without_embeddings:
                print(f"\n📄 Processing {len(content_without_embeddings)} content items...")
                
                for i, content in enumerate(content_without_embeddings):
                    try:
                        # Limit text length to prevent token limit issues
                        text_to_embed = content.text[:8000] if content.text else ""
                        
                        if not text_to_embed.strip():
                            print(f"  ⚠️  Skipping content {content.id}: no text")
                            continue
                        
                        # Generate embedding
                        embedding = embedding_service.generate_embedding(text_to_embed)
                        
                        if embedding:
                            content.embedding = embedding
                            content.is_processed = True
                            
                            print(f"  ✅ Content {i+1}/{len(content_without_embeddings)}: {content.title[:50] if content.title else content.id}")
                        else:
                            print(f"  ❌ Failed to generate embedding for content {content.id}")
                        
                        # Commit every 10 items to avoid losing progress
                        if i % 10 == 0:
                            session.commit()
                            print(f"     💾 Saved progress ({i+1} items)")
                            
                        # Rate limiting to avoid API limits
                        if i % 50 == 0 and i > 0:
                            print("     ⏸️  Pausing to respect rate limits...")
                            time.sleep(2)
                            
                    except Exception as e:
                        print(f"  ❌ Error processing content {content.id}: {str(e)}")
                
                # Final commit
                session.commit()
                print(f"✅ Completed content embedding generation")
            else:
                print("✅ All content already has embeddings")
            
            # Process chunks without embeddings
            chunks_without_embeddings = session.query(ContentChunk).filter(ContentChunk.embedding.is_(None)).all()
            
            if chunks_without_embeddings:
                print(f"\n🧩 Processing {len(chunks_without_embeddings)} chunks...")
                
                for i, chunk in enumerate(chunks_without_embeddings):
                    try:
                        if not chunk.text.strip():
                            print(f"  ⚠️  Skipping chunk {chunk.id}: no text")
                            continue
                        
                        # Generate embedding for chunk
                        embedding = embedding_service.generate_embedding(chunk.text)
                        
                        if embedding:
                            chunk.embedding = embedding
                            print(f"  ✅ Chunk {i+1}/{len(chunks_without_embeddings)}: {chunk.id}")
                        else:
                            print(f"  ❌ Failed to generate embedding for chunk {chunk.id}")
                        
                        # Commit every 10 items
                        if i % 10 == 0:
                            session.commit()
                            print(f"     💾 Saved progress ({i+1} chunks)")
                            
                        # Rate limiting
                        if i % 50 == 0 and i > 0:
                            print("     ⏸️  Pausing to respect rate limits...")
                            time.sleep(2)
                            
                    except Exception as e:
                        print(f"  ❌ Error processing chunk {chunk.id}: {str(e)}")
                
                # Final commit
                session.commit()
                print(f"✅ Completed chunk embedding generation")
            else:
                print("✅ All chunks already have embeddings")
        
        print("\n🎉 Embedding generation complete!")
        
        # Show final statistics
        with get_db_session() as session:
            total_content = session.query(Content).count()
            content_with_embeddings = session.query(Content).filter(Content.embedding.isnot(None)).count()
            
            total_chunks = session.query(ContentChunk).count()
            chunks_with_embeddings = session.query(ContentChunk).filter(ContentChunk.embedding.isnot(None)).count()
            
            print(f"\n📊 Final Statistics:")
            print(f"   Content: {content_with_embeddings}/{total_content} have embeddings ({content_with_embeddings/total_content*100:.1f}%)")
            print(f"   Chunks: {chunks_with_embeddings}/{total_chunks} have embeddings ({chunks_with_embeddings/total_chunks*100:.1f}%)")
        
    except Exception as e:
        print(f"❌ Embedding generation failed: {str(e)}")
        logger.exception("Embedding generation failed")

def generate_embeddings_for_domain(domain: str):
    """Generate embeddings for content from a specific domain only."""
    print(f"🧠 Generating Embeddings for Domain: {domain}")
    print("=" * 50)
    
    try:
        from database.session import get_db_session
        from database.models import Content, ContentChunk
        from processor.embeddings.embedding_service import EmbeddingService
        
        embedding_service = EmbeddingService()
        
        with get_db_session() as session:
            # Process content without embeddings from specific domain
            content_query = session.query(Content).filter(
                Content.domain == domain,
                Content.embedding.is_(None)
            )
            content_without_embeddings = content_query.all()
            
            if content_without_embeddings:
                print(f"📄 Processing {len(content_without_embeddings)} content items from {domain}...")
                
                for i, content in enumerate(content_without_embeddings):
                    try:
                        text_to_embed = content.text[:8000] if content.text else ""
                        
                        if not text_to_embed.strip():
                            continue
                        
                        embedding = embedding_service.generate_embedding(text_to_embed)
                        
                        if embedding:
                            content.embedding = embedding
                            content.is_processed = True
                            print(f"  ✅ {i+1}/{len(content_without_embeddings)}: {content.title[:50] if content.title else content.url}")
                        
                        if i % 10 == 0:
                            session.commit()
                            
                    except Exception as e:
                        print(f"  ❌ Error: {str(e)}")
                
                session.commit()
                print(f"✅ Domain {domain} content embedding complete")
            else:
                print(f"✅ All content from {domain} already has embeddings")
        
    except Exception as e:
        print(f"❌ Domain embedding generation failed: {str(e)}")

def main():
    """Main function with command line options."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate embeddings for VoiceForge content')
    parser.add_argument('--domain', help='Generate embeddings for specific domain only')
    parser.add_argument('--check-only', action='store_true', help='Only check current embedding status')
    
    args = parser.parse_args()
    
    if args.check_only:
        # Just show current status
        try:
            from database.session import get_db_session
            from database.models import Content, ContentChunk
            
            with get_db_session() as session:
                total_content = session.query(Content).count()
                content_with_embeddings = session.query(Content).filter(Content.embedding.isnot(None)).count()
                
                total_chunks = session.query(ContentChunk).count()
                chunks_with_embeddings = session.query(ContentChunk).filter(ContentChunk.embedding.isnot(None)).count()
                
                print("📊 Current Embedding Status:")
                print(f"   Content: {content_with_embeddings}/{total_content} have embeddings ({content_with_embeddings/total_content*100:.1f}%)")
                print(f"   Chunks: {chunks_with_embeddings}/{total_chunks} have embeddings ({chunks_with_embeddings/total_chunks*100:.1f}%)")
                
                if content_with_embeddings < total_content or chunks_with_embeddings < total_chunks:
                    print("\n💡 To generate missing embeddings:")
                    print("   python scripts/vector_optimization/generate_embeddings.py")
                else:
                    print("\n✅ All content has embeddings!")
        
        except Exception as e:
            print(f"❌ Status check failed: {str(e)}")
    
    elif args.domain:
        generate_embeddings_for_domain(args.domain)
    else:
        generate_missing_embeddings()

if __name__ == "__main__":
    main()
