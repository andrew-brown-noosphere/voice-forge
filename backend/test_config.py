#!/usr/bin/env python3
"""
Test script to check the actual behavior of CrawlConfig
"""

import sys
import json
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from api.models import CrawlConfig, CrawlRequest

print("🔍 Testing CrawlConfig Behavior")
print("=" * 50)

# Test 1: Default configuration
print("1. Default CrawlConfig:")
default_config = CrawlConfig()
print(f"   max_pages: {default_config.max_pages}")
print(f"   max_depth: {default_config.max_depth}")
print(f"   JSON: {default_config.json()}")
print()

# Test 2: Config with explicit max_pages
print("2. CrawlConfig with max_pages=60:")
custom_config = CrawlConfig(max_pages=60)
print(f"   max_pages: {custom_config.max_pages}")
print(f"   JSON: {custom_config.json()}")
print()

# Test 3: Config from dict (simulating API request)
print("3. CrawlConfig from dict with max_pages=60:")
config_dict = {"max_pages": 60, "max_depth": 3}
dict_config = CrawlConfig(**config_dict)
print(f"   max_pages: {dict_config.max_pages}")
print(f"   JSON: {dict_config.json()}")
print()

# Test 4: CrawlRequest with custom config
print("4. CrawlRequest with custom config:")
request_data = {
    "domain": "example.com",
    "config": {
        "max_pages": 60,
        "max_depth": 3
    }
}
crawl_request = CrawlRequest(**request_data)
print(f"   config.max_pages: {crawl_request.config.max_pages}")
print(f"   JSON: {crawl_request.json()}")
print()

# Test 5: What happens with validation
print("5. Testing validation limits:")
try:
    # Try to create a config with a very high max_pages
    high_config = CrawlConfig(max_pages=1000)
    print(f"   max_pages=1000 allowed: {high_config.max_pages}")
except Exception as e:
    print(f"   max_pages=1000 failed: {e}")

try:
    # Try to create a config with max_depth > 10
    deep_config = CrawlConfig(max_depth=15)
    print(f"   max_depth=15 allowed: {deep_config.max_depth}")
except Exception as e:
    print(f"   max_depth=15 failed: {e}")

print()
print("🔍 Summary:")
print(f"• Default max_pages: {CrawlConfig().max_pages} (None = unlimited)")
print(f"• Default max_depth: {CrawlConfig().max_depth}")
print("• No obvious validation limits on max_pages")
print("• The 25-page limit is likely coming from elsewhere")
