#!/usr/bin/env python3
"""
Content Processing for RAG
Processes existing content and generates embeddings for vector search
"""

import os
import sys
import time
import logging
from typing import List, Dict, Any, Optional

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.session import get_db_session
from database.models import Content, ContentChunk
from processor.rag import RAGSystem
from processor.chunker import ContentChunker
from sqlalchemy.orm import Session
from sqlalchemy import func

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentProcessor:
    """Processes content for RAG system"""
    
    def __init__(self, batch_size: int = 50):
        self.session = get_db_session()
        self.rag_system = RAGSystem()
        self.chunker = ContentChunker()
        self.batch_size = batch_size
        
        # Initialize embedding model
        self.embedding_model = self.rag_system.get_embedding_model()
        
    def get_content_stats(self) -> Dict[str, Any]:
        """Get current content and chunk statistics"""
        try:
            # Content stats
            content_count = self.session.query(Content).count()
            processed_content = self.session.query(Content).filter(
                Content.processed == True
            ).count()
            
            # Chunk stats
            chunk_count = self.session.query(ContentChunk).count()
            chunks_with_embeddings = self.session.query(ContentChunk).filter(
                ContentChunk.embedding.isnot(None)
            ).count()
            
            # Content without chunks
            content_ids_with_chunks = self.session.query(ContentChunk.content_id).distinct().all()
            content_ids_with_chunks = [row[0] for row in content_ids_with_chunks]
            content_without_chunks = self.session.query(Content).filter(
                ~Content.id.in_(content_ids_with_chunks)
            ).count()
            
            return {
                'total_content': content_count,
                'processed_content': processed_content,
                'content_without_chunks': content_without_chunks,
                'total_chunks': chunk_count,
                'chunks_with_embeddings': chunks_with_embeddings,
                'chunks_without_embeddings': chunk_count - chunks_with_embeddings,
                'embedding_coverage': f"{(chunks_with_embeddings/chunk_count*100):.1f}%" if chunk_count > 0 else "0%"
            }
            
        except Exception as e:
            logger.error(f"Error getting content stats: {e}")
            return {}
    
    def chunk_content(self, content_id: int, force_rechunk: bool = False) -> List[ContentChunk]:
        """Chunk a single content item"""
        try:
            # Get content
            content = self.session.query(Content).filter(Content.id == content_id).first()
            if not content:
                logger.error(f"Content {content_id} not found")
                return []
            
            # Check if already chunked
            existing_chunks = self.session.query(ContentChunk).filter(
                ContentChunk.content_id == content_id
            ).all()
            
            if existing_chunks and not force_rechunk:
                logger.info(f"Content {content_id} already chunked ({len(existing_chunks)} chunks)")
                return existing_chunks
            
            # Delete existing chunks if force rechunking
            if existing_chunks and force_rechunk:
                for chunk in existing_chunks:
                    self.session.delete(chunk)
                self.session.commit()
                logger.info(f"Deleted {len(existing_chunks)} existing chunks for content {content_id}")
            
            # Create chunks
            chunks_data = self.chunker.chunk_content(
                content=content.content,
                chunk_size=1000,
                overlap=200,
                content_type=content.content_type or 'text'
            )
            
            chunks = []
            for i, chunk_data in enumerate(chunks_data):
                chunk = ContentChunk(
                    content_id=content_id,
                    sequence_number=i,
                    content=chunk_data['text'],
                    metadata={
                        'chunk_size': len(chunk_data['text']),
                        'url': content.url,
                        'title': content.title,
                        'content_type': content.content_type
                    }
                )
                self.session.add(chunk)
                chunks.append(chunk)
            
            # Mark content as processed
            content.processed = True
            self.session.commit()
            
            logger.info(f"Created {len(chunks)} chunks for content {content_id}")
            return chunks
            
        except Exception as e:
            logger.error(f"Error chunking content {content_id}: {e}")
            self.session.rollback()
            return []
    
    def generate_embeddings_for_chunks(self, chunk_ids: List[int] = None) -> int:
        """Generate embeddings for chunks"""
        try:
            # Get chunks without embeddings
            query = self.session.query(ContentChunk).filter(
                ContentChunk.embedding.is_(None)
            )
            
            if chunk_ids:
                query = query.filter(ContentChunk.id.in_(chunk_ids))
            
            chunks_without_embeddings = query.limit(self.batch_size).all()
            
            if not chunks_without_embeddings:
                logger.info("All chunks already have embeddings")
                return 0
            
            logger.info(f"Generating embeddings for {len(chunks_without_embeddings)} chunks...")
            
            processed_count = 0
            for i, chunk in enumerate(chunks_without_embeddings):
                try:
                    # Generate embedding
                    embedding = self.embedding_model.encode(chunk.content)
                    
                    # Store embedding as list
                    chunk.embedding = embedding.tolist()
                    processed_count += 1
                    
                    # Log progress
                    if (i + 1) % 10 == 0:
                        logger.info(f"  Processed {i + 1}/{len(chunks_without_embeddings)} chunks")
                        
                except Exception as e:
                    logger.error(f"Error generating embedding for chunk {chunk.id}: {e}")
                    continue
            
            # Commit all changes
            self.session.commit()
            logger.info(f"✅ Generated embeddings for {processed_count} chunks")
            
            return processed_count
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            self.session.rollback()
            return 0
    
    def process_unprocessed_content(self) -> Dict[str, int]:
        """Process all content that hasn't been chunked yet"""
        try:
            # Get content without chunks
            content_ids_with_chunks = self.session.query(ContentChunk.content_id).distinct().all()
            content_ids_with_chunks = [row[0] for row in content_ids_with_chunks]
            
            unprocessed_content = self.session.query(Content).filter(
                ~Content.id.in_(content_ids_with_chunks)
            ).all()
            
            if not unprocessed_content:
                logger.info("All content has already been processed")
                return {'content_processed': 0, 'chunks_created': 0}
            
            logger.info(f"Processing {len(unprocessed_content)} unprocessed content items...")
            
            total_chunks_created = 0
            content_processed = 0
            
            for content in unprocessed_content:
                logger.info(f"Processing content {content.id}: {content.title[:50]}...")
                
                chunks = self.chunk_content(content.id)
                total_chunks_created += len(chunks)
                
                if chunks:
                    content_processed += 1
                    
                # Brief pause to avoid overwhelming the system
                time.sleep(0.1)
            
            logger.info(f"✅ Processed {content_processed} content items, created {total_chunks_created} chunks")
            
            return {
                'content_processed': content_processed,
                'chunks_created': total_chunks_created
            }
            
        except Exception as e:
            logger.error(f"Error processing unprocessed content: {e}")
            return {'content_processed': 0, 'chunks_created': 0}
    
    def process_all_missing_embeddings(self) -> int:
        """Process all chunks that don't have embeddings"""
        try:
            total_processed = 0
            
            while True:
                # Process next batch
                batch_processed = self.generate_embeddings_for_chunks()
                total_processed += batch_processed
                
                # If batch was smaller than batch_size, we're done
                if batch_processed < self.batch_size:
                    break
                
                # Brief pause between batches
                time.sleep(1)
            
            return total_processed
            
        except Exception as e:
            logger.error(f"Error processing missing embeddings: {e}")
            return 0
    
    def validate_processed_content(self) -> Dict[str, Any]:
        """Validate that content has been properly processed"""
        try:
            stats = self.get_content_stats()
            
            issues = []
            
            # Check for content without chunks
            if stats['content_without_chunks'] > 0:
                issues.append(f"{stats['content_without_chunks']} content items have no chunks")
            
            # Check for chunks without embeddings
            if stats['chunks_without_embeddings'] > 0:
                issues.append(f"{stats['chunks_without_embeddings']} chunks have no embeddings")
            
            # Check embedding coverage
            if stats['total_chunks'] > 0:
                coverage = stats['chunks_with_embeddings'] / stats['total_chunks']
                if coverage < 0.9:  # Less than 90% coverage
                    issues.append(f"Only {stats['embedding_coverage']} of chunks have embeddings")
            
            return {
                'valid': len(issues) == 0,
                'issues': issues,
                'stats': stats
            }
            
        except Exception as e:
            logger.error(f"Error validating content: {e}")
            return {'valid': False, 'error': str(e)}
    
    def run_full_processing(self) -> Dict[str, Any]:
        """Run complete content processing pipeline"""
        logger.info("🚀 Starting Full Content Processing for RAG")
        logger.info("=" * 50)
        
        # Step 1: Get initial stats
        logger.info("\n1️⃣ Getting content statistics...")
        initial_stats = self.get_content_stats()
        logger.info(f"   📄 Total content: {initial_stats['total_content']}")
        logger.info(f"   🧩 Total chunks: {initial_stats['total_chunks']}")
        logger.info(f"   🎯 Chunks with embeddings: {initial_stats['chunks_with_embeddings']}")
        logger.info(f"   📊 Embedding coverage: {initial_stats['embedding_coverage']}")
        
        if initial_stats['total_content'] == 0:
            logger.warning("⚠️ No content found. Please crawl some websites first.")
            return {'success': False, 'error': 'No content to process'}
        
        # Step 2: Process unprocessed content
        logger.info("\n2️⃣ Processing unprocessed content...")
        processing_results = self.process_unprocessed_content()
        logger.info(f"   ✅ Processed {processing_results['content_processed']} content items")
        logger.info(f"   ✅ Created {processing_results['chunks_created']} new chunks")
        
        # Step 3: Generate missing embeddings
        logger.info("\n3️⃣ Generating missing embeddings...")
        embeddings_generated = self.process_all_missing_embeddings()
        logger.info(f"   ✅ Generated {embeddings_generated} embeddings")
        
        # Step 4: Get final stats
        logger.info("\n4️⃣ Getting final statistics...")
        final_stats = self.get_content_stats()
        logger.info(f"   📄 Total content: {final_stats['total_content']}")
        logger.info(f"   🧩 Total chunks: {final_stats['total_chunks']}")
        logger.info(f"   🎯 Chunks with embeddings: {final_stats['chunks_with_embeddings']}")
        logger.info(f"   📊 Embedding coverage: {final_stats['embedding_coverage']}")
        
        # Step 5: Validate results
        logger.info("\n5️⃣ Validating processed content...")
        validation = self.validate_processed_content()
        
        if validation['valid']:
            logger.info("   ✅ All content properly processed!")
        else:
            logger.warning("   ⚠️ Issues found:")
            for issue in validation['issues']:
                logger.warning(f"     - {issue}")
        
        # Summary
        total_improvement = final_stats['chunks_with_embeddings'] - initial_stats['chunks_with_embeddings']
        
        logger.info(f"\n🎉 Content Processing Complete!")
        logger.info(f"   📈 Improvement: +{total_improvement} embeddings")
        logger.info(f"   📊 Final coverage: {final_stats['embedding_coverage']}")
        
        logger.info("\n📋 Next Steps:")
        logger.info("   1. Test vector search: python scripts/test_full_rag_pipeline.py")
        logger.info("   2. Optimize database: python scripts/optimize_vector_db.py")
        logger.info("   3. Add more content with your crawler")
        
        return {
            'success': validation['valid'],
            'initial_stats': initial_stats,
            'final_stats': final_stats,
            'processing_results': processing_results,
            'embeddings_generated': embeddings_generated,
            'validation': validation,
            'improvement': total_improvement
        }
    
    def __del__(self):
        """Clean up database session"""
        if hasattr(self, 'session'):
            self.session.close()

def main():
    """Main processing function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Process content for RAG system')
    parser.add_argument('--batch-size', type=int, default=50, help='Batch size for processing')
    parser.add_argument('--embeddings-only', action='store_true', help='Only generate embeddings, skip chunking')
    parser.add_argument('--chunk-only', action='store_true', help='Only chunk content, skip embeddings')
    
    args = parser.parse_args()
    
    try:
        processor = ContentProcessor(batch_size=args.batch_size)
        
        if args.embeddings_only:
            logger.info("Running embeddings generation only...")
            count = processor.process_all_missing_embeddings()
            logger.info(f"Generated {count} embeddings")
        elif args.chunk_only:
            logger.info("Running content chunking only...")
            results = processor.process_unprocessed_content()
            logger.info(f"Processed {results['content_processed']} content items")
        else:
            # Run full processing
            processor.run_full_processing()
            
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
