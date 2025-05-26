#!/usr/bin/env python
"""
Script to update the user agent string for the Voice Forge crawler.
"""
import sys
import os
import logging
import re

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def update_user_agent():
    """
    Update the user agent string in the models.py file.
    """
    # Path to the models.py file
    models_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             'api', 'models.py')
    
    try:
        # Read the file
        with open(models_path, 'r') as f:
            content = f.read()
        
        # Create a backup
        backup_path = models_path + '.bak'
        with open(backup_path, 'w') as f:
            f.write(content)
        logger.info(f"Created backup of models.py at {backup_path}")
        
        # Find the user agent line
        old_user_agent = 'user_agent: str = Field("VoiceForge Crawler (+https://voiceforge.example.com)", description="User agent string")'
        new_user_agent = 'user_agent: str = Field("VoiceForge Researcher (https://voiceforge.voyant.io)", description="User agent string")'
        
        # Replace the user agent
        updated_content = content.replace(old_user_agent, new_user_agent)
        
        # Write the updated file
        with open(models_path, 'w') as f:
            f.write(updated_content)
        
        logger.info("Successfully updated user agent string")
        logger.info("Old: VoiceForge Crawler (+https://voiceforge.example.com)")
        logger.info("New: VoiceForge Researcher (https://voiceforge.voyant.io)")
        
    except Exception as e:
        logger.error(f"Error updating user agent: {str(e)}")

if __name__ == "__main__":
    logger.info("Starting user agent update")
    update_user_agent()
    logger.info("User agent update completed")
