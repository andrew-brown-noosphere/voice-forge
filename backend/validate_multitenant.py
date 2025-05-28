#!/usr/bin/env python3
"""
Multi-tenant validation script for VoiceForge backend.
Tests that all service methods properly accept and use org_id parameters.
"""

import sys
import os
import importlib.util

def test_service_signatures():
    """Test that all service methods have the correct multi-tenant signatures."""
    
    print("🧪 Testing Multi-Tenant Service Signatures...")
    print("=" * 50)
    
    # Test CrawlerService
    print("📍 Testing CrawlerService...")
    try:
        from crawler.service import CrawlerService
        
        # Check method signatures
        methods_to_check = [
            ('init_crawl', ['crawl_id', 'request', 'org_id']),
            ('run_crawl', ['crawl_id', 'domain', 'config', 'org_id']),
            ('get_crawl_status', ['crawl_id', 'org_id']),
            ('cancel_crawl', ['crawl_id', 'org_id']),
            ('list_crawls', ['limit', 'offset', 'org_id']),
            ('delete_all_crawls', ['org_id'])
        ]
        
        for method_name, expected_params in methods_to_check:
            if hasattr(CrawlerService, method_name):
                method = getattr(CrawlerService, method_name)
                # Get parameter names from function
                import inspect
                sig = inspect.signature(method)
                param_names = list(sig.parameters.keys())
                
                # Check if all expected parameters are present
                missing_params = [p for p in expected_params if p not in param_names]
                if missing_params:
                    print(f"  ❌ {method_name}: Missing parameters: {missing_params}")
                else:
                    print(f"  ✅ {method_name}: Correct signature")
            else:
                print(f"  ❌ {method_name}: Method not found")
                
    except Exception as e:
        print(f"  ❌ CrawlerService import failed: {e}")
    
    # Test ProcessorService
    print("\n📍 Testing ProcessorService...")
    try:
        from processor.service import ProcessorService
        
        methods_to_check = [
            ('process_content', ['content_id', 'org_id']),
            ('get_content', ['content_id', 'org_id']),
            ('search_content', ['query', 'domain', 'content_type', 'limit', 'offset', 'org_id'])
        ]
        
        for method_name, expected_params in methods_to_check:
            if hasattr(ProcessorService, method_name):
                method = getattr(ProcessorService, method_name)
                import inspect
                sig = inspect.signature(method)
                param_names = list(sig.parameters.keys())
                
                missing_params = [p for p in expected_params if p not in param_names]
                if missing_params:
                    print(f"  ❌ {method_name}: Missing parameters: {missing_params}")
                else:
                    print(f"  ✅ {method_name}: Correct signature")
            else:
                print(f"  ❌ {method_name}: Method not found")
                
    except Exception as e:
        print(f"  ❌ ProcessorService import failed: {e}")
    
    # Test RAGService
    print("\n📍 Testing RAGService...")
    try:
        from processor.rag_service import RAGService
        
        methods_to_check = [
            ('search_chunks', ['query', 'domain', 'content_type', 'top_k', 'org_id']),
            ('get_content_chunks', ['content_id', 'org_id']),
            ('process_content_for_rag', ['content_id', 'org_id']),
            ('generate_content', ['query', 'platform', 'tone', 'domain', 'content_type', 'top_k', 'org_id']),
            ('create_template', ['template_data', 'org_id']),
            ('get_template', ['template_id', 'org_id']),
            ('list_templates', ['platform', 'tone', 'purpose', 'limit', 'offset', 'org_id'])
        ]
        
        for method_name, expected_params in methods_to_check:
            if hasattr(RAGService, method_name):
                method = getattr(RAGService, method_name)
                import inspect
                sig = inspect.signature(method)
                param_names = list(sig.parameters.keys())
                
                missing_params = [p for p in expected_params if p not in param_names]
                if missing_params:
                    print(f"  ❌ {method_name}: Missing parameters: {missing_params}")
                else:
                    print(f"  ✅ {method_name}: Correct signature")
            else:
                print(f"  ❌ {method_name}: Method not found")
                
    except Exception as e:
        print(f"  ❌ RAGService import failed: {e}")
    
    # Test Database
    print("\n📍 Testing Database...")
    try:
        from database.db import Database
        
        methods_to_check = [
            ('save_crawl_status', ['status', 'org_id']),
            ('get_crawl_status', ['crawl_id', 'org_id']),
            ('list_crawl_statuses', ['limit', 'offset', 'org_id']),
            ('save_content', ['content_data', 'org_id']),
            ('get_content', ['content_id', 'org_id']),
            ('search_content_by_vector', ['query_embedding', 'domain', 'content_type', 'limit', 'offset', 'org_id']),
            ('get_all_domains', ['org_id']),
            ('store_content_chunks', ['chunks', 'org_id']),
            ('search_chunks_by_vector', ['query_embedding', 'top_k', 'domain', 'content_type', 'org_id']),
            ('get_content_chunks', ['content_id', 'org_id']),
            ('store_template', ['template_data', 'org_id']),
            ('get_template', ['template_id', 'platform', 'tone', 'purpose', 'org_id']),
            ('list_templates', ['platform', 'tone', 'purpose', 'limit', 'offset', 'org_id'])
        ]
        
        for method_name, expected_params in methods_to_check:
            if hasattr(Database, method_name):
                method = getattr(Database, method_name)
                import inspect
                sig = inspect.signature(method)
                param_names = list(sig.parameters.keys())
                
                missing_params = [p for p in expected_params if p not in param_names]
                if missing_params:
                    print(f"  ❌ {method_name}: Missing parameters: {missing_params}")
                else:
                    print(f"  ✅ {method_name}: Correct signature")
            else:
                print(f"  ❌ {method_name}: Method not found")
                
    except Exception as e:
        print(f"  ❌ Database import failed: {e}")

