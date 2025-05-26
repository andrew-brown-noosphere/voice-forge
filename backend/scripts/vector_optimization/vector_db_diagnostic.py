#!/usr/bin/env python3
"""
Vector Database Diagnostic Script for VoiceForge RAG System

This script analyzes your current vector database setup and provides:
1. Configuration analysis
2. Performance metrics
3. Data quality assessment
4. Optimization recommendations

Run this script to understand your vector DB state before optimization.
"""

import os
import sys
import time
import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

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

class VectorDBDiagnostic:
    """Comprehensive vector database diagnostic tool."""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "configuration": {},
            "database_health": {},
            "performance_metrics": {},
            "data_quality": {},
            "recommendations": [],
            "next_steps": []
        }
        
    def run_full_diagnostic(self) -> Dict[str, Any]:
        """Run complete diagnostic suite."""
        print("🔍 Starting Vector Database Diagnostic...")
        print("=" * 60)
        
        # Check configuration
        self._check_configuration()
        
        # Check database health
        self._check_database_health()
        
        # Test performance
        self._test_performance()
        
        # Analyze data quality
        self._analyze_data_quality()
        
        # Generate recommendations
        self._generate_recommendations()
        
        # Print summary
        self._print_summary()
        
        return self.results
    
    def _check_configuration(self):
        """Check current vector database configuration."""
        print("\n📋 Configuration Analysis")
        print("-" * 30)
        
        config = {}
        
        # Check environment variables
        vector_provider = os.environ.get('VECTOR_DB_PROVIDER', 'database')
        config['vector_provider'] = vector_provider
        print(f"Vector DB Provider: {vector_provider}")
        
        # Check API keys
        openai_key = os.environ.get('OPENAI_API_KEY')
        config['has_openai_key'] = bool(openai_key)
        print(f"OpenAI API Key: {'✅ Set' if openai_key else '❌ Missing'}")
        
        anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
        config['has_anthropic_key'] = bool(anthropic_key)
        print(f"Anthropic API Key: {'✅ Set' if anthropic_key else '⚠️  Not Set (Optional)'}")
        
        # Check Pinecone configuration
        if vector_provider.lower() == 'pinecone':
            pinecone_key = os.environ.get('PINECONE_API_KEY')
            pinecone_env = os.environ.get('PINECONE_ENVIRONMENT')
            pinecone_index = os.environ.get('PINECONE_INDEX_NAME')
            
            config['pinecone'] = {
                'has_api_key': bool(pinecone_key),
                'environment': pinecone_env,
                'index_name': pinecone_index
            }
            
            print(f"Pinecone API Key: {'✅ Set' if pinecone_key else '❌ Missing'}")
            print(f"Pinecone Environment: {pinecone_env or '❌ Not Set'}")
            print(f"Pinecone Index: {pinecone_index or '❌ Not Set'}")
        
        # Check PostgreSQL configuration
        try:
            from database.session import get_db_session
            from sqlalchemy import text
            
            with get_db_session() as session:
                # Test basic database connection
                result = session.execute(text("SELECT 1")).fetchone()
                config['postgres_connection'] = True
                print("PostgreSQL Connection: ✅ Working")
                
                # Check for pgvector extension
                try:
                    result = session.execute(text("SELECT 1 FROM pg_extension WHERE extname = 'vector'")).fetchone()
                    config['pgvector_installed'] = bool(result)
                    print(f"pgvector Extension: {'✅ Installed' if result else '❌ Not Installed'}")
                except Exception as e:
                    config['pgvector_installed'] = False
                    print(f"pgvector Extension: ❌ Error checking ({str(e)[:50]}...)")
                
        except Exception as e:
            config['postgres_connection'] = False
            config['pgvector_installed'] = False
            print(f"PostgreSQL Connection: ❌ Failed ({str(e)[:50]}...)")
        
        self.results['configuration'] = config
    
    def _check_database_health(self):
        """Check database health and table status."""
        print("\n🏥 Database Health Check")
        print("-" * 30)
        
        health = {}
        
        try:
            from database.session import get_db_session
            from database.models import Content, ContentChunk, MarketingTemplate
            
            with get_db_session() as session:
                # Count records in each table
                content_count = session.query(Content).count()
                chunk_count = session.query(ContentChunk).count()
                template_count = session.query(MarketingTemplate).count()
                
                health['content_count'] = content_count
                health['chunk_count'] = chunk_count
                health['template_count'] = template_count
                
                print(f"Content Records: {content_count}")
                print(f"Content Chunks: {chunk_count}")
                print(f"Templates: {template_count}")
                
                # Check for embeddings
                content_with_embeddings = session.query(Content).filter(Content.embedding.isnot(None)).count()
                chunks_with_embeddings = session.query(ContentChunk).filter(ContentChunk.embedding.isnot(None)).count()
                
                health['content_with_embeddings'] = content_with_embeddings
                health['chunks_with_embeddings'] = chunks_with_embeddings
                
                content_embedding_ratio = (content_with_embeddings / content_count * 100) if content_count > 0 else 0
                chunk_embedding_ratio = (chunks_with_embeddings / chunk_count * 100) if chunk_count > 0 else 0
                
                print(f"Content with Embeddings: {content_with_embeddings}/{content_count} ({content_embedding_ratio:.1f}%)")
                print(f"Chunks with Embeddings: {chunks_with_embeddings}/{chunk_count} ({chunk_embedding_ratio:.1f}%)")
                
                health['content_embedding_ratio'] = content_embedding_ratio
                health['chunk_embedding_ratio'] = chunk_embedding_ratio
                
                # Check domains
                domains = session.query(Content.domain).distinct().all()
                health['domains'] = [d[0] for d in domains]
                print(f"Domains: {len(health['domains'])} ({', '.join(health['domains'][:3])}{'...' if len(health['domains']) > 3 else ''})")
                
        except Exception as e:
            health['error'] = str(e)
            print(f"❌ Database health check failed: {str(e)}")
        
        self.results['database_health'] = health
    
    def _test_performance(self):
        """Test vector search performance."""
        print("\n⚡ Performance Testing")
        print("-" * 30)
        
        metrics = {}
        
        try:
            from database.session import get_db_session
            from database.db import Database
            from processor.embeddings.embedding_service import EmbeddingService
            
            # Initialize services
            embedding_service = EmbeddingService()
            
            # Test embedding generation
            test_text = "This is a test query for performance evaluation of the vector database system."
            
            start_time = time.time()
            test_embedding = embedding_service.generate_embedding(test_text)
            embedding_time = time.time() - start_time
            
            metrics['embedding_generation_time'] = embedding_time
            print(f"Embedding Generation: {embedding_time:.3f}s")
            
            if test_embedding:
                with get_db_session() as session:
                    db = Database(session)
                    
                    # Test chunk search performance
                    start_time = time.time()
                    chunk_results = db.search_chunks_by_vector(
                        query_embedding=test_embedding,
                        top_k=5
                    )
                    chunk_search_time = time.time() - start_time
                    
                    metrics['chunk_search_time'] = chunk_search_time
                    metrics['chunk_results_count'] = len(chunk_results)
                    print(f"Chunk Vector Search: {chunk_search_time:.3f}s ({len(chunk_results)} results)")
                    
                    # Test content search performance
                    start_time = time.time()
                    content_results = db.search_content_by_vector(
                        query_embedding=test_embedding,
                        limit=5
                    )
                    content_search_time = time.time() - start_time
                    
                    metrics['content_search_time'] = content_search_time
                    metrics['content_results_count'] = len(content_results)
                    print(f"Content Vector Search: {content_search_time:.3f}s ({len(content_results)} results)")
                    
                    # Test text search fallback
                    start_time = time.time()
                    text_results = db.search_chunks_by_text(
                        query="test query performance",
                        top_k=5
                    )
                    text_search_time = time.time() - start_time
                    
                    metrics['text_search_time'] = text_search_time
                    metrics['text_results_count'] = len(text_results)
                    print(f"Text Search Fallback: {text_search_time:.3f}s ({len(text_results)} results)")
            else:
                print("❌ Could not generate test embedding")
                metrics['embedding_error'] = "Failed to generate test embedding"
                
        except Exception as e:
            metrics['error'] = str(e)
            print(f"❌ Performance test failed: {str(e)}")
        
        self.results['performance_metrics'] = metrics
    
    def _analyze_data_quality(self):
        """Analyze the quality of stored data."""
        print("\n📊 Data Quality Analysis")
        print("-" * 30)
        
        quality = {}
        
        try:
            from database.session import get_db_session
            from database.models import Content, ContentChunk
            
            with get_db_session() as session:
                # Analyze content quality
                content_stats = session.query(
                    Content.domain,
                    Content.content_type,
                    Content.is_processed
                ).all()
                
                # Group by domain and processing status
                domain_stats = {}
                for domain, content_type, is_processed in content_stats:
                    if domain not in domain_stats:
                        domain_stats[domain] = {'total': 0, 'processed': 0, 'types': set()}
                    
                    domain_stats[domain]['total'] += 1
                    if is_processed:
                        domain_stats[domain]['processed'] += 1
                    domain_stats[domain]['types'].add(content_type)
                
                # Convert sets to lists for JSON serialization
                for domain in domain_stats:
                    domain_stats[domain]['types'] = list(domain_stats[domain]['types'])
                    processing_ratio = (domain_stats[domain]['processed'] / domain_stats[domain]['total'] * 100)
                    domain_stats[domain]['processing_ratio'] = processing_ratio
                
                quality['domain_stats'] = domain_stats
                
                for domain, stats in domain_stats.items():
                    print(f"Domain {domain}: {stats['total']} content, {stats['processed']} processed ({stats['processing_ratio']:.1f}%)")
                
                # Analyze chunk quality
                if session.query(ContentChunk).count() > 0:
                    # Check chunk size distribution using SQLAlchemy expressions
                    from sqlalchemy import func
                    chunk_sizes = session.query(
                        (ContentChunk.end_char - ContentChunk.start_char).label('size')
                    ).all()
                    
                    sizes = [size[0] for size in chunk_sizes]
                    if sizes:
                        quality['chunk_stats'] = {
                            'count': len(sizes),
                            'avg_size': sum(sizes) / len(sizes),
                            'min_size': min(sizes),
                            'max_size': max(sizes)
                        }
                        
                        print(f"Chunk Statistics:")
                        print(f"  Average Size: {quality['chunk_stats']['avg_size']:.0f} characters")
                        print(f"  Size Range: {quality['chunk_stats']['min_size']} - {quality['chunk_stats']['max_size']} characters")
                else:
                    quality['chunk_stats'] = {'count': 0}
                    print("No content chunks found")
                
        except Exception as e:
            quality['error'] = str(e)
            print(f"❌ Data quality analysis failed: {str(e)}")
        
        self.results['data_quality'] = quality
    
    def _generate_recommendations(self):
        """Generate optimization recommendations based on diagnostic results."""
        print("\n💡 Optimization Recommendations")
        print("-" * 30)
        
        recommendations = []
        next_steps = []
        
        config = self.results.get('configuration', {})
        health = self.results.get('database_health', {})
        metrics = self.results.get('performance_metrics', {})
        quality = self.results.get('data_quality', {})
        
        # Configuration recommendations
        if not config.get('pgvector_installed', False):
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Configuration',
                'issue': 'pgvector extension not installed',
                'solution': 'Install pgvector extension for optimal vector search performance',
                'command': 'sudo -u postgres psql -c "CREATE EXTENSION IF NOT EXISTS vector;"'
            })
            next_steps.append("Install pgvector extension in PostgreSQL")
        
        if config.get('vector_provider') == 'pinecone' and not config.get('pinecone', {}).get('has_api_key'):
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Configuration',
                'issue': 'Pinecone configured but API key missing',
                'solution': 'Add PINECONE_API_KEY to .env file or switch to pgvector',
                'command': 'echo "PINECONE_API_KEY=your-key-here" >> .env'
            })
            next_steps.append("Configure Pinecone API key or switch to pgvector")
        
        # Data quality recommendations
        content_embedding_ratio = health.get('content_embedding_ratio', 0)
        chunk_embedding_ratio = health.get('chunk_embedding_ratio', 0)
        
        if content_embedding_ratio < 80:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Data Quality',
                'issue': f'Only {content_embedding_ratio:.1f}% of content has embeddings',
                'solution': 'Process existing content to generate embeddings',
                'command': 'python scripts/process_content_for_rag.py'
            })
            next_steps.append("Generate embeddings for existing content")
        
        if chunk_embedding_ratio < 80 and health.get('chunk_count', 0) > 0:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Data Quality',
                'issue': f'Only {chunk_embedding_ratio:.1f}% of chunks have embeddings',
                'solution': 'Process content chunks to generate embeddings',
                'command': 'python scripts/vector_optimization/optimize_embeddings.py'
            })
            next_steps.append("Generate embeddings for content chunks")
        
        # Performance recommendations
        if metrics.get('chunk_search_time', 0) > 1.0:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Performance',
                'issue': f'Slow chunk search ({metrics.get("chunk_search_time", 0):.3f}s)',
                'solution': 'Optimize database indexes and consider vector-specific optimizations',
                'command': 'python scripts/vector_optimization/optimize_indexes.py'
            })
            next_steps.append("Optimize database indexes for vector search")
        
        # Architecture recommendations
        if health.get('chunk_count', 0) == 0 and health.get('content_count', 0) > 0:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Architecture',
                'issue': 'No content chunks found but content exists',
                'solution': 'Implement content chunking for better RAG performance',
                'command': 'python scripts/vector_optimization/chunk_existing_content.py'
            })
            next_steps.append("Chunk existing content for RAG system")
        
        # Strategic recommendations
        if config.get('vector_provider') == 'database' and not config.get('pgvector_installed'):
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Strategy',
                'issue': 'Using database without pgvector - suboptimal performance',
                'solution': 'Choose between pgvector (local) or Pinecone (cloud) for vector operations',
                'details': 'pgvector: Better for development, lower latency. Pinecone: Better for production, more features.'
            })
            next_steps.append("Choose and implement optimal vector database strategy")
        
        # Sort recommendations by priority
        priority_order = {'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 0), reverse=True)
        
        for i, rec in enumerate(recommendations, 1):
            priority_emoji = {'HIGH': '🔥', 'MEDIUM': '⚠️', 'LOW': '💡'}
            print(f"{i}. {priority_emoji.get(rec['priority'], '📌')} [{rec['priority']}] {rec['category']}")
            print(f"   Issue: {rec['issue']}")
            print(f"   Solution: {rec['solution']}")
            if 'command' in rec:
                print(f"   Command: {rec['command']}")
            if 'details' in rec:
                print(f"   Details: {rec['details']}")
            print()
        
        self.results['recommendations'] = recommendations
        self.results['next_steps'] = next_steps
    
    def _print_summary(self):
        """Print diagnostic summary."""
        print("\n📋 Diagnostic Summary")
        print("=" * 60)
        
        config = self.results.get('configuration', {})
        health = self.results.get('database_health', {})
        recommendations = self.results.get('recommendations', [])
        
        # Overall health score
        score = 0
        max_score = 100
        
        # Configuration score (30 points)
        if config.get('postgres_connection'):
            score += 10
        if config.get('has_openai_key'):
            score += 10
        if config.get('pgvector_installed') or (config.get('vector_provider') == 'pinecone' and config.get('pinecone', {}).get('has_api_key')):
            score += 10
        
        # Data score (40 points)
        content_count = health.get('content_count', 0)
        chunk_count = health.get('chunk_count', 0)
        if content_count > 0:
            score += 10
        if chunk_count > 0:
            score += 10
        
        content_embedding_ratio = health.get('content_embedding_ratio', 0)
        chunk_embedding_ratio = health.get('chunk_embedding_ratio', 0)
        score += min(10, content_embedding_ratio / 10)
        score += min(10, chunk_embedding_ratio / 10)
        
        # Performance score (30 points)
        metrics = self.results.get('performance_metrics', {})
        if not metrics.get('error'):
            score += 10
        
        chunk_search_time = metrics.get('chunk_search_time', float('inf'))
        if chunk_search_time < 0.1:
            score += 20
        elif chunk_search_time < 0.5:
            score += 15
        elif chunk_search_time < 1.0:
            score += 10
        elif chunk_search_time < 2.0:
            score += 5
        
        # Determine health status
        if score >= 80:
            status = "🟢 EXCELLENT"
        elif score >= 60:
            status = "🟡 GOOD"
        elif score >= 40:
            status = "🟠 NEEDS IMPROVEMENT"
        else:
            status = "🔴 CRITICAL"
        
        print(f"Overall Health Score: {score:.0f}/100 - {status}")
        print()
        
        # Priority recommendations
        high_priority = [r for r in recommendations if r['priority'] == 'HIGH']
        if high_priority:
            print(f"🔥 {len(high_priority)} high-priority issues to address")
        
        # Next steps summary
        next_steps = self.results.get('next_steps', [])
        if next_steps:
            print("\n🎯 Immediate Next Steps:")
            for i, step in enumerate(next_steps[:3], 1):
                print(f"   {i}. {step}")
            if len(next_steps) > 3:
                print(f"   ... and {len(next_steps) - 3} more")
        
        print(f"\n📊 System Overview:")
        print(f"   • Vector Provider: {config.get('vector_provider', 'unknown')}")
        print(f"   • Content Records: {health.get('content_count', 0)}")
        print(f"   • Content Chunks: {health.get('chunk_count', 0)}")
        print(f"   • Domains: {len(health.get('domains', []))}")
        
        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"vector_diagnostic_{timestamp}.json"
        
        try:
            with open(output_file, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            print(f"\n💾 Detailed results saved to: {output_file}")
        except Exception as e:
            print(f"\n❌ Could not save results: {str(e)}")

def main():
    """Main function to run the diagnostic."""
    try:
        diagnostic = VectorDBDiagnostic()
        results = diagnostic.run_full_diagnostic()
        
        print("\n" + "=" * 60)
        print("🏁 Diagnostic Complete!")
        print("\nTo optimize your vector database:")
        print("1. Address high-priority recommendations first")
        print("2. Run the optimization scripts mentioned above")
        print("3. Re-run this diagnostic to measure improvements")
        print("\nFor detailed optimization guides, check:")
        print("   - scripts/vector_optimization/postgresql_optimization.py")
        print("   - scripts/vector_optimization/pinecone_optimization.py")
        
        return results
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Diagnostic interrupted by user")
        return None
    except Exception as e:
        print(f"\n❌ Diagnostic failed: {str(e)}")
        logger.exception("Diagnostic failed")
        return None

if __name__ == "__main__":
    main()
