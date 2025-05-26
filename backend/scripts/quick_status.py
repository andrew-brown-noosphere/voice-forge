#!/usr/bin/env python3
"""
Quick RAG Status Check
Provides a quick overview of your RAG system status
"""

import os
import sys
import time
from datetime import datetime

# Load environment variables from .env file first
def load_env_file():
    """Load environment variables from .env file"""
    backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(backend_path, '.env')
    
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        return True
    return False

# Load .env file
load_env_file()

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_rag_status():
    """Quick status check of RAG system"""
    print("🔍 VoiceForge RAG System Status Check")
    print("=" * 45)
    print(f"📅 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    status = {
        'database': '❓',
        'content': '❓', 
        'chunks': '❓',
        'embeddings': '❓',
        'rag_system': '❓',
        'llm_integration': '❓'
    }
    
    try:
        # Check database connection
        from database.session import get_db_session
        from sqlalchemy import text
        session = get_db_session()
        session.execute(text("SELECT 1"))
        status['database'] = '✅'
        
        # Check content
        from database.models import Content, ContentChunk
        content_count = session.query(Content).count()
        if content_count > 0:
            status['content'] = f'✅ ({content_count})'
        else:
            status['content'] = '❌ (0)'
        
        # Check chunks
        chunk_count = session.query(ContentChunk).count()
        if chunk_count > 0:
            status['chunks'] = f'✅ ({chunk_count})'
        else:
            status['chunks'] = '❌ (0)'
        
        # Check embeddings
        chunks_with_embeddings = session.query(ContentChunk).filter(
            ContentChunk.embedding.isnot(None)
        ).count()
        if chunks_with_embeddings > 0:
            coverage = f"{(chunks_with_embeddings/chunk_count*100):.0f}%" if chunk_count > 0 else "0%"
            status['embeddings'] = f'✅ ({chunks_with_embeddings}/{chunk_count} - {coverage})'
        else:
            status['embeddings'] = '❌ (0)'
        
        session.close()
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")
    
    try:
        # Check RAG system
        from processor.rag import RAGSystem
        rag = RAGSystem()
        status['rag_system'] = '✅'
    except Exception as e:
        status['rag_system'] = f'❌ ({str(e)[:30]}...)'
    
    try:
        # Check LLM integration
        from processor.llm.llm_service import LLMService
        llm = LLMService()
        if os.environ.get('OPENAI_API_KEY') or os.environ.get('ANTHROPIC_API_KEY'):
            status['llm_integration'] = '✅'
        else:
            status['llm_integration'] = '⚠️ (No API keys)'
    except Exception as e:
        status['llm_integration'] = f'❌ ({str(e)[:30]}...)'
    
    # Display status
    print(f"\n📊 System Components:")
    print(f"   Database Connection: {status['database']}")
    print(f"   Content Items: {status['content']}")
    print(f"   Content Chunks: {status['chunks']}")
    print(f"   Embeddings: {status['embeddings']}")
    print(f"   RAG System: {status['rag_system']}")
    print(f"   LLM Integration: {status['llm_integration']}")
    
    # Overall health
    working_components = sum(1 for v in status.values() if v.startswith('✅'))
    total_components = len(status)
    health_percentage = (working_components / total_components) * 100
    
    print(f"\n💪 Overall Health: {health_percentage:.0f}% ({working_components}/{total_components} components working)")
    
    if health_percentage == 100:
        print("🎉 Your RAG system is fully operational!")
    elif health_percentage >= 70:
        print("⚠️ Your RAG system is mostly working but needs attention")
    else:
        print("❌ Your RAG system needs setup/fixing")
    
    # Environment check
    print(f"\n🔧 Environment Status:")
    env_vars = ['OPENAI_API_KEY', 'DATABASE_URL', 'VECTOR_DB_PROVIDER']
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            print(f"   {var}: ✅ SET")
        else:
            print(f"   {var}: ❌ NOT SET")
    
    # Recommendations
    print(f"\n📋 Quick Actions:")
    if status['content'].startswith('❌'):
        print("   🔧 Add content: python scripts/add_sample_content.py")
    if status['chunks'].startswith('❌') or status['embeddings'].startswith('❌'):
        print("   🔧 Process content: python scripts/process_content_for_rag.py")
    if not (status['rag_system'].startswith('✅') and status['llm_integration'].startswith('✅')):
        print("   🔧 Run full setup: python scripts/setup_complete_rag.py")
    
    print("   📊 Detailed diagnostics: python scripts/diagnose_vector_db.py")
    print("   🧪 Full test: python scripts/test_full_rag_pipeline.py")

if __name__ == "__main__":
    check_rag_status()
