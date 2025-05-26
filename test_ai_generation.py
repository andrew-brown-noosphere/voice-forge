#!/usr/bin/env python3
"""
Test AI Content Generation
Verify that the new AI-powered content generation is working
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

def test_ai_generation():
    """Test the AI content generation system"""
    print("🤖 Testing AI Content Generation")
    print("=" * 35)
    
    # Check OpenAI API key
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment!")
        print("🔧 Make sure your .env file has: OPENAI_API_KEY=your-key")
        return False
    
    print(f"✅ OpenAI API key found: {api_key[:10]}...")
    
    try:
        from database.session import get_db_session
        from database.db import Database
        from processor.rag import RAGSystem
        
        session = get_db_session()
        db = Database(session)
        rag_system = RAGSystem(db)
        
        # Test query
        test_query = "create a tweet about code signing"
        platform = "twitter"
        tone = "professional"
        
        print(f"\n🔍 Testing AI generation:")
        print(f"   Query: '{test_query}'")
        print(f"   Platform: {platform}")
        print(f"   Tone: {tone}")
        
        # Generate content
        print("\n⏳ Generating AI content...")
        response = rag_system.process_and_generate(
            query=test_query,
            platform=platform,
            tone=tone
        )
        
        print(f"\n📝 Generated Content:")
        print(f"   Length: {len(response['text'])} characters")
        print(f"   Content: {response['text']}")
        
        # Show metadata
        metadata = response.get('metadata', {})
        generation_method = metadata.get('generation_method', 'ai')
        print(f"\n📊 Generation Details:")
        print(f"   Method: {generation_method}")
        print(f"   Sources: {len(response.get('source_chunks', []))}")
        print(f"   Model: {metadata.get('model_used', 'N/A')}")
        
        if generation_method == 'template_fallback':
            print("⚠️  Used template fallback - AI generation may have failed")
        else:
            print("✅ AI generation successful!")
        
        session.close()
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🚀 VoiceForge AI Content Generation Test")
    print("=" * 40)
    
    success = test_ai_generation()
    
    if success:
        print("\n🎯 Next Steps:")
        print("   1. Test in the frontend: http://localhost:5173")
        print("   2. Try different platforms and tones")
        print("   3. Check that content is high-quality and contextual")
    else:
        print("\n🔧 Troubleshooting:")
        print("   • Check OpenAI API key in .env")
        print("   • Ensure content has been processed")
        print("   • Verify backend is running")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
