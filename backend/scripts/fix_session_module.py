#!/usr/bin/env python
"""
Script to directly fix the database session to ensure it doesn't require next() calls.
"""
import sys
import os
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import importlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def fix_session_module():
    """Fix the database session module to return a session directly."""
    try:
        # Import the module
        import database.session
        
        # Check the current implementation
        try:
            session = database.session.get_db_session()
            if hasattr(session, '__next__'):
                logger.info("Current get_db_session returns a generator. Fixing...")
                
                # Save the original function
                original_get_db_session = database.session.get_db_session
                
                # Create a fixed version
                def fixed_get_db_session():
                    # Fixed version that returns a session directly
                    return next(original_get_db_session())
                
                # Replace the function
                database.session.get_db_session = fixed_get_db_session
                
                # Verify the fix
                new_session = database.session.get_db_session()
                if hasattr(new_session, '__next__'):
                    logger.error("Fix failed. get_db_session still returns a generator.")
                else:
                    logger.info("Fix successful! get_db_session now returns a session directly.")
                    # Test the session
                    if hasattr(new_session, 'query'):
                        logger.info("Session has query method, looks correct.")
                    else:
                        logger.warning("Session doesn't have query method, may not be a valid session.")
            else:
                logger.info("get_db_session already returns a session directly. No fix needed.")
        except Exception as e:
            logger.error(f"Error testing get_db_session: {str(e)}")
    except Exception as e:
        logger.error(f"Error importing database.session: {str(e)}")

def patch_session_module():
    """Create a patched version of the session module."""
    session_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                              'database', 'session.py')
    
    try:
        # Read the current file
        with open(session_path, 'r') as f:
            content = f.read()
        
        # Check if it's already patched
        if 'PATCHED_BY_SCRIPT' in content:
            logger.info("Session module already patched. No changes needed.")
            return
        
        # Create a backup
        backup_path = session_path + '.bak'
        with open(backup_path, 'w') as f:
            f.write(content)
        logger.info(f"Created backup of session module at {backup_path}")
        
        # Examine the content
        if 'def get_db_session():' in content:
            # Look for patterns that indicate it's a generator
            if 'yield session' in content:
                logger.info("Found generator pattern in get_db_session")
                
                # Create patched content
                patched_content = content.replace(
                    'def get_db_session():', 
                    'def _original_get_db_session():'
                )
                
                # Add new function at the end
                patched_content += """

# PATCHED_BY_SCRIPT
def get_db_session():
    # Return a database session directly
    return next(_original_get_db_session())
"""
                
                # Write the patched file
                with open(session_path, 'w') as f:
                    f.write(patched_content)
                
                logger.info(f"Patched session module at {session_path}")
                
                # Reload the module
                import database.session
                importlib.reload(database.session)
                
                logger.info("Reloaded session module")
            else:
                logger.info("get_db_session doesn't appear to be a generator. No changes needed.")
        else:
            logger.warning("Could not find get_db_session in the session module.")
    except Exception as e:
        logger.error(f"Error patching session module: {str(e)}")

if __name__ == "__main__":
    logger.info("Starting session module fix")
    fix_session_module()
    patch_session_module()
    logger.info("Session module fix completed")
