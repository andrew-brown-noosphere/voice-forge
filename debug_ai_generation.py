#!/usr/bin/env python3
"""
Debug AI Generation Issues
Check why AI generation is falling back to templates
"""

import os
import sys

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

def test_openai_directly():
    """Test OpenAI API directly"""
    print("🤖 Testing OpenAI API Directly")
    print("=" * 32)
    
    # Check API key
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found!")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    try:
        import openai
        
        # Set API key
        openai.api_key = api_key
        
        print("📡 Testing API connection...")
        
        # Simple test call
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": "Say 'API test successful' in a creative way"}
            ],
            max_tokens=50
        )
        
        result = response.choices[0].message.content
        print(f"✅ OpenAI API working!")
        print(f"   Response: {result}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API failed: {e}")
        
        # Try with older model as fallback
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": "Say 'API test successful'"}
                ],
                max_tokens=20
            )
            
            result = response.choices[0].message.content
            print(f"✅ OpenAI API working with GPT-3.5!")
            print(f"   Response: {result}")
            print("⚠️  Note: gpt-4o-mini might not be available, using gpt-3.5-turbo")
            return True
            
        except Exception as e2:
            print(f"❌ OpenAI API completely failed: {e2}")
            return False

def test_ai_generator():
    """Test the AI content generator directly"""
    print("\n🎨 Testing AI Content Generator")
    print("=" * 32)
    
    try:
        from processor.ai_content_generator import AIContentGenerator
        
        ai_gen = AIContentGenerator()
        
        # Create sample chunks
        sample_chunks = [
            {
                "id": "test1",
                "text": "SignPath provides automated code signing solutions for enterprise teams. Our platform ensures secure, repeatable signing processes in the cloud.",
                "similarity": 0.9,
                "content_id": "test"
            }
        ]
        
        print("🔧 Testing AI generation...")
        
        response = ai_gen.generate_content(
            query="create a tweet about code signing",
            platform="twitter",
            tone="professional",
            chunks=sample_chunks
        )
        
        print(f"📝 AI Generator Response:")
        print(f"   Text: {response['text']}")
        print(f"   Length: {len(response['text'])} chars")
        
        metadata = response.get('metadata', {})
        error = metadata.get('error')
        
        if error:
            print(f"❌ AI Generator Error: {error}")
            return False
        else:
            print("✅ AI Generator working!")
            return True
            
    except Exception as e:
        print(f"❌ AI Generator failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_rag_integration():
    """Test the full RAG system"""
    print("\n🔄 Testing Full RAG Integration")
    print("=" * 32)
    
    try:
        from database.session import get_db_session
        from database.db import Database
        from processor.rag import RAGSystem
        
        session = get_db_session()
        db = Database(session)
        rag_system = RAGSystem(db)
        
        print("🔍 Testing RAG generation...")
        
        # Test with debugging
        response = rag_system.process_and_generate(
            query="create a tweet about code signing",
            platform="twitter",
            tone="professional"
        )
        
        print(f"📝 RAG Response:")
        print(f"   Text: {response['text'][:100]}...")
        print(f"   Length: {len(response['text'])} chars")
        
        metadata = response.get('metadata', {})
        generation_method = metadata.get('generation_method', 'unknown')
        model_used = metadata.get('model_used', 'unknown')
        
        print(f"   Generation method: {generation_method}")
        print(f"   Model used: {model_used}")
        
        if generation_method == 'template_fallback':
            print("❌ Using template fallback - AI generation failed!")
            return False
        else:
            print("✅ AI generation successful!")
            return True
            
        session.close()
        
    except Exception as e:
        print(f"❌ RAG test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def fix_openai_version():
    """Check and fix OpenAI library version"""
    print("\n📦 Checking OpenAI Library")
    print("=" * 25)
    
    try:
        import openai
        print(f"✅ OpenAI library version: {openai.__version__}")
        
        # Check if it's the new version (1.0+)
        version_parts = openai.__version__.split('.')
        major_version = int(version_parts[0])
        
        if major_version >= 1:
            print("✅ Using OpenAI v1.0+ (new API)")
            return True
        else:
            print("⚠️  Using older OpenAI library")
            print("🔧 Consider upgrading: pip install openai>=1.0.0")
            return True
            
    except ImportError:
        print("❌ OpenAI library not installed!")
        print("🔧 Install it: pip install openai")
        return False
    except Exception as e:
        print(f"⚠️  OpenAI library issue: {e}")
        return False

def main():
    print("🔍 VoiceForge AI Generation Debug")
    print("=" * 34)
    
    # Step 1: Check OpenAI library
    lib_ok = fix_openai_version()
    
    # Step 2: Test OpenAI API
    api_ok = test_openai_directly()
    
    # Step 3: Test AI generator
    gen_ok = test_ai_generator()
    
    # Step 4: Test full RAG integration
    rag_ok = test_rag_integration()
    
    print(f"\n📊 Debug Results:")
    print(f"   OpenAI Library: {'✅' if lib_ok else '❌'}")
    print(f"   OpenAI API: {'✅' if api_ok else '❌'}")
    print(f"   AI Generator: {'✅' if gen_ok else '❌'}")
    print(f"   RAG Integration: {'✅' if rag_ok else '❌'}")
    
    if not all([lib_ok, api_ok, gen_ok, rag_ok]):
        print(f"\n🔧 Fixes needed:")
        if not api_ok:
            print("   • Check OpenAI API key")
            print("   • Verify account has API access")
        if not gen_ok:
            print("   • Check AI generator code")
            print("   • Restart backend server")
        if not rag_ok:
            print("   • Full system restart needed")
    else:
        print(f"\n🎉 All systems working! If you're still getting templates:")
        print("   • Clear browser cache")
        print("   • Restart frontend: npm run dev")
        print("   • Check browser network tab for API errors")

if __name__ == "__main__":
    main()
