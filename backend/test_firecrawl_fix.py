#!/usr/bin/env python3
"""
Test script to verify Firecrawl imports work after fixing the Pydantic conflicts.
"""

try:
    print("🔥 Testing Firecrawl import...")
    from firecrawl import FirecrawlApp
    print("✅ Firecrawl imported successfully!")
    
    # Test basic initialization
    print("🔥 Testing FirecrawlApp initialization...")
    app = FirecrawlApp(api_key="dummy_key_for_test")
    print("✅ FirecrawlApp initialized successfully!")
    
    print("🎉 All tests passed! Firecrawl is working correctly.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
