"""
Database migration script to add multi-tenancy support to VoiceForge.
This script will add the necessary tables and columns for organization-based isolation.
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import logging

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_url():
    """Get database URL from environment."""
    return os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/voice_forge")

def run_migration():
    """Run the migration to add multi-tenancy support."""
    
    # Create database connection
    database_url = get_database_url()
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        logger.info("Starting multi-tenancy migration...")
        
        # Step 1: Create new tables
        logger.info("Creating new tables...")
        
        # Create organizations table
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS organizations (
                id VARCHAR NOT NULL PRIMARY KEY,
                name VARCHAR NOT NULL,
                slug VARCHAR NOT NULL UNIQUE,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP,
                max_users INTEGER DEFAULT 5,
                max_content_items INTEGER DEFAULT 1000,
                max_crawls_per_month INTEGER DEFAULT 10,
                features JSONB DEFAULT '{}'
            );
        """))
        
        # Create users table
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id VARCHAR NOT NULL PRIMARY KEY,
                org_id VARCHAR NOT NULL REFERENCES organizations(id),
                email VARCHAR NOT NULL,
                first_name VARCHAR,
                last_name VARCHAR,
                role VARCHAR DEFAULT 'member',
                created_at TIMESTAMP NOT NULL,
                last_login TIMESTAMP
            );
        """))
        
        # Create usage_metrics table
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS usage_metrics (
                id VARCHAR NOT NULL PRIMARY KEY,
                org_id VARCHAR NOT NULL REFERENCES organizations(id),
                period_start TIMESTAMP NOT NULL,
                period_end TIMESTAMP NOT NULL,
                crawls_count INTEGER DEFAULT 0,
                content_items_count INTEGER DEFAULT 0,
                content_generations_count INTEGER DEFAULT 0,
                api_calls_count INTEGER DEFAULT 0,
                storage_used FLOAT DEFAULT 0.0,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP
            );
        """))
        
        logger.info("New tables created successfully.")
        
        # Step 2: Add org_id columns to existing tables
        logger.info("Adding org_id columns to existing tables...")
        
        # Check if org_id columns already exist before adding them
        tables_to_modify = ['crawls', 'contents', 'content_chunks', 'marketing_templates']
        
        for table in tables_to_modify:
            # Check if org_id column exists
            result = session.execute(text(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table}' AND column_name = 'org_id';
            """)).fetchone()
            
            if not result:
                logger.info(f"Adding org_id column to {table}...")
                session.execute(text(f"""
                    ALTER TABLE {table} ADD COLUMN org_id VARCHAR;
                """))
            else:
                logger.info(f"org_id column already exists in {table}, skipping...")
        
        # Step 3: Create a default organization for existing data
        logger.info("Creating default organization for existing data...")
        
        default_org_id = "org_default_migration"
        default_org_name = "Default Organization"
        default_org_slug = "default-org"
        
        # Check if default org already exists
        existing_org = session.execute(text("""
            SELECT id FROM organizations WHERE id = :org_id
        """), {"org_id": default_org_id}).fetchone()
        
        if not existing_org:
            session.execute(text("""
                INSERT INTO organizations (id, name, slug, created_at, max_users, max_content_items, max_crawls_per_month)
                VALUES (:id, :name, :slug, NOW(), 10, 5000, 50)
            """), {
                "id": default_org_id,
                "name": default_org_name,
                "slug": default_org_slug
            })
            logger.info("Default organization created.")
        else:
            logger.info("Default organization already exists.")
        
        # Step 4: Update existing records with default org_id
        logger.info("Updating existing records with default organization...")
        
        for table in tables_to_modify:
            # Update only records where org_id is NULL
            result = session.execute(text(f"""
                UPDATE {table} 
                SET org_id = :org_id 
                WHERE org_id IS NULL
            """), {"org_id": default_org_id})
            
            updated_count = result.rowcount
            logger.info(f"Updated {updated_count} records in {table} with default org_id.")
        
        # Step 5: Add NOT NULL constraints and foreign keys
        logger.info("Adding constraints...")
        
        for table in tables_to_modify:
            try:
                # Add NOT NULL constraint
                session.execute(text(f"""
                    ALTER TABLE {table} ALTER COLUMN org_id SET NOT NULL;
                """))
                
                # Add foreign key constraint
                session.execute(text(f"""
                    ALTER TABLE {table} 
                    ADD CONSTRAINT fk_{table}_org_id 
                    FOREIGN KEY (org_id) REFERENCES organizations(id);
                """))
                
                logger.info(f"Constraints added to {table}.")
                
            except Exception as e:
                logger.warning(f"Could not add constraints to {table}: {e}")
                # Continue with other tables
        
        # Step 6: Create indexes for performance
        logger.info("Creating indexes for performance...")
        
        indexes = [
            ("CREATE INDEX IF NOT EXISTS ix_users_org_id ON users(org_id);", "users org_id"),
            ("CREATE INDEX IF NOT EXISTS ix_crawls_org_id ON crawls(org_id);", "crawls org_id"),
            ("CREATE INDEX IF NOT EXISTS ix_crawls_org_id_domain ON crawls(org_id, domain);", "crawls org_id + domain"),
            ("CREATE INDEX IF NOT EXISTS ix_contents_org_id ON contents(org_id);", "contents org_id"),
            ("CREATE INDEX IF NOT EXISTS ix_contents_org_id_domain ON contents(org_id, domain);", "contents org_id + domain"),
            ("CREATE INDEX IF NOT EXISTS ix_contents_org_id_content_type ON contents(org_id, content_type);", "contents org_id + content_type"),
            ("CREATE INDEX IF NOT EXISTS ix_content_chunks_org_id ON content_chunks(org_id);", "content_chunks org_id"),
            ("CREATE INDEX IF NOT EXISTS ix_content_chunks_org_id_content_id ON content_chunks(org_id, content_id);", "content_chunks org_id + content_id"),
            ("CREATE INDEX IF NOT EXISTS ix_marketing_templates_org_id ON marketing_templates(org_id);", "marketing_templates org_id"),
            ("CREATE INDEX IF NOT EXISTS ix_marketing_templates_org_id_platform ON marketing_templates(org_id, platform);", "marketing_templates org_id + platform"),
            ("CREATE INDEX IF NOT EXISTS ix_usage_metrics_org_id ON usage_metrics(org_id);", "usage_metrics org_id"),
            ("CREATE INDEX IF NOT EXISTS ix_usage_metrics_org_id_period ON usage_metrics(org_id, period_start, period_end);", "usage_metrics org_id + period"),
        ]
        
        for sql, description in indexes:
            try:
                session.execute(text(sql))
                logger.info(f"Created index: {description}")
            except Exception as e:
                logger.warning(f"Could not create index for {description}: {e}")
        
        # Step 7: Add created_by columns where missing
        logger.info("Adding created_by columns...")
        
        tables_with_created_by = ['crawls', 'marketing_templates']
        
        for table in tables_with_created_by:
            # Check if created_by column exists
            result = session.execute(text(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table}' AND column_name = 'created_by';
            """)).fetchone()
            
            if not result:
                logger.info(f"Adding created_by column to {table}...")
                session.execute(text(f"""
                    ALTER TABLE {table} ADD COLUMN created_by VARCHAR REFERENCES users(id);
                """))
            else:
                logger.info(f"created_by column already exists in {table}, skipping...")
        
        # Commit all changes
        session.commit()
        logger.info("Migration completed successfully!")
        
        # Step 8: Verify migration
        logger.info("Verifying migration...")
        
        # Check organization count
        org_count = session.execute(text("SELECT COUNT(*) FROM organizations")).scalar()
        logger.info(f"Organizations in database: {org_count}")
        
        # Check that all content has org_id
        for table in tables_to_modify:
            null_count = session.execute(text(f"SELECT COUNT(*) FROM {table} WHERE org_id IS NULL")).scalar()
            total_count = session.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            logger.info(f"{table}: {total_count} total records, {null_count} without org_id")
        
        logger.info("Migration verification completed!")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    run_migration()
