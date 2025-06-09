#!/usr/bin/env python3
"""
Test Firecrawl API format to determine correct parameters.
"""

import os
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_firecrawl_api_formats():
    """Test different Firecrawl API formats to find the working one."""
    
    api_key = os.getenv('FIRECRAWL_API_KEY')
    if not api_key:
        logger.error("❌ FIRECRAWL_API_KEY not set")
        return
    
    try:
        from firecrawl import FirecrawlApp
        
        firecrawl = FirecrawlApp(api_key=api_key)
        test_url = "https://buf.build"
        
        logger.info(f"🧪 Testing Firecrawl API formats with {test_url}")
        
        # Test 1: Simple scrape with minimal options
        logger.info("\\n📋 Test 1: Simple scrape with minimal options")
        try:
            result = firecrawl.scrape_url(test_url)\n            if result and hasattr(result, 'content'):\n                logger.info(f\"✅ Simple scrape worked: {len(result.content)} chars\")\n            else:\n                logger.info(\"❌ Simple scrape failed\")\n        except Exception as e:\n            logger.info(f\"❌ Simple scrape error: {e}\")\n        \n        # Test 2: Scrape with direct parameters (v1 format)\n        logger.info(\"\\n📋 Test 2: Scrape with direct parameters\")\n        try:\n            result = firecrawl.scrape_url(\n                test_url,\n                extractorOptions={\"mode\": \"markdown\"},\n                includeHtml=True\n            )\n            if result and hasattr(result, 'content'):\n                logger.info(f\"✅ Direct params scrape worked: {len(result.content)} chars\")\n            else:\n                logger.info(\"❌ Direct params scrape failed\")\n        except Exception as e:\n            logger.info(f\"❌ Direct params scrape error: {e}\")\n        \n        # Test 3: Scrape with formats parameter (some APIs need this)\n        logger.info(\"\\n📋 Test 3: Scrape with formats parameter\")\n        try:\n            result = firecrawl.scrape_url(\n                test_url,\n                formats=[\"markdown\", \"html\"]\n            )\n            if result and hasattr(result, 'content'):\n                logger.info(f\"✅ Formats scrape worked: {len(result.content)} chars\")\n            else:\n                logger.info(\"❌ Formats scrape failed\")\n        except Exception as e:\n            logger.info(f\"❌ Formats scrape error: {e}\")\n        \n        # Test 4: Simple crawl with minimal options\n        logger.info(\"\\n📋 Test 4: Simple crawl (1 page only)\")\n        try:\n            result = firecrawl.crawl_url(\n                test_url,\n                limit=1,\n                maxDepth=1\n            )\n            if result and hasattr(result, 'data') and result.data:\n                logger.info(f\"✅ Simple crawl worked: {len(result.data)} pages\")\n            else:\n                logger.info(\"❌ Simple crawl failed\")\n        except Exception as e:\n            logger.info(f\"❌ Simple crawl error: {e}\")\n            \n        # Test 5: Check what methods are available\n        logger.info(\"\\n📋 Test 5: Available FirecrawlApp methods\")\n        methods = [attr for attr in dir(firecrawl) if not attr.startswith('_')]\n        logger.info(f\"Available methods: {methods}\")\n        \n        # Test 6: Check API documentation if available\n        logger.info(\"\\n📋 Test 6: Checking for API version info\")\n        if hasattr(firecrawl, '_version') or hasattr(firecrawl, 'version'):\n            version = getattr(firecrawl, '_version', None) or getattr(firecrawl, 'version', None)\n            logger.info(f\"API version: {version}\")\n        else:\n            logger.info(\"No version info found\")\n            \n    except ImportError as e:\n        logger.error(f\"❌ Failed to import Firecrawl: {e}\")\n    except Exception as e:\n        logger.error(f\"❌ Unexpected error: {e}\")\n\ndef test_direct_requests():\n    \"\"\"Test Firecrawl using direct HTTP requests to understand API format.\"\"\"\n    import requests\n    \n    api_key = os.getenv('FIRECRAWL_API_KEY')\n    if not api_key:\n        logger.error(\"❌ FIRECRAWL_API_KEY not set\")\n        return\n    \n    logger.info(\"\\n🌐 Testing direct HTTP requests to Firecrawl API\")\n    \n    base_url = \"https://api.firecrawl.dev\"\n    headers = {\n        \"Authorization\": f\"Bearer {api_key}\",\n        \"Content-Type\": \"application/json\"\n    }\n    \n    # Test scrape endpoint\n    logger.info(\"\\n📋 Testing /v1/scrape endpoint\")\n    try:\n        payload = {\n            \"url\": \"https://buf.build\",\n            \"formats\": [\"markdown\"]\n        }\n        \n        response = requests.post(\n            f\"{base_url}/v1/scrape\",\n            json=payload,\n            headers=headers,\n            timeout=30\n        )\n        \n        logger.info(f\"Status: {response.status_code}\")\n        if response.status_code == 200:\n            data = response.json()\n            logger.info(f\"✅ Direct scrape worked: {len(str(data))} chars response\")\n            if 'data' in data and 'markdown' in data['data']:\n                logger.info(f\"✅ Got markdown content: {len(data['data']['markdown'])} chars\")\n        else:\n            logger.info(f\"❌ Direct scrape failed: {response.text}\")\n            \n    except Exception as e:\n        logger.info(f\"❌ Direct scrape error: {e}\")\n\nif __name__ == \"__main__\":\n    logger.info(\"🧪 Starting Firecrawl API format tests\")\n    logger.info(\"=\" * 60)\n    \n    test_firecrawl_api_formats()\n    test_direct_requests()\n    \n    logger.info(\"\\n\" + \"=\" * 60)\n    logger.info(\"🎯 Based on the results above, we can determine the correct API format\")\n