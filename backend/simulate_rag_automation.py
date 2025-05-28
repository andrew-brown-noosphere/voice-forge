#!/usr/bin/env python3
"""
Simulate automated RAG integration to see it working
"""

import sys
import os
import time
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append('/Users/andrewbrown/Sites/noosphere/github/voice-forge/backend')

def simulate_org_creation():
    """Simulate organization creation and RAG automation"""
    print("🏢 Simulating organization creation...")
    
    try:
        from automated_rag_integration import RAGIntegrationHooks
        
        # Simulate new org creation
        org_id = f"test-org-{int(time.time())}"
        org_data = {
            "name": "Test Organization",
            "created_at": datetime.now().isoformat()
        }
        
        print(f"   Creating org: {org_id}")
        result = RAGIntegrationHooks.on_organization_created(org_id, org_data)
        print(f"   ✅ Hook result: {result}")
        
        return org_id
        
    except Exception as e:
        print(f"   ❌ Error simulating org creation: {e}")
        return None

def simulate_crawl_completion(org_id):
    """Simulate crawl completion and automatic RAG optimization"""
    print(f"\n🕷️ Simulating crawl completion for org {org_id}...")
    
    try:
        from automated_rag_integration import RAGIntegrationHooks
        
        # Simulate crawl completion
        crawl_id = f"crawl-{int(time.time())}"
        crawl_results = {
            "pages_crawled": 15,
            "content_extracted": 12,
            "pages_failed": 0,
            "pages_discovered": 15
        }
        
        print(f"   Crawl ID: {crawl_id}")
        print(f"   Pages crawled: {crawl_results['pages_crawled']}")
        print(f"   Content extracted: {crawl_results['content_extracted']}")
        
        result = RAGIntegrationHooks.on_crawl_completed(crawl_id, org_id, crawl_results)
        print(f"   ✅ Hook result: {result}")
        
        return result
        
    except Exception as e:
        print(f"   ❌ Error simulating crawl completion: {e}")
        return None

def check_optimization_status(org_id):
    """Check the optimization status for an org"""
    print(f"\n📊 Checking optimization status for org {org_id}...")
    
    try:
        from automated_rag_integration import check_org_optimization_status, is_org_ready_for_rag
        
        # Check status
        status = check_org_optimization_status(org_id)
        if status:
            print(f"   Status: {status.get('status', 'unknown')}")
            if status.get('started_at'):
                print(f"   Started: {status['started_at']}")
            if status.get('error'):
                print(f"   Error: {status['error']}")
        else:
            print("   No optimization history found")
        
        # Check readiness
        ready, reason = is_org_ready_for_rag(org_id)
        print(f"   Ready for RAG: {ready}")
        print(f"   Reason: {reason}")
        
        return ready
        
    except Exception as e:
        print(f"   ❌ Error checking optimization status: {e}")
        return False

def test_service_configuration():
    """Test service configuration"""
    print("⚙️ Testing service configuration...")
    
    try:
        from automated_rag_integration import automated_rag_service
        
        config = automated_rag_service.config
        print(f"   Auto-optimize new orgs: {config['auto_optimize_new_orgs']}")
        print(f"   Content threshold: {config['auto_optimize_on_content_threshold']}")
        print(f"   Min interval: {config['min_optimization_interval']}")
        print(f"   Background processing: {config['background_processing']}")
        print(f"   Max concurrent: {config['max_concurrent_optimizations']}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error testing service configuration: {e}")
        return False

def main():
    """Run simulation"""
    print("🎬 RAG Integration Simulation")
    print("=" * 50)
    
    # Test service configuration
    if not test_service_configuration():
        print("❌ Service configuration test failed")
        return 1
    
    # Simulate org creation
    org_id = simulate_org_creation()
    if not org_id:
        print("❌ Organization creation simulation failed")
        return 1
    
    # Simulate crawl completion
    crawl_result = simulate_crawl_completion(org_id)
    if not crawl_result:
        print("❌ Crawl completion simulation failed")
        return 1
    
    # Check optimization status
    ready = check_optimization_status(org_id)
    
    print(f"\n{'=' * 50}")
    print("🎯 Simulation Results:")
    print(f"   ✅ Organization created: {org_id}")
    print(f"   ✅ Crawl completion simulated")
    print(f"   ✅ RAG automation triggered: {crawl_result.get('status', 'unknown')}")
    print(f"   📊 Ready for RAG queries: {ready}")
    
    if crawl_result.get('status') in ['processing', 'completed']:
        print("\n🎉 Automated RAG integration is working correctly!")
        print("The system automatically triggered optimization after the crawl completed.")
    elif crawl_result.get('status') == 'not_needed':
        print("\n✅ System is working but didn't need optimization.")
        print(f"Reason: {crawl_result.get('reason', 'unknown')}")
    else:
        print("\n⚠️  System responded but may need investigation.")
        print(f"Status: {crawl_result.get('status', 'unknown')}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
