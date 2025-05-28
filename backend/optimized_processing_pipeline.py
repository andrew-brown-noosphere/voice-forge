#!/usr/bin/env python3
"""
Optimized Content Processing Pipeline for VoiceForge RAG System
Enhanced with better chunking, embedding generation, and error handling
"""

import os
import sys
import time
import logging
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import json
import uuid

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.session import get_db_session
from database.models import Content, ContentChunk
from database.db import Database
from processor.chunker import ContentChunker
from processor.service import ProcessorService
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OptimizedContentProcessor:
    """
    Optimized content processor with enhanced chunking, embedding generation,
    and robust error handling for the VoiceForge RAG system.
    """
    
    def __init__(self, 
                 chunk_size: int = 400, 
                 chunk_overlap: int = 80,
                 batch_size: int = 32,
                 max_workers: int = 4):
        """
        Initialize the optimized content processor.
        
        Args:
            chunk_size: Target chunk size in tokens
            chunk_overlap: Overlap between chunks in tokens
            batch_size: Batch size for embedding generation
            max_workers: Maximum number of worker threads
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.batch_size = batch_size
        self.max_workers = max_workers
        
        # Initialize components
        self.session = None
        self.db = None
        self.processor_service = None
        self.embedding_model = None
        
        # Performance tracking
        self.stats = {
            'content_processed': 0,
            'chunks_created': 0,
            'embeddings_generated': 0,
            'errors': 0,
            'start_time': None,
            'end_time': None
        }
        
        # Initialize chunker with optimized settings
        self.chunker = ContentChunker(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            respect_sentences=True
        )
    
    def _initialize_services(self):
        """Initialize database session and services."""
        if self.session is None:
            self.session = get_db_session()
            if hasattr(self.session, '__next__'):
                self.session = next(self.session)
            
            self.db = Database(self.session)
            self.processor_service = ProcessorService(self.db)
    
    def _get_embedding_model(self):
        """Lazy-load embedding model with fallback strategies."""
        if self.embedding_model is None:
            try:
                # Try to get from processor service first
                self._initialize_services()
                self.embedding_model = self.processor_service.get_embedding_model()
                logger.info("Loaded embedding model from processor service")
                
            except Exception as e:
                logger.warning(f"Failed to load from processor service: {e}")
                
                # Try direct import as fallback
                try:
                    from sentence_transformers import SentenceTransformer
                    self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                    logger.info("Loaded SentenceTransformer model directly")
                    
                except ImportError as e:
                    logger.error(f"SentenceTransformers not available: {e}")
                    raise RuntimeError("No embedding model available. Please install sentence-transformers.")
                
                except Exception as e:
                    logger.error(f"Failed to initialize embedding model: {e}")
                    raise
        
        return self.embedding_model
    
    def get_processing_statistics(self, org_id: str) -> Dict[str, Any]:
        """Get comprehensive processing statistics."""
        self._initialize_services()
        
        try:
            # Content statistics
            total_content = self.session.query(Content).filter(
                Content.org_id == org_id
            ).count()
            
            processed_content = self.session.query(Content).filter(
                and_(
                    Content.org_id == org_id,
                    Content.is_processed == True
                )
            ).count()
            
            # Chunk statistics
            total_chunks = self.session.query(ContentChunk).filter(
                ContentChunk.org_id == org_id
            ).count()
            
            chunks_with_embeddings = self.session.query(ContentChunk).filter(
                and_(
                    ContentChunk.org_id == org_id,
                    ContentChunk.embedding.isnot(None)
                )
            ).count()
            
            # Content without chunks
            content_with_chunks = self.session.query(ContentChunk.content_id).filter(
                ContentChunk.org_id == org_id
            ).distinct().count()
            
            content_without_chunks = total_content - content_with_chunks
            
            # Domain statistics
            domains = self.session.query(Content.domain).filter(
                Content.org_id == org_id
            ).distinct().all()
            domain_list = [d[0] for d in domains]
            
            # Content type statistics
            content_types = self.session.query(Content.content_type).filter(
                Content.org_id == org_id
            ).distinct().all()
            content_type_list = [ct[0] for ct in content_types]
            
            embedding_coverage = (chunks_with_embeddings / total_chunks * 100) if total_chunks > 0 else 0
            
            return {
                'content_stats': {
                    'total_content': total_content,
                    'processed_content': processed_content,
                    'content_without_chunks': content_without_chunks,
                    'processing_coverage': f"{(processed_content/total_content*100):.1f}%" if total_content > 0 else "0%"
                },
                'chunk_stats': {
                    'total_chunks': total_chunks,
                    'chunks_with_embeddings': chunks_with_embeddings,
                    'chunks_without_embeddings': total_chunks - chunks_with_embeddings,
                    'embedding_coverage': f"{embedding_coverage:.1f}%"
                },
                'domain_stats': {
                    'total_domains': len(domain_list),
                    'domains': domain_list
                },
                'content_type_stats': {
                    'total_types': len(content_type_list),
                    'content_types': content_type_list
                },
                'readiness': {
                    'ready_for_rag': embedding_coverage > 80,
                    'needs_processing': content_without_chunks > 0,
                    'needs_embeddings': (total_chunks - chunks_with_embeddings) > 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting processing statistics: {e}")
            return {}
    
    def optimize_chunking_strategy(self, content_type: str, content_length: int) -> Tuple[int, int]:
        """
        Optimize chunking parameters based on content type and length.
        
        Args:
            content_type: Type of content (blog, api_docs, etc.)
            content_length: Length of content in characters
            
        Returns:
            Tuple of (chunk_size, chunk_overlap)
        """
        # Content type specific optimizations
        if content_type in ['api_docs', 'documentation']:
            # Technical docs benefit from larger chunks with more context
            chunk_size = 600
            chunk_overlap = 120
        elif content_type in ['blog', 'article']:
            # Articles work well with medium chunks
            chunk_size = 400
            chunk_overlap = 80
        elif content_type in ['social_media', 'tweet']:
            # Short content needs smaller chunks
            chunk_size = 200
            chunk_overlap = 40
        else:
            # Default values
            chunk_size = self.chunk_size
            chunk_overlap = self.chunk_overlap
        
        # Adjust based on content length
        if content_length < 1000:
            # Very short content - use smaller chunks
            chunk_size = min(chunk_size, 250)
            chunk_overlap = min(chunk_overlap, 50)
        elif content_length > 10000:
            # Very long content - use larger chunks for efficiency
            chunk_size = min(chunk_size + 200, 800)
            chunk_overlap = min(chunk_overlap + 40, 160)
        
        return chunk_size, chunk_overlap
    
    def process_content_item(self, content: Content, org_id: str, force_rechunk: bool = False) -> Dict[str, Any]:
        """
        Process a single content item with optimized chunking and error handling.
        
        Args:
            content: Content object to process
            org_id: Organization ID
            force_rechunk: Force re-chunking even if chunks exist
            
        Returns:
            Processing results dictionary
        """
        result = {
            'content_id': content.id,
            'success': False,
            'chunks_created': 0,
            'embeddings_generated': 0,
            'error': None,
            'processing_time': 0
        }
        
        start_time = time.time()
        
        try:
            # Check if already processed
            existing_chunks = self.session.query(ContentChunk).filter(
                and_(
                    ContentChunk.content_id == content.id,
                    ContentChunk.org_id == org_id
                )
            ).count()
            
            if existing_chunks > 0 and not force_rechunk:
                logger.info(f"Content {content.id} already has {existing_chunks} chunks")
                result['chunks_created'] = existing_chunks
                result['success'] = True
                return result
            
            # Delete existing chunks if force rechunking
            if existing_chunks > 0 and force_rechunk:
                self.session.query(ContentChunk).filter(
                    and_(
                        ContentChunk.content_id == content.id,
                        ContentChunk.org_id == org_id
                    )
                ).delete()
                self.session.commit()
                logger.info(f"Deleted {existing_chunks} existing chunks for content {content.id}")
            
            # Optimize chunking strategy
            chunk_size, chunk_overlap = self.optimize_chunking_strategy(
                content.content_type or 'default',
                len(content.text)
            )
            
            # Create optimized chunker for this content
            content_chunker = ContentChunker(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                respect_sentences=True
            )
            
            # Prepare content for chunking
            content_data = {
                "content_id": content.id,
                "url": content.url,
                "domain": content.domain,
                "text": content.text,
                "metadata": {
                    "title": content.title,
                    "content_type": content.content_type,
                    "author": content.author,
                    "publication_date": content.publication_date,
                    "last_modified": content.last_modified,
                    "categories": content.categories or [],
                    "tags": content.tags or [],
                    "language": content.language
                },
                "crawl_id": content.crawl_id,
                "extracted_at": content.extracted_at
            }
            
            # Generate chunks
            chunks = content_chunker.process_content(content_data)
            
            if not chunks:
                result['error'] = "No chunks generated"
                return result
            
            # Generate embeddings in batches
            embedding_model = self._get_embedding_model()
            chunks_processed = 0
            
            for i in range(0, len(chunks), self.batch_size):
                batch = chunks[i:i + self.batch_size]
                
                try:
                    # Extract text for embedding generation
                    texts = [chunk["text"] for chunk in batch]
                    
                    # Generate embeddings
                    embeddings = embedding_model.encode(texts, show_progress_bar=False)
                    
                    # Add embeddings to chunks
                    for j, embedding in enumerate(embeddings):
                        batch[j]["embedding"] = embedding.tolist()
                    
                    # Store chunks in database
                    self.db.store_content_chunks(batch, org_id)
                    chunks_processed += len(batch)
                    
                    logger.debug(f"Processed batch {i//self.batch_size + 1} for content {content.id}")
                    
                except Exception as e:
                    logger.error(f"Error processing batch {i//self.batch_size + 1} for content {content.id}: {e}")
                    # Continue with next batch rather than failing completely
                    continue
            
            # Mark content as processed
            content.is_processed = True
            self.session.commit()
            
            result['success'] = True
            result['chunks_created'] = len(chunks)
            result['embeddings_generated'] = chunks_processed
            
            logger.info(f"Successfully processed content {content.id}: {len(chunks)} chunks, {chunks_processed} embeddings")
            
        except Exception as e:
            logger.error(f"Error processing content {content.id}: {e}")
            result['error'] = str(e)
            self.session.rollback()
        
        result['processing_time'] = time.time() - start_time
        return result
    
    def process_unprocessed_content(self, org_id: str, max_items: Optional[int] = None) -> Dict[str, Any]:
        """
        Process all unprocessed content items.
        
        Args:
            org_id: Organization ID
            max_items: Maximum number of items to process (None for all)
            
        Returns:
            Processing results summary
        """
        self._initialize_services()
        
        try:
            # Get unprocessed content
            query = self.session.query(Content).filter(
                and_(
                    Content.org_id == org_id,
                    or_(
                        Content.is_processed == False,
                        Content.is_processed.is_(None)
                    )
                )
            ).order_by(Content.extracted_at.desc())
            
            if max_items:
                query = query.limit(max_items)
            
            unprocessed_content = query.all()
            
            if not unprocessed_content:
                logger.info("No unprocessed content found")
                return {
                    'success': True,
                    'content_processed': 0,
                    'total_chunks': 0,
                    'total_embeddings': 0,
                    'errors': [],
                    'processing_time': 0
                }
            
            logger.info(f"Processing {len(unprocessed_content)} unprocessed content items")
            
            # Process content items
            results = []
            total_chunks = 0
            total_embeddings = 0
            errors = []
            
            start_time = time.time()
            
            for i, content in enumerate(unprocessed_content):
                logger.info(f"Processing {i+1}/{len(unprocessed_content)}: {content.title[:50] if content.title else content.url}")
                
                result = self.process_content_item(content, org_id)
                results.append(result)
                
                if result['success']:
                    total_chunks += result['chunks_created']
                    total_embeddings += result['embeddings_generated']
                else:
                    errors.append({
                        'content_id': content.id,
                        'url': content.url,
                        'error': result['error']
                    })
                
                # Brief pause to avoid overwhelming the system
                time.sleep(0.1)
            
            processing_time = time.time() - start_time
            
            # Update stats
            self.stats['content_processed'] += len([r for r in results if r['success']])
            self.stats['chunks_created'] += total_chunks
            self.stats['embeddings_generated'] += total_embeddings
            self.stats['errors'] += len(errors)
            
            return {
                'success': len(errors) == 0,
                'content_processed': len([r for r in results if r['success']]),
                'total_chunks': total_chunks,
                'total_embeddings': total_embeddings,
                'errors': errors,
                'processing_time': processing_time,
                'detailed_results': results
            }
            
        except Exception as e:
            logger.error(f"Error processing unprocessed content: {e}")
            return {
                'success': False,
                'error': str(e),
                'content_processed': 0,
                'total_chunks': 0,
                'total_embeddings': 0
            }
    
    def generate_missing_embeddings(self, org_id: str, max_chunks: Optional[int] = None) -> Dict[str, Any]:
        """
        Generate embeddings for chunks that don't have them.
        
        Args:
            org_id: Organization ID
            max_chunks: Maximum number of chunks to process (None for all)
            
        Returns:
            Processing results
        """
        self._initialize_services()
        
        try:
            # Get chunks without embeddings
            query = self.session.query(ContentChunk).filter(
                and_(
                    ContentChunk.org_id == org_id,
                    ContentChunk.embedding.is_(None)
                )
            ).order_by(ContentChunk.id)
            
            if max_chunks:
                query = query.limit(max_chunks)
            
            chunks_without_embeddings = query.all()
            
            if not chunks_without_embeddings:
                logger.info("All chunks already have embeddings")
                return {
                    'success': True,
                    'embeddings_generated': 0,
                    'errors': [],
                    'processing_time': 0
                }
            
            logger.info(f"Generating embeddings for {len(chunks_without_embeddings)} chunks")
            
            # Get embedding model
            embedding_model = self._get_embedding_model()
            
            # Process in batches
            embeddings_generated = 0
            errors = []
            start_time = time.time()
            
            for i in range(0, len(chunks_without_embeddings), self.batch_size):
                batch = chunks_without_embeddings[i:i + self.batch_size]
                
                try:
                    # Extract texts
                    texts = [chunk.text for chunk in batch]
                    
                    # Generate embeddings
                    embeddings = embedding_model.encode(texts, show_progress_bar=False)
                    
                    # Update chunks
                    for j, embedding in enumerate(embeddings):
                        batch[j].embedding = embedding.tolist()
                    
                    # Commit batch
                    self.session.commit()
                    embeddings_generated += len(batch)
                    
                    logger.info(f"Generated embeddings for batch {i//self.batch_size + 1}/{(len(chunks_without_embeddings) + self.batch_size - 1)//self.batch_size}")
                    
                except Exception as e:
                    logger.error(f"Error generating embeddings for batch {i//self.batch_size + 1}: {e}")
                    errors.append(f"Batch {i//self.batch_size + 1}: {str(e)}")
                    self.session.rollback()
                    continue
            
            processing_time = time.time() - start_time
            
            # Update stats
            self.stats['embeddings_generated'] += embeddings_generated
            self.stats['errors'] += len(errors)
            
            return {
                'success': len(errors) == 0,
                'embeddings_generated': embeddings_generated,
                'errors': errors,
                'processing_time': processing_time
            }
            
        except Exception as e:
            logger.error(f"Error generating missing embeddings: {e}")
            return {
                'success': False,
                'error': str(e),
                'embeddings_generated': 0
            }
    
    def validate_rag_readiness(self, org_id: str) -> Dict[str, Any]:
        """
        Validate that the RAG system is ready for use.
        
        Args:
            org_id: Organization ID
            
        Returns:
            Validation results
        """
        self._initialize_services()
        
        validation_results = {
            'ready': False,
            'issues': [],
            'recommendations': [],
            'stats': {}
        }
        
        try:
            stats = self.get_processing_statistics(org_id)
            validation_results['stats'] = stats
            
            # Check for content
            if stats['content_stats']['total_content'] == 0:
                validation_results['issues'].append("No content found")
                validation_results['recommendations'].append("Crawl some websites to add content")
                return validation_results
            
            # Check chunk coverage
            if stats['content_stats']['content_without_chunks'] > 0:
                validation_results['issues'].append(f"{stats['content_stats']['content_without_chunks']} content items need chunking")
                validation_results['recommendations'].append("Run content processing to create chunks")
            
            # Check embedding coverage
            if stats['chunk_stats']['chunks_without_embeddings'] > 0:
                validation_results['issues'].append(f"{stats['chunk_stats']['chunks_without_embeddings']} chunks need embeddings")
                validation_results['recommendations'].append("Run embedding generation to create embeddings")
            
            # Check embedding coverage percentage
            embedding_coverage = float(stats['chunk_stats']['embedding_coverage'].replace('%', ''))
            if embedding_coverage < 80:
                validation_results['issues'].append(f"Low embedding coverage: {stats['chunk_stats']['embedding_coverage']}")
                validation_results['recommendations'].append("Improve embedding coverage to at least 80%")
            
            # Test vector search capability
            try:
                test_chunks = self.session.query(ContentChunk).filter(
                    and_(
                        ContentChunk.org_id == org_id,
                        ContentChunk.embedding.isnot(None)
                    )
                ).limit(1).all()
                
                if not test_chunks:
                    validation_results['issues'].append("No chunks with embeddings found for testing")
                else:
                    # Test worked
                    validation_results['vector_search_working'] = True
                    
            except Exception as e:
                validation_results['issues'].append(f"Vector search test failed: {str(e)}")
                validation_results['recommendations'].append("Check database configuration and vector extensions")
            
            # Determine readiness
            validation_results['ready'] = len(validation_results['issues']) == 0
            
            if validation_results['ready']:
                validation_results['message'] = "RAG system is ready for use!"
            else:
                validation_results['message'] = f"RAG system has {len(validation_results['issues'])} issues to resolve"
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating RAG readiness: {e}")
            validation_results['issues'].append(f"Validation error: {str(e)}")
            return validation_results
    
    def run_full_optimization(self, org_id: str, max_content: Optional[int] = None) -> Dict[str, Any]:
        """
        Run the complete optimization pipeline.
        
        Args:
            org_id: Organization ID
            max_content: Maximum content items to process (None for all)
            
        Returns:
            Complete optimization results
        """
        logger.info("🚀 Starting Optimized Content Processing Pipeline")
        logger.info("=" * 60)
        
        self.stats['start_time'] = time.time()
        
        # Step 1: Get initial statistics
        logger.info("\n📊 Step 1: Getting initial statistics...")
        initial_stats = self.get_processing_statistics(org_id)
        
        if not initial_stats:
            return {'success': False, 'error': 'Failed to get initial statistics'}
        
        logger.info(f"   📄 Total content: {initial_stats['content_stats']['total_content']}")
        logger.info(f"   🧩 Total chunks: {initial_stats['chunk_stats']['total_chunks']}")
        logger.info(f"   🎯 Embedding coverage: {initial_stats['chunk_stats']['embedding_coverage']}")
        logger.info(f"   🌐 Domains: {', '.join(initial_stats['domain_stats']['domains'][:3])}{'...' if len(initial_stats['domain_stats']['domains']) > 3 else ''}")
        
        if initial_stats['content_stats']['total_content'] == 0:
            logger.warning("⚠️ No content found. Please crawl some websites first.")
            return {'success': False, 'error': 'No content to process'}
        
        # Step 2: Process unprocessed content
        logger.info("\n🔄 Step 2: Processing unprocessed content...")
        processing_results = self.process_unprocessed_content(org_id, max_content)
        
        if processing_results['success']:
            logger.info(f"   ✅ Processed {processing_results['content_processed']} content items")
            logger.info(f"   ✅ Created {processing_results['total_chunks']} chunks")
            logger.info(f"   ✅ Generated {processing_results['total_embeddings']} embeddings")
        else:
            logger.warning(f"   ⚠️ Processing completed with {len(processing_results.get('errors', []))} errors")
            for error in processing_results.get('errors', [])[:3]:  # Show first 3 errors
                logger.warning(f"     - {error['url']}: {error['error']}")
        
        # Step 3: Generate missing embeddings
        logger.info("\n🎯 Step 3: Generating missing embeddings...")
        embedding_results = self.generate_missing_embeddings(org_id)
        
        if embedding_results['success']:
            logger.info(f"   ✅ Generated {embedding_results['embeddings_generated']} embeddings")
        else:
            logger.warning(f"   ⚠️ Embedding generation had {len(embedding_results.get('errors', []))} errors")
        
        # Step 4: Get final statistics
        logger.info("\n📈 Step 4: Getting final statistics...")
        final_stats = self.get_processing_statistics(org_id)
        
        logger.info(f"   📄 Total content: {final_stats['content_stats']['total_content']}")
        logger.info(f"   🧩 Total chunks: {final_stats['chunk_stats']['total_chunks']}")
        logger.info(f"   🎯 Embedding coverage: {final_stats['chunk_stats']['embedding_coverage']}")
        
        # Step 5: Validate RAG readiness
        logger.info("\n🔍 Step 5: Validating RAG readiness...")
        validation = self.validate_rag_readiness(org_id)
        
        if validation['ready']:
            logger.info("   ✅ RAG system is ready for use!")
        else:
            logger.warning("   ⚠️ RAG system has issues:")
            for issue in validation['issues']:
                logger.warning(f"     - {issue}")
            
            logger.info("   💡 Recommendations:")
            for rec in validation['recommendations']:
                logger.info(f"     - {rec}")
        
        # Calculate improvements
        content_improvement = (final_stats['content_stats']['processed_content'] - 
                              initial_stats['content_stats']['processed_content'])
        chunk_improvement = (final_stats['chunk_stats']['total_chunks'] - 
                           initial_stats['chunk_stats']['total_chunks'])
        embedding_improvement = (final_stats['chunk_stats']['chunks_with_embeddings'] - 
                               initial_stats['chunk_stats']['chunks_with_embeddings'])
        
        self.stats['end_time'] = time.time()
        total_time = self.stats['end_time'] - self.stats['start_time']
        
        # Final summary
        logger.info(f"\n🎉 Optimization Complete!")
        logger.info(f"   ⏱️  Total time: {total_time:.2f} seconds")
        logger.info(f"   📈 Content processed: +{content_improvement}")
        logger.info(f"   📈 Chunks created: +{chunk_improvement}")
        logger.info(f"   📈 Embeddings generated: +{embedding_improvement}")
        logger.info(f"   📊 Final embedding coverage: {final_stats['chunk_stats']['embedding_coverage']}")
        
        if validation['ready']:
            logger.info(f"\n🚀 Ready for RAG operations!")
            logger.info(f"   🔍 Test search: python -c \"from processor.rag_service import RAGService; from database.db import Database; from database.session import get_db_session; session = next(get_db_session()); db = Database(session); rag = RAGService(db); print(rag.search_chunks('your query here', org_id='{org_id}'))\"")
        else:
            logger.info(f"\n🔧 Next steps to complete setup:")  
            for rec in validation['recommendations']:
                logger.info(f"   - {rec}")
        
        return {
            'success': validation['ready'],
            'initial_stats': initial_stats,
            'final_stats': final_stats,
            'processing_results': processing_results,
            'embedding_results': embedding_results,
            'validation': validation,
            'improvements': {
                'content_processed': content_improvement,
                'chunks_created': chunk_improvement,
                'embeddings_generated': embedding_improvement
            },
            'performance': {
                'total_time': total_time,
                'content_per_second': content_improvement / total_time if total_time > 0 else 0,
                'embeddings_per_second': embedding_improvement / total_time if total_time > 0 else 0
            }
        }
    
    def __del__(self):
        """Clean up database session."""
        if self.session:
            self.session.close()

def main():
    """Main execution function with CLI interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Optimized Content Processing Pipeline for VoiceForge RAG')
    parser.add_argument('--org-id', required=True, help='Organization ID for multi-tenant processing')
    parser.add_argument('--chunk-size', type=int, default=400, help='Target chunk size in tokens')
    parser.add_argument('--chunk-overlap', type=int, default=80, help='Chunk overlap in tokens')
    parser.add_argument('--batch-size', type=int, default=32, help='Batch size for embedding generation')
    parser.add_argument('--max-content', type=int, help='Maximum content items to process')
    parser.add_argument('--stats-only', action='store_true', help='Only show statistics without processing')
    parser.add_argument('--validate-only', action='store_true', help='Only validate RAG readiness')
    parser.add_argument('--embeddings-only', action='store_true', help='Only generate missing embeddings')
    
    args = parser.parse_args()
    
    try:
        processor = OptimizedContentProcessor(
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
            batch_size=args.batch_size
        )
        
        if args.stats_only:
            logger.info("📊 Getting processing statistics...")
            stats = processor.get_processing_statistics(args.org_id)
            print(json.dumps(stats, indent=2, default=str))
            
        elif args.validate_only:
            logger.info("🔍 Validating RAG readiness...")
            validation = processor.validate_rag_readiness(args.org_id)
            print(json.dumps(validation, indent=2, default=str))
            
        elif args.embeddings_only:
            logger.info("🎯 Generating missing embeddings only...")
            results = processor.generate_missing_embeddings(args.org_id)
            print(json.dumps(results, indent=2, default=str))
            
        else:
            # Run full optimization
            results = processor.run_full_optimization(args.org_id, args.max_content)
            
            # Output final results as JSON for potential automation
            if results['success']:
                logger.info("\n✅ Pipeline completed successfully!")
            else:
                logger.error("\n❌ Pipeline completed with issues")
            
            print("\n" + "="*50)
            print("FINAL RESULTS (JSON):")
            print(json.dumps({
                'success': results['success'],
                'improvements': results['improvements'],
                'performance': results['performance'],
                'ready_for_rag': results['validation']['ready']
            }, indent=2))
    
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
