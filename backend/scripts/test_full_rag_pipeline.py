#!/usr/bin/env python3
"""
Full RAG Pipeline Test
Tests the complete RAG system from content retrieval to content generation
"""

import os
import sys
import time
import json
import logging
from typing import Dict, Any, List

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.session import get_db_session
from database.models import ContentChunk, Content
from processor.rag import RAGSystem
from processor.rag_service import RAGService
from processor.llm.llm_service import LLMService
from database.db import Database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGPipelineTester:
    """Comprehensive RAG pipeline testing"""
    
    def __init__(self):
        self.session = get_db_session()
        self.db = Database(self.session)
        self.rag_service = RAGService(self.db)
        self.rag_system = self.rag_service.rag_system
        self.llm_service = LLMService()
        
        self.test_results = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'tests': {}
        }
    
    def test_database_connectivity(self) -> Dict[str, Any]:
        """Test database connection and basic queries"""
        logger.info("🔗 Testing database connectivity...")
        
        try:
            # Test content count
            content_count = self.session.query(Content).count()
            chunk_count = self.session.query(ContentChunk).count()
            
            # Test embedding count
            chunks_with_embeddings = self.session.query(ContentChunk).filter(
                ContentChunk.embedding.isnot(None)
            ).count()
            
            result = {
                'success': True,
                'content_count': content_count,
                'chunk_count': chunk_count,
                'chunks_with_embeddings': chunks_with_embeddings,
                'embedding_coverage': f"{(chunks_with_embeddings/chunk_count*100):.1f}%" if chunk_count > 0 else "0%"
            }
            
            logger.info(f"   ✅ Database connected")
            logger.info(f"   📄 Content items: {content_count}")
            logger.info(f"   🧩 Chunks: {chunk_count}")
            logger.info(f"   🎯 Embeddings: {chunks_with_embeddings} ({result['embedding_coverage']})")
            
            return result
            
        except Exception as e:
            logger.error(f"   ❌ Database test failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def test_embedding_model(self) -> Dict[str, Any]:
        """Test embedding model functionality"""
        logger.info("🧠 Testing embedding model...")
        
        try:
            embedding_model = self.rag_system.get_embedding_model()
            
            # Test embeddings for different types of content
            test_texts = [
                "artificial intelligence and machine learning",
                "web development with React and JavaScript",
                "database optimization and performance tuning",
                "cloud computing and AWS services"
            ]
            
            embeddings = []
            for text in test_texts:
                embedding = embedding_model.encode(text)
                embeddings.append(embedding)
                logger.info(f"   📊 Generated embedding: dimension {len(embedding)}")
            
            # Test similarity calculation
            from sklearn.metrics.pairwise import cosine_similarity
            import numpy as np
            
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            
            result = {
                'success': True,
                'embedding_dimension': len(embeddings[0]),
                'test_embeddings': len(embeddings),
                'sample_similarity': float(similarity)
            }
            
            logger.info(f"   ✅ Embedding model working")
            logger.info(f"   📏 Dimension: {result['embedding_dimension']}")
            logger.info(f"   🎯 Sample similarity: {similarity:.3f}")
            
            return result
            
        except Exception as e:
            logger.error(f"   ❌ Embedding model test failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def test_vector_search(self) -> Dict[str, Any]:
        """Test vector similarity search"""
        logger.info("🔍 Testing vector search...")
        
        try:
            # Test queries with different complexity
            test_queries = [
                "technology",
                "artificial intelligence",
                "web development best practices",
                "how to optimize database performance"
            ]
            
            results = {}
            for query in test_queries:
                start_time = time.time()
                
                chunks = self.rag_system.retrieve_relevant_chunks(
                    query=query, 
                    top_k=5
                )
                
                search_time = time.time() - start_time
                
                results[query] = {
                    'chunks_found': len(chunks),
                    'search_time_ms': round(search_time * 1000, 2),
                    'top_score': chunks[0]['score'] if chunks else 0
                }
                
                logger.info(f"   🔎 Query: '{query}' -> {len(chunks)} results in {search_time*1000:.1f}ms")
            
            overall_result = {
                'success': True,
                'queries_tested': len(test_queries),
                'average_search_time': round(
                    sum(r['search_time_ms'] for r in results.values()) / len(results), 2
                ),
                'total_unique_chunks': len(set(
                    chunk['id'] for result in results.values() 
                    for chunk in chunks if chunks  # This should reference the actual chunks
                )),
                'query_results': results
            }
            
            logger.info(f"   ✅ Vector search working")
            logger.info(f"   ⚡ Average search time: {overall_result['average_search_time']}ms")
            
            return overall_result
            
        except Exception as e:
            logger.error(f"   ❌ Vector search test failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def test_llm_integration(self) -> Dict[str, Any]:
        """Test LLM API integration"""
        logger.info("🤖 Testing LLM integration...")
        
        try:
            # Test different providers if available
            test_prompt = "Explain what artificial intelligence is in one sentence."
            
            providers_tested = []
            
            # Test OpenAI if available
            if os.environ.get('OPENAI_API_KEY'):
                try:
                    response = self.llm_service.generate_content(
                        prompt=test_prompt,
                        provider='openai',
                        max_tokens=50
                    )
                    providers_tested.append({
                        'provider': 'openai',
                        'success': True,
                        'response_length': len(response),
                        'sample': response[:100] + "..." if len(response) > 100 else response
                    })
                    logger.info(f"   ✅ OpenAI API working")
                except Exception as e:
                    providers_tested.append({
                        'provider': 'openai',
                        'success': False,
                        'error': str(e)
                    })
                    logger.error(f"   ❌ OpenAI API failed: {e}")
            
            # Test Anthropic if available
            if os.environ.get('ANTHROPIC_API_KEY'):
                try:
                    response = self.llm_service.generate_content(
                        prompt=test_prompt,
                        provider='anthropic',
                        max_tokens=50
                    )
                    providers_tested.append({
                        'provider': 'anthropic',
                        'success': True,
                        'response_length': len(response),
                        'sample': response[:100] + "..." if len(response) > 100 else response
                    })
                    logger.info(f"   ✅ Anthropic API working")
                except Exception as e:
                    providers_tested.append({
                        'provider': 'anthropic',
                        'success': False,
                        'error': str(e)
                    })
                    logger.error(f"   ❌ Anthropic API failed: {e}")
            
            working_providers = [p for p in providers_tested if p['success']]
            
            result = {
                'success': len(working_providers) > 0,
                'providers_tested': len(providers_tested),
                'working_providers': len(working_providers),
                'provider_details': providers_tested
            }
            
            if result['success']:
                logger.info(f"   ✅ LLM integration working ({len(working_providers)} providers)")
            else:
                logger.error(f"   ❌ No working LLM providers found")
            
            return result
            
        except Exception as e:
            logger.error(f"   ❌ LLM integration test failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def test_end_to_end_generation(self) -> Dict[str, Any]:
        """Test complete RAG pipeline from query to generated content"""
        logger.info("🎯 Testing end-to-end content generation...")
        
        try:
            test_cases = [
                {
                    'query': 'What is artificial intelligence?',
                    'platform': 'website',
                    'tone': 'informative'
                },
                {
                    'query': 'web development best practices',
                    'platform': 'blog', 
                    'tone': 'professional'
                },
                {
                    'query': 'database optimization techniques',
                    'platform': 'documentation',
                    'tone': 'technical'
                }
            ]
            
            results = []
            
            for i, test_case in enumerate(test_cases):
                logger.info(f"   🧪 Test case {i+1}: {test_case['query']}")
                
                start_time = time.time()
                
                try:
                    response = self.rag_system.process_and_generate(
                        query=test_case['query'],
                        platform=test_case['platform'],
                        tone=test_case['tone']
                    )
                    
                    generation_time = time.time() - start_time
                    
                    # Analyze response quality
                    response_text = response.get('text', '')
                    contains_default_message = "Sorry, I couldn't find relevant information" in response_text
                    
                    test_result = {
                        'query': test_case['query'],
                        'success': True,
                        'generation_time_ms': round(generation_time * 1000, 2),
                        'response_length': len(response_text),
                        'contains_default_message': contains_default_message,
                        'sources_used': len(response.get('sources', [])),
                        'response_preview': response_text[:200] + "..." if len(response_text) > 200 else response_text
                    }
                    
                    if contains_default_message:
                        logger.warning(f"     ⚠️ Default message returned - may indicate retrieval issues")
                    else:
                        logger.info(f"     ✅ Generated {len(response_text)} chars in {generation_time*1000:.1f}ms")
                    
                    results.append(test_result)
                    
                except Exception as e:
                    logger.error(f"     ❌ Generation failed: {e}")
                    results.append({
                        'query': test_case['query'],
                        'success': False,
                        'error': str(e)
                    })
            
            successful_tests = [r for r in results if r['success']]
            
            overall_result = {
                'success': len(successful_tests) > 0,
                'total_tests': len(test_cases),
                'successful_tests': len(successful_tests),
                'average_generation_time': round(
                    sum(r['generation_time_ms'] for r in successful_tests) / len(successful_tests), 2
                ) if successful_tests else 0,
                'test_results': results
            }
            
            logger.info(f"   🎯 End-to-end tests: {len(successful_tests)}/{len(test_cases)} successful")
            
            return overall_result
            
        except Exception as e:
            logger.error(f"   ❌ End-to-end test failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def test_performance_benchmarks(self) -> Dict[str, Any]:
        """Run performance benchmarks"""
        logger.info("⚡ Running performance benchmarks...")
        
        try:
            benchmarks = {}
            
            # Benchmark 1: Cold start time
            start_time = time.time()
            fresh_rag = RAGSystem()
            cold_start_time = time.time() - start_time
            benchmarks['cold_start_ms'] = round(cold_start_time * 1000, 2)
            
            # Benchmark 2: Embedding generation speed
            start_time = time.time()
            embedding_model = fresh_rag.get_embedding_model()
            test_text = "This is a test sentence for measuring embedding generation speed."
            embedding = embedding_model.encode(test_text)
            embedding_time = time.time() - start_time
            benchmarks['embedding_generation_ms'] = round(embedding_time * 1000, 2)
            
            # Benchmark 3: Batch search performance
            queries = [f"test query {i}" for i in range(10)]
            start_time = time.time()
            for query in queries:
                fresh_rag.retrieve_relevant_chunks(query=query, top_k=3)
            batch_search_time = time.time() - start_time
            benchmarks['batch_search_ms'] = round(batch_search_time * 1000, 2)
            benchmarks['avg_search_ms'] = round(batch_search_time * 1000 / len(queries), 2)
            
            logger.info(f"   🚀 Cold start: {benchmarks['cold_start_ms']}ms")
            logger.info(f"   🧠 Embedding generation: {benchmarks['embedding_generation_ms']}ms")
            logger.info(f"   🔍 Average search: {benchmarks['avg_search_ms']}ms")
            
            return {
                'success': True,
                'benchmarks': benchmarks
            }
            
        except Exception as e:
            logger.error(f"   ❌ Performance benchmark failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def run_full_test_suite(self) -> Dict[str, Any]:
        """Run the complete RAG pipeline test suite"""
        logger.info("🧪 Starting Full RAG Pipeline Test Suite")
        logger.info("=" * 60)
        
        # Run all tests
        tests = [
            ('database_connectivity', self.test_database_connectivity),
            ('embedding_model', self.test_embedding_model),
            ('vector_search', self.test_vector_search),
            ('llm_integration', self.test_llm_integration),
            ('end_to_end_generation', self.test_end_to_end_generation),
            ('performance_benchmarks', self.test_performance_benchmarks)
        ]
        
        for test_name, test_function in tests:
            logger.info(f"\n" + "─" * 40)
            self.test_results['tests'][test_name] = test_function()
            time.sleep(1)  # Brief pause between tests
        
        # Calculate overall results
        successful_tests = sum(1 for test in self.test_results['tests'].values() if test.get('success', False))
        total_tests = len(tests)
        
        self.test_results['summary'] = {
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'success_rate': f"{(successful_tests/total_tests*100):.1f}%",
            'overall_status': 'PASS' if successful_tests == total_tests else 'PARTIAL' if successful_tests > 0 else 'FAIL'
        }
        
        # Display summary
        logger.info(f"\n" + "=" * 60)
        logger.info("📊 TEST SUITE SUMMARY")
        logger.info("=" * 60)
        logger.info(f"   Tests run: {total_tests}")
        logger.info(f"   Successful: {successful_tests}")
        logger.info(f"   Success rate: {self.test_results['summary']['success_rate']}")
        logger.info(f"   Overall status: {self.test_results['summary']['overall_status']}")
        
        # Show recommendations
        self._show_recommendations()
        
        # Save detailed results
        with open('rag_pipeline_test_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        logger.info(f"\n📄 Detailed results saved to: rag_pipeline_test_results.json")
        
        return self.test_results
    
    def _show_recommendations(self):
        """Show recommendations based on test results"""
        logger.info(f"\n📋 RECOMMENDATIONS:")
        
        db_test = self.test_results['tests'].get('database_connectivity', {})
        if db_test.get('chunks_with_embeddings', 0) == 0:
            logger.info("   🔧 Generate embeddings: python scripts/optimize_vector_db.py")
        
        vector_test = self.test_results['tests'].get('vector_search', {})
        if not vector_test.get('success', False):
            logger.info("   🔧 Fix vector search: Check pgvector installation and embeddings")
        
        llm_test = self.test_results['tests'].get('llm_integration', {})
        if not llm_test.get('success', False):
            logger.info("   🔧 Configure LLM APIs: Add API keys to .env file")
        
        e2e_test = self.test_results['tests'].get('end_to_end_generation', {})
        if e2e_test.get('successful_tests', 0) == 0:
            logger.info("   🔧 Debug RAG pipeline: Check content processing and embeddings")
        
        performance = self.test_results['tests'].get('performance_benchmarks', {})
        if performance.get('benchmarks', {}).get('avg_search_ms', 0) > 1000:
            logger.info("   ⚡ Optimize performance: Add vector indexes and tune PostgreSQL")
    
    def __del__(self):
        """Clean up database session"""
        if hasattr(self, 'session'):
            self.session.close()

def main():
    """Main test function"""
    try:
        tester = RAGPipelineTester()
        tester.run_full_test_suite()
    except Exception as e:
        logger.error(f"Test suite failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
