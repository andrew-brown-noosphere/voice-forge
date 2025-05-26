"""
Setup script for VoiceForge.
"""
import os
import sys
import logging
import subprocess
import time
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Root directory
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add the project root to the Python path
sys.path.insert(0, ROOT_DIR)

def check_python_version():
    """Check Python version compatibility."""
    python_version = sys.version_info
    
    # Log the Python version
    logger.info(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check if Python version is compatible
    if python_version.major != 3 or python_version.minor != 11:
        logger.warning(f"You're using Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        logger.warning("This project is optimized for Python 3.11 for best performance with neural embeddings.")
        logger.warning("Some advanced features might not work optimally on other Python versions.")
        
        # Ask for confirmation if not using Python 3.11
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 9):
            logger.error("Python version must be at least 3.9. Please use a newer Python version.")
            return False
        
        response = input("Do you want to continue with your current Python version? (y/n): ")
        if response.lower() != 'y':
            logger.info("Setup cancelled. Please install Python 3.11 and try again.")
            return False
    
    return True

def install_dependencies():
    """Install Python dependencies."""
    try:
        logger.info("Installing Python dependencies...")
        subprocess.run(
            ["pip", "install", "-r", "requirements.txt"],
            cwd=ROOT_DIR + "/backend",
            check=True
        )
        
        # Install spaCy model
        try:
            logger.info("Downloading spaCy model...")
            subprocess.run(
                ["python", "-m", "spacy", "download", "en_core_web_sm"],
                cwd=ROOT_DIR,
                check=True
            )
        except subprocess.CalledProcessError:
            logger.warning("Failed to download spaCy model, will use fallback")
        
        logger.info("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to install dependencies: {e}")
        return False

def run_database_migrations():
    """Run database migrations."""
    try:
        logger.info("Running database migrations...")
        
        # Make sure DATABASE_URL environment variable is set
        if "DATABASE_URL" not in os.environ:
            from database.session import DATABASE_URL
            os.environ["DATABASE_URL"] = DATABASE_URL
            logger.info(f"Using default DATABASE_URL: {DATABASE_URL}")
        
        subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=ROOT_DIR + "/backend",
            check=True,
            env=dict(os.environ, PYTHONPATH=ROOT_DIR)
        )
        logger.info("✅ Database migrations completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to run migrations: {e}")
        return False

def setup_pinecone():
    """Test Pinecone setup."""
    try:
        logger.info("Testing Pinecone connection...")
        
        # Import after adding to path
        from database.vector.factory import get_vector_db_client
        
        # Get vector client
        client = get_vector_db_client()
        
        if client is None:
            logger.error("❌ Failed to get vector database client")
            return False
        
        # Get stats to test connection
        stats = client.get_stats()
        logger.info(f"Pinecone index stats: {stats}")
        
        logger.info("✅ Pinecone connection verified")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to set up Pinecone: {e}")
        return False

def create_templates():
    """Create sample marketing templates."""
    try:
        logger.info("Creating sample marketing templates...")
        script_path = os.path.join(ROOT_DIR, "backend", "scripts", "create_templates.py")
        
        subprocess.run(
            ["python", script_path],
            cwd=ROOT_DIR + "/backend",
            check=True,
            env=dict(os.environ, PYTHONPATH=ROOT_DIR)
        )
        logger.info("✅ Templates created successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to create templates: {e}")
        return False

def check_database():
    """Check if PostgreSQL database exists and create if not."""
    try:
        logger.info("Checking PostgreSQL database...")
        
        # Get database connection parameters
        from database.session import DATABASE_URL
        
        # Extract database name from URL
        db_name = DATABASE_URL.split("/")[-1]
        
        # Create connection string to PostgreSQL server (without database)
        server_url = DATABASE_URL.rsplit("/", 1)[0]
        
        # Check if database exists
        check_cmd = f"psql {server_url} -t -c \"SELECT 1 FROM pg_database WHERE datname='{db_name}'\""
        result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
        
        if "1" not in result.stdout:
            logger.info(f"Database '{db_name}' does not exist, creating...")
            create_cmd = f"psql {server_url} -c \"CREATE DATABASE {db_name}\""
            subprocess.run(create_cmd, shell=True, check=True)
            logger.info(f"Database '{db_name}' created successfully")
        else:
            logger.info(f"Database '{db_name}' already exists")
        
        # Create pgvector extension if it doesn't exist
        try:
            pgvector_cmd = f"psql {DATABASE_URL} -c \"CREATE EXTENSION IF NOT EXISTS vector\""
            subprocess.run(pgvector_cmd, shell=True, check=True)
            logger.info("pgvector extension created successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create pgvector extension: {e}")
            logger.warning("Vector search functionality may not work properly")
        
        return True
    except Exception as e:
        logger.error(f"❌ Failed to check/create database: {e}")
        logger.warning("You may need to create the database manually")
        return False

def main():
    """Run the setup process."""
    logger.info("Starting VoiceForge setup...")
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Load environment variables
    load_dotenv(os.path.join(ROOT_DIR, "backend", ".env"))
    
    # Install dependencies
    if not install_dependencies():
        logger.error("Setup failed at dependency installation")
        return False
    
    # Check database
    check_database()
    
    # Run migrations
    if not run_database_migrations():
        logger.error("Setup failed at database migrations")
        return False
    
    # Check Pinecone setup
    if not setup_pinecone():
        logger.warning("Pinecone setup had issues, but continuing...")
    
    # Create templates
    if not create_templates():
        logger.warning("Template creation had issues, but continuing...")
    
    logger.info("✨ VoiceForge setup completed successfully!")
    logger.info("You can now start the server with: uvicorn api.main:app --reload")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
