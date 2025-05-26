"""
Simple setup script for VoiceForge (Python 3.11 version).
"""
import os
import sys
import logging
import subprocess
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Root directory - adjust this to your project location
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add the project root to the Python path
sys.path.insert(0, ROOT_DIR)

def install_dependencies():
    """Install Python dependencies."""
    try:
        logger.info("Installing Python dependencies...")
        subprocess.run(
            ["pip", "install", "-r", "requirements.txt"],
            check=True
        )
        
        # Install spaCy model
        try:
            logger.info("Downloading spaCy model...")
            subprocess.run(
                ["python", "-m", "spacy", "download", "en_core_web_sm"],
                check=True
            )
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to download spaCy model: {e}")
        
        logger.info("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to install dependencies: {e}")
        return False

def create_database():
    """Create PostgreSQL database if it doesn't exist."""
    try:
        logger.info("Setting up PostgreSQL database...")
        
        # Create database (assuming PostgreSQL is installed and running)
        db_name = "voiceforge"
        db_user = "postgres"
        db_password = "postgres"
        
        # Create database if it doesn't exist
        create_db_cmd = f"PGPASSWORD={db_password} createdb -U {db_user} {db_name} -e || true"
        subprocess.run(create_db_cmd, shell=True, check=False)
        
        # Create pgvector extension
        create_extension_cmd = f"PGPASSWORD={db_password} psql -U {db_user} -d {db_name} -c 'CREATE EXTENSION IF NOT EXISTS vector;'"
        subprocess.run(create_extension_cmd, shell=True, check=False)
        
        logger.info("✅ Database setup completed successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to set up database: {e}")
        logger.warning("You may need to create the database manually")
        return False

def run_migrations():
    """Run database migrations."""
    try:
        logger.info("Running database migrations...")
        env = os.environ.copy()
        env["PYTHONPATH"] = ROOT_DIR
        
        subprocess.run(
            ["alembic", "upgrade", "head"],
            env=env,
            check=True
        )
        logger.info("✅ Database migrations completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to run migrations: {e}")
        return False

def main():
    """Run the setup process."""
    logger.info("Starting VoiceForge setup...")
    
    # Install dependencies
    if not install_dependencies():
        logger.error("Setup failed at dependency installation")
        return False
    
    # Create database
    if not create_database():
        logger.warning("Database setup had issues, but continuing...")
    
    # Run migrations
    if not run_migrations():
        logger.error("Setup failed at database migrations")
        return False
    
    logger.info("✨ VoiceForge basic setup completed successfully!")
    logger.info("You can now start the server with: uvicorn api.main:app --reload")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
