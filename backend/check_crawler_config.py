#!/usr/bin/env python3
"""
Check and configure crawler engine selection.
"""

import os
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_crawler_configuration():
    """Check current crawler configuration and environment."""
    
    logger.info("🔍 Checking crawler configuration...")
    
    # Check environment variables
    crawler_engine = os.getenv('CRAWLER_ENGINE', 'not_set')
    firecrawl_key = os.getenv('FIRECRAWL_API_KEY', 'not_set')
    scrapingbee_key = os.getenv('SCRAPINGBEE_API_KEY', 'not_set')
    
    logger.info(f"📋 Current configuration:")
    logger.info(f"   CRAWLER_ENGINE: {crawler_engine}")
    logger.info(f"   FIRECRAWL_API_KEY: {'✅ Set' if firecrawl_key != 'not_set' else '❌ Not set'}")
    logger.info(f"   SCRAPINGBEE_API_KEY: {'✅ Set' if scrapingbee_key != 'not_set' else '❌ Not set'}")
    
    # Test Firecrawl availability
    try:
        from crawler.firecrawl_engine import FirecrawlCrawler
        logger.info("✅ Firecrawl engine available")
        firecrawl_available = True
    except Exception as e:
        logger.error(f"❌ Firecrawl engine not available: {e}")
        firecrawl_available = False
    
    # Determine which engine will be used
    crawler_engine_actual = crawler_engine if crawler_engine != 'not_set' else 'firecrawl'  # Default after our fix
    
    logger.info(f"\n🎯 Engine selection logic:")
    
    if crawler_engine_actual == 'firecrawl' and firecrawl_available:
        logger.info("✅ Will use: Firecrawl")
    elif crawler_engine_actual == 'scrapingbee' and scrapingbee_key != 'not_set':
        logger.info("🐝 Will use: ScrapingBee")
    else:
        logger.info("🕷️ Will use: Playwright (fallback)")
    
    # Recommendations
    logger.info(f"\n💡 Recommendations:")
    
    if crawler_engine_actual != 'firecrawl':
        logger.info("   🔧 To force Firecrawl: export CRAWLER_ENGINE=firecrawl")
    
    if not firecrawl_available:
        logger.info("   🔧 To enable Firecrawl: Fix import issues in firecrawl_engine.py")
    
    if firecrawl_key == 'not_set':
        logger.info("   🔧 To use Firecrawl: Set FIRECRAWL_API_KEY environment variable")
    
    return {
        'engine': crawler_engine_actual,
        'firecrawl_available': firecrawl_available,
        'firecrawl_key_set': firecrawl_key != 'not_set',
        'scrapingbee_key_set': scrapingbee_key != 'not_set'
    }

def set_crawler_to_firecrawl():
    """Set environment to use Firecrawl."""
    logger.info("🔧 Setting CRAWLER_ENGINE to firecrawl...")
    
    # For current session
    os.environ['CRAWLER_ENGINE'] = 'firecrawl'
    
    # Show how to set permanently
    logger.info("✅ CRAWLER_ENGINE set to 'firecrawl' for current session")
    logger.info("\n💾 To make this permanent, add to your environment:")
    logger.info("   export CRAWLER_ENGINE=firecrawl")
    logger.info("   # Or add to your .env file:")
    logger.info("   echo 'CRAWLER_ENGINE=firecrawl' >> .env")

if __name__ == "__main__":
    config = check_crawler_configuration()
    
    if config['engine'] != 'firecrawl':
        logger.info("\n🔄 Setting crawler to use Firecrawl...")
        set_crawler_to_firecrawl()
        
        # Re-check
        logger.info("\n🔍 Re-checking configuration...")
        check_crawler_configuration()
