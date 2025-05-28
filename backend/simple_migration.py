"""
Simple step-by-step migration for multi-tenancy.
Run each step individually to avoid hanging.
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_url():
    """Get database URL from environment."""
    return os.getenv("DATABASE_URL", "postgresql://andrewbrown@localhost:5432/voice_forge")

def test_connection():
    """Test database connection."""
    try:
        database_url = get_database_url()
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        result = session.execute(text("SELECT 1 as test;")).fetchone()
        logger.info(f"✅ Database connection successful: {result}")
        session.close()
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

def step1_create_organizations_table():
    """Step 1: Create organizations table."""
    try:
        database_url = get_database_url()
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        logger.info("Step 1: Creating organizations table...")
        
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS organizations (
                id VARCHAR NOT NULL PRIMARY KEY,
                name VARCHAR NOT NULL,
                slug VARCHAR NOT NULL UNIQUE,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP,
                max_users INTEGER DEFAULT 5,
                max_content_items INTEGER DEFAULT 1000,
                max_crawls_per_month INTEGER DEFAULT 10,
                features JSONB DEFAULT '{}'
            );
        """))
        
        session.commit()
        session.close()
        logger.info("✅ Organizations table created successfully.")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create organizations table: {e}")
        return False

def step2_create_default_org():
    """Step 2: Create default organization."""
    try:
        database_url = get_database_url()
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        logger.info("Step 2: Creating default organization...")
        
        # Check if default org exists
        existing = session.execute(text("""
            SELECT id FROM organizations WHERE id = 'org_default_migration'
        """)).fetchone()
        
        if not existing:
            session.execute(text("""
                INSERT INTO organizations (id, name, slug, created_at)
                VALUES ('org_default_migration', 'Default Organization', 'default-org', NOW())
            """))
            logger.info("✅ Default organization created.")
        else:
            logger.info("✅ Default organization already exists.")
        
        session.commit()
        session.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create default organization: {e}")
        return False

def step3_add_org_id_to_crawls():
    """Step 3: Add org_id to crawls table."""
    try:
        database_url = get_database_url()
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        logger.info("Step 3: Adding org_id to crawls table...")
        
        # Check if column exists
        result = session.execute(text("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'crawls' AND column_name = 'org_id';
        """)).fetchone()
        
        if not result:
            session.execute(text("ALTER TABLE crawls ADD COLUMN org_id VARCHAR;"))
            logger.info("✅ Added org_id column to crawls.")
        else:
            logger.info("✅ org_id column already exists in crawls.")
        
        # Update existing records
        session.execute(text("""
            UPDATE crawls SET org_id = 'org_default_migration' WHERE org_id IS NULL;
        """))
        
        updated = session.execute(text("SELECT COUNT(*) FROM crawls WHERE org_id = 'org_default_migration';")).scalar()
        logger.info(f"✅ Updated {updated} crawl records with default org_id.")
        
        session.commit()
        session.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to update crawls table: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        step = sys.argv[1]
        if step == "test":
            test_connection()
        elif step == "1":
            step1_create_organizations_table()
        elif step == "2":
            step2_create_default_org()
        elif step == "3":
            step3_add_org_id_to_crawls()
        else:
            print("Usage: python simple_migration.py [test|1|2|3]")
    else:
        print("Running all steps...")
        if test_connection():
            step1_create_organizations_table()
            step2_create_default_org()
            step3_add_org_id_to_crawls()
            print("✅ Migration completed!")