def test_authentication_imports():
    """Test that authentication modules can be imported."""
    
    print("\n🔐 Testing Authentication Imports...")
    print("=" * 50)
    
    try:
        from auth.clerk_auth import get_current_user, get_current_user_with_org, require_org_admin, AuthUser
        print("✅ Authentication modules imported successfully")
        print("✅ get_current_user available")
        print("✅ get_current_user_with_org available") 
        print("✅ require_org_admin available")
        print("✅ AuthUser class available")
    except Exception as e:
        print(f"❌ Authentication import failed: {e}")

def test_model_updates():
    """Test that database models have org_id columns."""
    
    print("\n🗄️ Testing Database Model Updates...")
    print("=" * 50)
    
    try:
        from database.models import Crawl, Content, ContentChunk, MarketingTemplate
        
        # Check each model has org_id
        models_to_check = [
            ('Crawl', Crawl),
            ('Content', Content), 
            ('ContentChunk', ContentChunk),
            ('MarketingTemplate', MarketingTemplate)
        ]
        
        for model_name, model_class in models_to_check:
            if hasattr(model_class, 'org_id'):
                print(f"✅ {model_name}: Has org_id column")
            else:
                print(f"❌ {model_name}: Missing org_id column")
                
    except Exception as e:
        print(f"❌ Model import failed: {e}")

def main():
    """Run all validation tests."""
    
    print("🎯 VoiceForge Multi-Tenant Validation")
    print("=" * 60)
    print("Testing service layer updates for multi-tenancy...")
    print()
    
    # Add current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # Run tests
    test_service_signatures()
    test_authentication_imports()
    test_model_updates()
    
    print("\n" + "=" * 60)
    print("🎉 Multi-tenant validation completed!")
    print()
    print("📝 Summary:")
    print("- All service methods should accept org_id parameters")
    print("- All database queries should filter by org_id")
    print("- Authentication middleware should be available")
    print("- Database models should have org_id columns")
    print()
    print("🚀 If all tests pass, your multi-tenant system is ready!")

if __name__ == "__main__":
    main()
