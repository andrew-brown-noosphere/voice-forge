"""
Complete the remaining migration steps.
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

def step4_update_contents_table():
    """Step 4: Add org_id to contents table."""
    try:
        database_url = get_database_url()
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        logger.info("Step 4: Adding org_id to contents table...")
        
        # Check if column exists
        result = session.execute(text("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'contents' AND column_name = 'org_id';
        """)).fetchone()
        
        if not result:
            session.execute(text("ALTER TABLE contents ADD COLUMN org_id VARCHAR;"))
            logger.info("✅ Added org_id column to contents.")
        else:
            logger.info("✅ org_id column already exists in contents.")
        
        # Update existing records
        session.execute(text("""
            UPDATE contents SET org_id = 'org_default_migration' WHERE org_id IS NULL;
        """))
        
        updated = session.execute(text("SELECT COUNT(*) FROM contents WHERE org_id = 'org_default_migration';")).scalar()
        logger.info(f"✅ Updated {updated} content records with default org_id.")
        
        session.commit()
        session.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to update contents table: {e}")
        return False

def step5_update_content_chunks_table():
    """Step 5: Add org_id to content_chunks table."""
    try:
        database_url = get_database_url()
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        logger.info("Step 5: Adding org_id to content_chunks table...")
        
        # Check if column exists
        result = session.execute(text("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'content_chunks' AND column_name = 'org_id';
        """)).fetchone()
        
        if not result:
            session.execute(text("ALTER TABLE content_chunks ADD COLUMN org_id VARCHAR;"))
            logger.info("✅ Added org_id column to content_chunks.")
        else:
            logger.info("✅ org_id column already exists in content_chunks.")
        
        # Update existing records
        session.execute(text("""
            UPDATE content_chunks SET org_id = 'org_default_migration' WHERE org_id IS NULL;
        """))
        
        updated = session.execute(text("SELECT COUNT(*) FROM content_chunks WHERE org_id = 'org_default_migration';")).scalar()
        logger.info(f"✅ Updated {updated} content chunk records with default org_id.")
        
        session.commit()
        session.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to update content_chunks table: {e}")
        return False

def step6_update_marketing_templates_table():
    """Step 6: Add org_id to marketing_templates table (if it exists)."""
    try:
        database_url = get_database_url()
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        logger.info("Step 6: Adding org_id to marketing_templates table...")
        
        # Check if table exists
        table_exists = session.execute(text("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_name = 'marketing_templates';
        """)).fetchone()
        
        if not table_exists:
            logger.info("ℹ️ marketing_templates table doesn't exist yet, skipping.")
            session.close()
            return True
        
        # Check if column exists
        result = session.execute(text("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'marketing_templates' AND column_name = 'org_id';
        """)).fetchone()
        
        if not result:
            session.execute(text("ALTER TABLE marketing_templates ADD COLUMN org_id VARCHAR;"))
            logger.info("✅ Added org_id column to marketing_templates.")
        else:
            logger.info("✅ org_id column already exists in marketing_templates.")
        
        # Update existing records
        session.execute(text("""
            UPDATE marketing_templates SET org_id = 'org_default_migration' WHERE org_id IS NULL;
        """))
        
        updated = session.execute(text("SELECT COUNT(*) FROM marketing_templates WHERE org_id = 'org_default_migration';")).scalar()
        logger.info(f"✅ Updated {updated} marketing template records with default org_id.")
        
        session.commit()
        session.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to update marketing_templates table: {e}")
        return False

def step7_create_users_table():
    """Step 7: Create users table."""
    try:
        database_url = get_database_url()
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        logger.info("Step 7: Creating users table...")
        
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id VARCHAR NOT NULL PRIMARY KEY,
                org_id VARCHAR NOT NULL REFERENCES organizations(id),
                email VARCHAR NOT NULL,
                first_name VARCHAR,
                last_name VARCHAR,
                role VARCHAR DEFAULT 'member',
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                last_login TIMESTAMP
            );
        """))
        
        session.commit()
        session.close()
        logger.info("✅ Users table created successfully.")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create users table: {e}")
        return False

def step8_create_indexes():
    """Step 8: Create performance indexes."""
    try:
        database_url = get_database_url()
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        logger.info("Step 8: Creating performance indexes...")
        
        indexes = [
            ("CREATE INDEX IF NOT EXISTS ix_crawls_org_id ON crawls(org_id);", "crawls org_id"),
            ("CREATE INDEX IF NOT EXISTS ix_contents_org_id ON contents(org_id);", "contents org_id"),
            ("CREATE INDEX IF NOT EXISTS ix_content_chunks_org_id ON content_chunks(org_id);", "content_chunks org_id"),
            ("CREATE INDEX IF NOT EXISTS ix_users_org_id ON users(org_id);", "users org_id"),
        ]
        
        for sql, description in indexes:
            try:
                session.execute(text(sql))
                logger.info(f"✅ Created index: {description}")
            except Exception as e:
                logger.warning(f"⚠️ Could not create index for {description}: {e}")
        
        session.commit()
        session.close()
        logger.info("✅ Indexes created successfully.")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create indexes: {e}")
        return False

def check_migration_status():
    """Check the current migration status."""
    try:
        database_url = get_database_url()
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        logger.info("🔍 Checking migration status...")
        
        # Check organizations
        org_count = session.execute(text("SELECT COUNT(*) FROM organizations;")).scalar()
        logger.info(f"📊 Organizations: {org_count}")
        
        # Check tables with org_id
        tables = ['crawls', 'contents', 'content_chunks']
        for table in tables:
            try:
                total = session.execute(text(f"SELECT COUNT(*) FROM {table};")).scalar()
                with_org = session.execute(text(f"SELECT COUNT(*) FROM {table} WHERE org_id IS NOT NULL;")).scalar()
                logger.info(f"📊 {table}: {with_org}/{total} records have org_id")
            except Exception as e:
                logger.warning(f"⚠️ Could not check {table}: {e}")
        
        session.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to check migration status: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        step = sys.argv[1]
        if step == "4":
            step4_update_contents_table()
        elif step == "5":
            step5_update_content_chunks_table()
        elif step == "6":
            step6_update_marketing_templates_table()
        elif step == "7":
            step7_create_users_table()
        elif step == "8":
            step8_create_indexes()
        elif step == "status":
            check_migration_status()
        else:
            print("Usage: python complete_migration.py [4|5|6|7|8|status]")
    else:
        print("Running remaining migration steps...")
        step4_update_contents_table()
        step5_update_content_chunks_table()
        step6_update_marketing_templates_table()
        step7_create_users_table()
        step8_create_indexes()
        check_migration_status()
        print("🎉 Complete migration finished!")
