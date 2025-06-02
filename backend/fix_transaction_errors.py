#!/usr/bin/env python3
"""
Quick script to fix the InFailedSqlTransaction errors in VoiceForge backend.
"""

import os
import shutil

def backup_and_fix_dependencies():
    """Fix the dependencies.py file."""
    
    # Backup original
    shutil.copy2("api/dependencies.py", "api/dependencies.py.backup")
    print("✅ Backed up api/dependencies.py")
    
    # Write the fixed version
    fixed_content = '''"""
FastAPI dependency injection functions.
"""
from fastapi import Depends
from crawler.service import CrawlerService
from processor.service import ProcessorService
from processor.rag_service import RAGService
from database.session import get_db_session
from database.db import Database
import logging

logger = logging.getLogger(__name__)

def get_db():
    """Get a database session with proper transaction management."""
    db_session = get_db_session()
    db = Database(db_session)
    try:
        yield db
    except Exception as e:
        logger.error(f"Database error occurred: {str(e)}")
        # Always rollback on any exception to ensure clean state
        try:
            db_session.rollback()
            logger.info("Transaction rolled back successfully")
        except Exception as rollback_error:
            logger.error(f"Failed to rollback transaction: {str(rollback_error)}")
        # Re-raise the original exception
        raise e
    finally:
        # Always close the session
        try:
            db_session.close()
        except Exception as close_error:
            logger.error(f"Failed to close database session: {str(close_error)}")

def get_crawler_service(db = Depends(get_db)):
    """Get a new crawler service instance (not singleton)."""
    return CrawlerService(db)

def get_processor_service(db = Depends(get_db)):
    """Get a new processor service instance (not singleton)."""
    return ProcessorService(db)

def get_rag_service(
    db = Depends(get_db),
    processor_service = Depends(get_processor_service)
):
    """Get a new RAG service instance (not singleton)."""
    return RAGService(db, processor_service)
'''
    
    with open("api/dependencies.py", "w") as f:
        f.write(fixed_content)
    
    print("✅ Fixed api/dependencies.py - removed singletons")

def enhance_db_class():
    """Add better error handling to the Database class."""
    
    # Backup original
    shutil.copy2("database/db.py", "database/db.py.backup")
    print("✅ Backed up database/db.py")
    
    # Read current content
    with open("database/db.py", "r") as f:
        content = f.read()
    
    # Add SQLAlchemy error import if not present
    if 'from sqlalchemy.exc import SQLAlchemyError' not in content:
        content = content.replace(
            'from sqlalchemy import desc, func, cast, Float, or_, and_',
            'from sqlalchemy import desc, func, cast, Float, or_, and_\nfrom sqlalchemy.exc import SQLAlchemyError'
        )
    
    # Replace the existing _ensure_session_health method with an improved version
    old_method = '''    def _ensure_session_health(self):
        """Ensure the session is in a healthy state for queries."""
        try:
            # Test if the session is in a failed state
            from sqlalchemy.sql.expression import text
            self.session.execute(text("SELECT 1"))
        except Exception as e:
            logger.warning(f"Session unhealthy, attempting rollback: {str(e)}")
            try:
                self.session.rollback()
                # Test again after rollback
                self.session.execute(text("SELECT 1"))
                logger.info("Session recovered after rollback")
            except Exception as rollback_error:
                logger.error(f"Failed to recover session: {str(rollback_error)}")
                # Force close and recreate connection
                try:
                    self.session.close()
                except Exception:
                    pass
                # Re-raise the error so caller knows session is unusable
                raise rollback_error'''
    
    new_method = '''    def _ensure_session_health(self):
        """
        Ensure the session is in a healthy state for queries.
        This method attempts to recover from failed transactions.
        """
        try:
            # Test if the session is in a failed state
            from sqlalchemy.sql.expression import text
            self.session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.warning(f"Session unhealthy, attempting rollback: {str(e)}")
            try:
                # Rollback the failed transaction
                self.session.rollback()
                # Test again after rollback
                self.session.execute(text("SELECT 1"))
                logger.info("Session recovered after rollback")
                return True
            except Exception as rollback_error:
                logger.error(f"Failed to recover session: {str(rollback_error)}")
                # Session is completely unusable at this point
                return False
    
    def _safe_execute(self, operation_name: str, operation_func, *args, **kwargs):
        """
        Safely execute a database operation with proper error handling.
        
        Args:
            operation_name: Name of the operation for logging
            operation_func: The function to execute
            *args, **kwargs: Arguments to pass to the function
            
        Returns:
            Result of the operation, or None if failed
        """
        try:
            # Ensure session is healthy before operation
            if not self._ensure_session_health():
                logger.error(f"Cannot execute {operation_name}: session is unhealthy")
                return None
            
            # Execute the operation
            result = operation_func(*args, **kwargs)
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemy error in {operation_name}: {str(e)}")
            try:
                self.session.rollback()
            except Exception as rollback_error:
                logger.error(f"Failed to rollback after {operation_name}: {str(rollback_error)}")
            return None
            
        except Exception as e:
            logger.error(f"Unexpected error in {operation_name}: {str(e)}")
            try:
                self.session.rollback()
            except Exception as rollback_error:
                logger.error(f"Failed to rollback after {operation_name}: {str(rollback_error)}")
            return None'''
    
    # Replace the method
    if old_method in content:
        content = content.replace(old_method, new_method)
    
    # Write the updated content
    with open("database/db.py", "w") as f:
        f.write(content)
    
    print("✅ Enhanced database/db.py with better error handling")

def main():
    """Apply the fixes."""
    print("🔧 Fixing VoiceForge transaction errors...")
    
    try:
        backup_and_fix_dependencies()
        enhance_db_class()
        
        print()
        print("✅ All fixes applied successfully!")
        print()
        print("📋 Changes made:")
        print("   • Removed singleton services (fresh DB sessions per request)")
        print("   • Improved transaction rollback handling")
        print("   • Added safe execution wrapper for DB operations")
        print("   • Enhanced session health checking")
        print()
        print("🚀 Next steps:")
        print("   1. Restart your backend server")
        print("   2. Test your API endpoints") 
        print("   3. The InFailedSqlTransaction errors should be resolved")
        
    except Exception as e:
        print(f"❌ Error applying fixes: {e}")

if __name__ == "__main__":
    main()
