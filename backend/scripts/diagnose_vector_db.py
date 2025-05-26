#!/usr/bin/env python3
"""
Vector Database Diagnostic Script
Analyzes current vector DB setup and provides optimization recommendations
"""

import os
import sys
import traceback
from typing import Dict, Any

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_environment() -> Dict[str, Any]:
    """Check environment variables and configuration"""
    env_status = {
        'vector_db_provider': os.environ.get('VECTOR_DB_PROVIDER', 'database'),
        'pinecone_api_key': 'SET' if os.environ.get('PINECONE_API_KEY') else 'NOT SET',
        'openai_api_key': 'SET' if os.environ.get('OPENAI_API_KEY') else 'NOT SET',
        'anthropic_api_key': 'SET' if os.environ.get('ANTHROPIC_API_KEY') else 'NOT SET',
        'database_url': 'SET' if os.environ.get('DATABASE_URL') else 'NOT SET'
    }
    return env_status

def check_database_vector_capabilities():
    """Check PostgreSQL vector capabilities"""
    try:
        from database.session import get_db_session
        
        db_session = get_db_session()
        
        # Check pgvector extension
        result = db_session.execute("SELECT 1 FROM pg_extension WHERE extname = 'vector'").fetchone()
        pgvector_installed = bool(result)
        
        # Check content_chunks table structure
        chunks_result = db_session.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'content_chunks'
        """).fetchall()
        
        has_embedding_column = any(col[0] == 'embedding' for col in chunks_result)
        
        # Count chunks with embeddings
        if has_embedding_column:
            embedding_count = db_session.execute(
                "SELECT COUNT(*) FROM content_chunks WHERE embedding IS NOT NULL"
            ).fetchone()[0]
        else:
            embedding_count = 0
            
        # Count total chunks
        total_chunks = db_session.execute("SELECT COUNT(*) FROM content_chunks").fetchone()[0]
        
        # Check for vector indexes
        vector_indexes = db_session.execute("""
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE tablename = 'content_chunks' 
            AND indexdef LIKE '%vector%'
        """).fetchall()
        
        db_session.close()
        
        return {
            'pgvector_installed': pgvector_installed,
            'has_embedding_column': has_embedding_column,
            'chunks_with_embeddings': embedding_count,
            'total_chunks': total_chunks,
            'embedding_coverage': f"{(embedding_count/total_chunks*100):.1f}%" if total_chunks > 0 else "0%",
            'vector_indexes': len(vector_indexes),
            'table_structure': chunks_result
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'traceback': traceback.format_exc()
        }

def check_rag_system():
    """Check RAG system components"""
    try:
        from processor.rag import RAGSystem
        from processor.retrieval.hybrid_retriever import HybridRetriever
        from processor.llm.llm_service import LLMService
        
        # Try to initialize components
        rag_available = True
        hybrid_retriever_available = True
        llm_service_available = True
        
        try:
            rag = RAGSystem()
        except:
            rag_available = False
            
        try:
            retriever = HybridRetriever()
        except:
            hybrid_retriever_available = False
            
        try:
            llm = LLMService()
        except:
            llm_service_available = False
        
        return {
            'rag_system': rag_available,
            'hybrid_retriever': hybrid_retriever_available,
            'llm_service': llm_service_available
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'components_available': False
        }

def check_file_structure():
    """Check if expected files exist"""
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    expected_files = [
        'processor/retrieval/relevance_scoring.py',
        'processor/retrieval/context_filter.py', 
        'processor/retrieval/hybrid_retriever.py',
        'processor/retrieval/query_reformulation.py',
        'processor/llm/api_client.py',
        'processor/llm/token_manager.py',
        'processor/llm/response_cache.py',
        'processor/llm/prompt_templates.py',
        'processor/llm/llm_service.py',
        'processor/llm/templates.json',
        '.env'
    ]
    
    file_status = {}
    for file_path in expected_files:
        full_path = os.path.join(base_path, file_path)
        file_status[file_path] = os.path.exists(full_path)
    
    return file_status

def test_vector_search():
    """Test basic vector search functionality"""
    try:
        from processor.rag import RAGSystem
        
        rag = RAGSystem()
        
        # Try a simple search
        results = rag.search("test query", limit=5)
        
        return {
            'search_works': True,
            'results_count': len(results) if results else 0,
            'sample_result': results[0] if results else None
        }
        
    except Exception as e:
        return {
            'search_works': False,
            'error': str(e)
        }

def main():
    """Run comprehensive vector DB diagnostic"""
    print("🔍 VoiceForge Vector Database Diagnostic")
    print("=" * 50)
    
    # Check environment
    print("\n📋 Environment Configuration:")
    env_status = check_environment()
    for key, value in env_status.items():
        status_icon = "✅" if value not in ['NOT SET', 'database'] else "⚠️"
        print(f"  {status_icon} {key}: {value}")
    
    # Check file structure
    print("\n📁 File Structure:")
    file_status = check_file_structure()
    missing_files = [f for f, exists in file_status.items() if not exists]
    existing_files = [f for f, exists in file_status.items() if exists]
    
    print(f"  ✅ Existing files: {len(existing_files)}/{len(file_status)}")
    if missing_files:
        print(f"  ❌ Missing files:")
        for file in missing_files[:5]:  # Show first 5 missing files
            print(f"    - {file}")
        if len(missing_files) > 5:
            print(f"    ... and {len(missing_files) - 5} more")
    
    # Check database capabilities
    print("\n🗄️ Database Vector Capabilities:")
    db_status = check_database_vector_capabilities()
    if 'error' in db_status:
        print(f"  ❌ Database check failed: {db_status['error']}")
    else:
        pgvector_icon = "✅" if db_status['pgvector_installed'] else "❌"
        embedding_icon = "✅" if db_status['has_embedding_column'] else "❌"
        coverage_icon = "✅" if db_status['chunks_with_embeddings'] > 0 else "⚠️"
        
        print(f"  {pgvector_icon} pgvector extension: {'INSTALLED' if db_status['pgvector_installed'] else 'NOT INSTALLED'}")
        print(f"  {embedding_icon} Embedding column: {'EXISTS' if db_status['has_embedding_column'] else 'MISSING'}")
        print(f"  {coverage_icon} Chunks with embeddings: {db_status['chunks_with_embeddings']}/{db_status['total_chunks']} ({db_status['embedding_coverage']})")
        print(f"  📊 Vector indexes: {db_status['vector_indexes']}")
    
    # Check RAG system
    print("\n🤖 RAG System Components:")
    rag_status = check_rag_system()
    if 'error' in rag_status:
        print(f"  ❌ Component check failed: {rag_status['error']}")
    else:
        for component, available in rag_status.items():
            icon = "✅" if available else "❌"
            print(f"  {icon} {component}: {'AVAILABLE' if available else 'UNAVAILABLE'}")
    
    # Test vector search
    print("\n🔍 Vector Search Test:")
    search_status = test_vector_search()
    if search_status['search_works']:
        print(f"  ✅ Vector search: WORKING")
        print(f"  📊 Test results: {search_status['results_count']} items found")
    else:
        print(f"  ❌ Vector search: FAILED")
        print(f"  🐛 Error: {search_status['error']}")
    
    # Recommendations
    print("\n🎯 Recommendations:")
    
    if not env_status['openai_api_key'] == 'SET' and not env_status['anthropic_api_key'] == 'SET':
        print("  🔑 Set up API keys for OpenAI or Anthropic in .env file")
    
    if 'error' not in db_status:
        if not db_status['pgvector_installed']:
            print("  🔧 Install pgvector extension: CREATE EXTENSION IF NOT EXISTS vector;")
        
        if not db_status['has_embedding_column']:
            print("  🗄️ Add embedding column to content_chunks table")
        
        if db_status['chunks_with_embeddings'] == 0:
            print("  ⚡ Generate embeddings for existing content")
        
        if db_status['vector_indexes'] == 0 and db_status['chunks_with_embeddings'] > 100:
            print("  📈 Add vector indexes for better performance")
    
    if env_status['vector_db_provider'] == 'database' and env_status['pinecone_api_key'] == 'NOT SET':
        print("  🎯 Consider Pinecone for production-scale vector search")
    
    print("\n✨ Next Steps:")
    print("  1. Fix any ❌ issues above")
    print("  2. Run: python scripts/test_openai.py")
    print("  3. Run: python scripts/optimize_vector_db.py")
    print("  4. Run: python scripts/test_full_rag_pipeline.py")

if __name__ == "__main__":
    main()
