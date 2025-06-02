#!/usr/bin/env python3
"""
Quick test to verify backend can start without errors.
Run this before starting the full server to catch issues early.
"""

import sys
import os

# Add the backend directory to the Python path
backend_dir = "/Users/andrewbrown/Sites/noosphere/github/voice-forge/backend"
sys.path.insert(0, backend_dir)
os.chdir(backend_dir)

def test_imports():
    """Test that all critical imports work."""
    print("🔍 Testing Python imports...")
    
    try:
        # Core web framework
        import fastapi 
        print(f"✅ FastAPI: {fastapi.__version__}")
        
        import uvicorn
        print("✅ Uvicorn imported successfully")
        
        # Database
        import sqlalchemy
        print(f"✅ SQLAlchemy: {sqlalchemy.__version__}")
        
        import psycopg2
        print("✅ PostgreSQL driver (psycopg2) imported successfully")
        
        # Authentication
        import jwt
        print("✅ JWT imported successfully")
        
        # Environment variables
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Environment variables loaded")
        
        # Test main app import
        from api.main import app
        print("✅ Main application imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("💡 Try running: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_environment():
    """Test environment configuration."""
    print("\n🔧 Testing environment configuration...")
    
    # Check critical environment variables
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key and len(openai_key) > 10:
        print("✅ OpenAI API key configured")
    else:
        print("⚠️  OpenAI API key missing or invalid")
    
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        print("✅ Database URL configured")
    else:
        print("❌ Database URL missing")
    
    clerk_key = os.getenv('CLERK_SECRET_KEY')
    if clerk_key and len(clerk_key) > 10:
        print("✅ Clerk secret key configured")
    else:
        print("⚠️  Clerk secret key missing or invalid")

def test_database_connection():
    """Test database connectivity."""
    print("\n🗄️  Testing database connection...")
    
    try:
        import psycopg2
        from urllib.parse import urlparse
        
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            print("❌ DATABASE_URL not configured")
            return False
        
        # Parse and connect
        parsed = urlparse(db_url)
        conn = psycopg2.connect(
            host=parsed.hostname or 'localhost',
            port=parsed.port or 5432,
            database=parsed.path[1:] if parsed.path else 'voice_forge',
            user=parsed.username,
            password=parsed.password
        )
        
        cursor = conn.cursor()
        cursor.execute('SELECT 1;')
        cursor.fetchone()
        
        print("✅ Database connection successful")
        
        # Check for vector extension
        cursor.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
        if cursor.fetchone():
            print("✅ pgvector extension available")
        else:
            print("⚠️  pgvector extension not installed")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 VoiceForge Backend Pre-flight Check")
    print("=====================================")
    
    # Test imports
    imports_ok = test_imports()
    
    # Test environment
    test_environment() 
    
    # Test database
    db_ok = test_database_connection()
    
    # Summary
    print("\n📊 Test Summary:")
    print("================")
    if imports_ok:
        print("✅ Python imports: PASS")
    else:
        print("❌ Python imports: FAIL")
    
    if db_ok:
        print("✅ Database connection: PASS")
    else:
        print("❌ Database connection: FAIL")
    
    if imports_ok and db_ok:
        print("\n🎉 All critical tests passed! Backend should start successfully.")
        print("💡 You can now run: python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")
        return True
    else:
        print("\n🚨 Some tests failed. Fix the issues above before starting the backend.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
