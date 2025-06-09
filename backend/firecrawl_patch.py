"""
Fix for Firecrawl Pydantic v2 compatibility issue.
Patches the ChangeTrackingData class to avoid the 'json' field name conflict.
"""
import sys
import logging

logger = logging.getLogger(__name__)

def patch_firecrawl_pydantic():
    """Patch Firecrawl to work with Pydantic v2."""
    try:
        # Import firecrawl module
        import firecrawl.firecrawl as fc_module
        
        # Get the original ChangeTrackingData class
        original_class = fc_module.ChangeTrackingData
        
        # Create a new class with fixed field names
        from pydantic import BaseModel, Field
        from typing import Optional, Dict, Any
        
        class FixedChangeTrackingData(BaseModel):
            """Fixed version of ChangeTrackingData without field name conflicts."""
            # Rename 'json' field to 'json_data' to avoid shadowing
            json_data: Optional[Dict[str, Any]] = Field(None, alias='json')
            # Keep other fields as they were
            
            class Config:
                allow_population_by_field_name = True
        
        # Replace the problematic class
        fc_module.ChangeTrackingData = FixedChangeTrackingData
        
        logger.info("✅ Firecrawl Pydantic compatibility patch applied successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to patch Firecrawl: {str(e)}")
        return False

def import_firecrawl_with_patch():
    """Import Firecrawl with automatic patching."""
    try:
        # First, try to patch the module
        patch_firecrawl_pydantic()
        
        # Then import FirecrawlApp
        from firecrawl import FirecrawlApp
        logger.info("🔥 Firecrawl imported successfully with patch")
        return FirecrawlApp, True
        
    except Exception as e:
        logger.error(f"❌ Firecrawl import failed even with patch: {str(e)}")
        return None, False

if __name__ == "__main__":
    # Test the patch
    app, success = import_firecrawl_with_patch()
    if success:
        print("✅ Firecrawl patch successful!")
    else:
        print("❌ Firecrawl patch failed!")
