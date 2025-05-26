#!/usr/bin/env python3
"""
Quick Backend Test - Verify environment is working
"""

import sys
import os

def test_environment():
    """Test if the backend environment is properly configured"""
    print("🧪 VoiceForge Backend Environment Test")
    print("=" * 40)
    
    # Test Python version
    print(f"🐍 Python version: {sys.version}")
    
    # Test core imports
    tests = [
        ("FastAPI", "import fastapi"),
        ("Uvicorn", "import uvicorn"),
        ("SQLAlchemy", "import sqlalchemy"),
        ("Database Session", "from database.session import get_db_session"),
        ("Database Models", "from database.models import Content"),
        ("RAG System", "from processor.rag import RAGSystem"),
        ("RAG Service", "from processor.rag_service import RAGService"),
        ("API Main", "from api.main import app"),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, import_cmd in tests:
        try:
            exec(import_cmd)
            print(f"✅ {name}: OK")
            passed += 1
        except ImportError as e:
            print(f"❌ {name}: FAILED - {e}")
        except Exception as e:
            print(f"⚠️  {name}: ERROR - {e}")
    
    # Test environment variables
    print("\n🔧 Environment Variables:")
    env_vars = ['OPENAI_API_KEY', 'DATABASE_URL']
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            print(f"✅ {var}: SET")
        else:
            print(f"❌ {var}: NOT SET")
    
    # Summary
    print(f"\n📊 Test Results: {passed}/{total} imports successful")
    
    if passed == total:
        print("🎉 Backend environment is ready!")
        print("\n🚀 Start the backend with:")
        print("   python -m uvicorn api.main:app --reload")
        return True
    else:
        print("❌ Backend environment needs setup")
        print("\n🔧 Run setup script:")
        print("   ./setup_environment.sh")
        return False

if __name__ == "__main__":
    # Add backend path
    backend_path = '/Users/andrewbrown/Sites/noosphere/github/voice-forge/backend'
    sys.path.append(backend_path)
    os.chdir(backend_path)
    
    # Load environment
    env_path = os.path.join(backend_path, '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
    
    success = test_environment()
    sys.exit(0 if success else 1)
