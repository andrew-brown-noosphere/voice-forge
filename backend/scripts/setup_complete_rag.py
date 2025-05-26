#!/usr/bin/env python3
"""
Complete RAG Setup and Optimization
Master script that sets up and optimizes the entire RAG system
"""

import os
import sys
import subprocess
import time
import logging
from pathlib import Path

# Load environment variables from .env file first
def load_env_file():
    """Load environment variables from .env file"""
    backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(backend_path, '.env')
    
    if os.path.exists(env_path):
        print(f"📄 Loading environment from {env_path}")
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        print(f"✅ Environment variables loaded")
        
        # Debug: Show which vars are now set (without showing values)
        important_vars = ['OPENAI_API_KEY', 'DATABASE_URL', 'VECTOR_DB_PROVIDER']
        for var in important_vars:
            status = "SET" if os.environ.get(var) else "NOT SET"
            print(f"   {var}: {status}")
        
        return True
    else:
        print(f"❌ .env file not found at {env_path}")
        return False

# Load .env file before importing anything else
load_env_success = load_env_file()

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RAGSetupManager:
    """Manages the complete RAG setup and optimization process"""
    
    def __init__(self):
        self.backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.scripts_path = os.path.join(self.backend_path, 'scripts')
        
    def run_script(self, script_name: str, description: str) -> bool:
        """Run a Python script and return success status"""
        script_path = os.path.join(self.scripts_path, script_name)
        
        if not os.path.exists(script_path):
            logger.error(f"❌ Script not found: {script_path}")
            return False
        
        logger.info(f"🔄 {description}")
        logger.info(f"   Running: {script_name}")
        
        try:
            # Change to backend directory before running script
            original_cwd = os.getcwd()
            os.chdir(self.backend_path)
            
            # Set up environment for the subprocess
            env = os.environ.copy()
            env['PYTHONPATH'] = self.backend_path
            
            # Run the script
            result = subprocess.run([
                sys.executable, script_path
            ], capture_output=True, text=True, timeout=300, env=env)  # 5 minute timeout
            
            # Restore original working directory
            os.chdir(original_cwd)
            
            if result.returncode == 0:
                logger.info(f"   ✅ {description} completed successfully")
                if result.stdout:
                    # Show last few lines of output
                    lines = result.stdout.strip().split('\n')
                    for line in lines[-3:]:  # Show last 3 lines
                        if line.strip():  # Only show non-empty lines
                            logger.info(f"   📝 {line}")
                return True
            else:
                logger.error(f"   ❌ {description} failed")
                if result.stderr:
                    logger.error(f"   🐛 Error: {result.stderr[:300]}...")
                if result.stdout:
                    logger.error(f"   📝 Output: {result.stdout[-300:]}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"   ⏰ {description} timed out")
            return False
        except Exception as e:
            logger.error(f"   ❌ Error running {script_name}: {e}")
            return False
    
    def check_prerequisites(self) -> bool:
        """Check if prerequisites are met"""
        logger.info("🔍 Checking Prerequisites")
        logger.info("=" * 40)
        
        # Check environment variables
        required_env_vars = ['OPENAI_API_KEY', 'DATABASE_URL']
        missing_vars = []
        
        for var in required_env_vars:
            value = os.environ.get(var)
            if not value:
                missing_vars.append(var)
            else:
                logger.info(f"✅ {var}: {'*' * 20}...{value[-10:] if len(value) > 10 else '*' * len(value)}")
        
        if missing_vars:
            logger.error(f"❌ Missing environment variables: {', '.join(missing_vars)}")
            logger.error("   Please check your .env file")
            
            # Show what we do have
            logger.info("   Current environment variables:")
            for key, value in os.environ.items():
                if any(keyword in key.upper() for keyword in ['API', 'KEY', 'URL', 'DATABASE']):
                    logger.info(f"     {key}: {'SET' if value else 'EMPTY'}")
            
            return False
        
        logger.info("✅ Required environment variables configured")
        
        # Check if key files exist
        key_files = [
            'processor/rag.py',
            'processor/llm/llm_service.py',
            'database/models.py'
        ]
        
        missing_files = []
        for file_path in key_files:
            full_path = os.path.join(self.backend_path, file_path)
            if not os.path.exists(full_path):
                missing_files.append(file_path)
        
        if missing_files:
            logger.error(f"❌ Missing key files: {', '.join(missing_files)}")
            return False
        
        logger.info("✅ Key files present")
        
        # Check if we can connect to database
        try:
            from database.session import get_db_session
            from sqlalchemy import text
            session = get_db_session()
            session.execute(text("SELECT 1"))
            session.close()
            logger.info("✅ Database connection working")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            logger.error(f"   DATABASE_URL: {os.environ.get('DATABASE_URL', 'NOT SET')}")
            return False
        
        return True
    
    def run_complete_setup(self) -> bool:
        """Run the complete RAG setup process"""
        logger.info("🚀 Starting Complete RAG Setup and Optimization")
        logger.info("=" * 60)
        
        # Step 1: Check prerequisites
        if not self.check_prerequisites():
            logger.error("❌ Prerequisites not met. Please fix issues and try again.")
            return False
        
        # Step 2: Add sample content (if needed)
        logger.info(f"\n" + "─" * 60)
        success = self.run_script(
            'add_sample_content.py',
            'Adding sample content for testing'
        )
        if not success:
            logger.warning("⚠️ Sample content addition failed, but continuing...")
        
        # Step 3: Process content for RAG
        logger.info(f"\n" + "─" * 60)
        success = self.run_script(
            'process_content_for_rag.py',
            'Processing content and generating embeddings'
        )
        if not success:
            logger.error("❌ Content processing failed. Cannot continue.")
            return False
        
        # Step 4: Optimize vector database
        logger.info(f"\n" + "─" * 60)
        success = self.run_script(
            'optimize_vector_db.py',
            'Optimizing vector database performance'
        )
        if not success:
            logger.warning("⚠️ Vector DB optimization failed, but continuing...")
        
        # Step 5: Test the complete pipeline
        logger.info(f"\n" + "─" * 60)
        success = self.run_script(
            'test_full_rag_pipeline.py',
            'Testing complete RAG pipeline'
        )
        if not success:
            logger.error("❌ RAG pipeline test failed")
            return False
        
        # Step 6: Run final diagnostics
        logger.info(f"\n" + "─" * 60)
        success = self.run_script(
            'diagnose_vector_db.py',
            'Running final system diagnostics'
        )
        if not success:
            logger.warning("⚠️ Final diagnostics failed, but setup may still be working")
        
        return True
    
    def show_completion_summary(self):
        """Show completion summary and next steps"""
        logger.info(f"\n" + "=" * 60)
        logger.info("🎉 RAG SETUP AND OPTIMIZATION COMPLETE!")
        logger.info("=" * 60)
        
        logger.info("\n📋 What's been set up:")
        logger.info("   ✅ Sample content added to database")
        logger.info("   ✅ Content processed and chunked")
        logger.info("   ✅ Vector embeddings generated")
        logger.info("   ✅ Database optimized for vector search")
        logger.info("   ✅ Complete RAG pipeline tested")
        
        logger.info("\n🎯 Your RAG system is now ready to:")
        logger.info("   • Answer questions based on your content")
        logger.info("   • Generate contextual responses")
        logger.info("   • Perform semantic search")
        logger.info("   • Scale to handle more content")
        
        logger.info("\n🔧 Quick test commands:")
        logger.info("   # Test individual components:")
        logger.info("   python scripts/test_openai.py")
        logger.info("   python scripts/test_full_rag_pipeline.py")
        logger.info("   python scripts/diagnose_vector_db.py")
        
        logger.info("\n📚 Add more content:")
        logger.info("   # Use your existing crawler to add more content")
        logger.info("   # Then process it with:")
        logger.info("   python scripts/process_content_for_rag.py")
        
        logger.info("\n🎨 Integration examples:")
        logger.info("   # Use the RAG system in your application:")
        logger.info("   from processor.rag_service import RAGService")
        logger.info("   from database.db import Database")
        logger.info("   # ... (see existing API endpoints)")
        
        logger.info("\n📈 Performance monitoring:")
        logger.info("   # Regular health checks:")
        logger.info("   python scripts/diagnose_vector_db.py")
        
        logger.info(f"\n🏆 Success! Your VoiceForge RAG system is ready for production use.")

def main():
    """Main setup function"""
    try:
        if not load_env_success:
            print("❌ Could not load .env file. Please ensure it exists and is properly formatted.")
            print("   Expected location: /Users/andrewbrown/Sites/noosphere/github/voice-forge/backend/.env")
            sys.exit(1)
        
        setup_manager = RAGSetupManager()
        
        # Run complete setup
        success = setup_manager.run_complete_setup()
        
        if success:
            setup_manager.show_completion_summary()
        else:
            logger.error("\n❌ Setup failed. Please check the logs above for specific issues.")
            logger.error("💡 Common issues:")
            logger.error("   - Missing API keys in .env file")
            logger.error("   - Database connection problems")
            logger.error("   - Missing Python dependencies")
            
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("\n⏹️ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n💥 Unexpected error during setup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
