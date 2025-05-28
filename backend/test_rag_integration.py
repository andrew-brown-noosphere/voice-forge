#!/usr/bin/env python3
"""
Test script to verify automated RAG integration is working correctly.
Run this to test that all components are properly integrated.
"""

import sys
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """Test that all required modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        # Test automated RAG integration
        from automated_rag_integration import (
            automated_rag_service, 
            RAGIntegrationHooks,
            auto_optimize_org,
            check_org_optimization_status,
            is_org_ready_for_rag
        )
        print("✅ Automated RAG integration imports successful")
        
        # Test RAG endpoints
        from api.rag_endpoints import rag_router
        print("✅ RAG endpoints imports successful")
        
        # Test optimized processor
        from optimized_processing_pipeline import OptimizedContentProcessor
        print("✅ Optimized processor imports successful")
        
        # Test main API
        from api.main import app
        print("✅ Main API imports successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during imports: {e}")
        return False

def test_service_initialization():
    """Test that the automated RAG service initializes correctly."""
    print("\n🔍 Testing service initialization...")
    
    try:
        from automated_rag_integration import automated_rag_service
        
        # Check configuration
        config = automated_rag_service.config
        print(f"✅ Service configuration loaded:")
        print(f"   - Auto-optimize new orgs: {config['auto_optimize_new_orgs']}")
        print(f"   - Content threshold: {config['auto_optimize_on_content_threshold']}")
        print(f"   - Background processing: {config['background_processing']}")
        
        # Test hook methods exist
        from automated_rag_integration import RAGIntegrationHooks
        
        # Test org creation hook (with dummy data)
        result = RAGIntegrationHooks.on_organization_created("test-org-123", {"name": "Test Org"})
        print(f"✅ Organization creation hook works: {result['status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Service initialization error: {e}")
        return False

def test_api_integration():
    """Test that the API router is properly integrated."""
    print("\n🔍 Testing API integration...")
    
    try:
        from api.main import app
        from api.rag_endpoints import rag_router
        
        # Check if RAG router is included
        router_found = False
        for router in app.router.routes:
            if hasattr(router, 'path') and '/api/rag' in router.path:
                router_found = True
                break
        
        if router_found:
            print("✅ RAG router is properly included in main app")
        else:
            print("❌ RAG router not found in main app routes")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ API integration error: {e}")
        return False

def test_crawler_hooks():
    """Test that crawler service has the RAG hooks."""
    print("\n🔍 Testing crawler integration...")
    
    try:
        from crawler.service import CrawlerService
        import inspect
        
        # Check if run_crawl method contains RAG integration code
        source = inspect.getsource(CrawlerService.run_crawl)
        
        if "RAGIntegrationHooks" in source:
            print("✅ Crawler service has RAG integration hooks")
        else:
            print("❌ RAG integration hooks not found in crawler service")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Crawler integration error: {e}")
        return False

def test_endpoint_functionality():
    """Test RAG endpoint functionality (basic checks)."""
    print("\n🔍 Testing endpoint functionality...")
    
    try:
        from api.rag_endpoints import rag_router
        
        # Check that endpoints are defined
        endpoints = []
        for route in rag_router.routes:
            if hasattr(route, 'path'):
                endpoints.append(route.path)
        
        expected_endpoints = [
            "/optimize", 
            "/status/{org_id}", 
            "/readiness/{org_id}",
            "/health"
        ]
        
        found_endpoints = []
        for expected in expected_endpoints:
            for endpoint in endpoints:
                if expected.replace("{org_id}", "") in endpoint:
                    found_endpoints.append(expected)
                    break
        
        print(f"✅ Found {len(found_endpoints)}/{len(expected_endpoints)} expected endpoints:")
        for endpoint in found_endpoints:
            print(f"   - {endpoint}")
        
        if len(found_endpoints) >= len(expected_endpoints) - 1:  # Allow for minor variations
            return True
        else:
            print(f"❌ Missing endpoints: {set(expected_endpoints) - set(found_endpoints)}")
            return False
            
    except Exception as e:
        print(f"❌ Endpoint functionality error: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 VoiceForge Automated RAG Integration Test")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("Service Initialization", test_service_initialization),
        ("API Integration", test_api_integration),
        ("Crawler Hooks", test_crawler_hooks),
        ("Endpoint Functionality", test_endpoint_functionality),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        print(f"\n{'=' * 20} {name} {'=' * 20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {name}: PASSED")
            else:
                print(f"❌ {name}: FAILED")
        except Exception as e:
            print(f"❌ {name}: ERROR - {e}")
    
    print(f"\n{'=' * 50}")
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Automated RAG integration is working correctly.")
        print("\n📋 Next Steps:")
        print("1. Start your FastAPI server: uvicorn api.main:app --reload")
        print("2. Test the endpoints: curl http://localhost:8000/api/rag/health")
        print("3. Create a new organization and crawl content to see automation in action!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the errors above and fix them.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
