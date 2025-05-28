"""
Example Integration: How to Add Automated RAG to Your Existing VoiceForge Code

This file shows exactly where and how to add the automation hooks 
to your existing codebase with minimal changes.
"""

# ==========================================
# EXAMPLE 1: Organization Creation
# ==========================================

# 🔄 BEFORE: Your existing org creation code
def create_organization_old(org_data):
    """Your existing organization creation function."""
    from database.models import Organization
    from database.session import get_db_session
    
    session = next(get_db_session())
    
    org = Organization(
        name=org_data['name'],
        domain=org_data['domain'],
        # ... other org fields
    )
    
    session.add(org)
    session.commit()
    
    return org

# ✅ AFTER: Enhanced with automated RAG integration
def create_organization_new(org_data):
    """Enhanced organization creation with automated RAG setup."""
    from database.models import Organization
    from database.session import get_db_session
    from automated_rag_integration import RAGIntegrationHooks  # 🆕 ADD THIS
    
    session = next(get_db_session())
    
    org = Organization(
        name=org_data['name'],
        domain=org_data['domain'],
        # ... other org fields
    )
    
    session.add(org)
    session.commit()
    
    # 🆕 ADD THIS: Set up automated RAG for new org
    try:
        rag_result = RAGIntegrationHooks.on_organization_created(org.id, org_data)
        print(f"RAG setup for org {org.id}: {rag_result['status']}")
    except Exception as e:
        print(f"Warning: RAG setup failed for org {org.id}: {e}")
        # Don't fail org creation if RAG setup fails
    
    return org

# ==========================================
# EXAMPLE 2: Crawl Completion
# ==========================================

# 🔄 BEFORE: Your existing crawl completion code
def update_crawl_status_old(status, org_id=None):
    """Your existing crawl status update function."""
    from database.db import Database
    from database.session import get_db_session
    
    session = next(get_db_session())
    db = Database(session)
    
    # Update crawl status
    db.update_crawl_status(status, org_id)
    
    # If crawl completed, maybe do some cleanup
    if status.state == "completed":
        print(f"Crawl {status.crawl_id} completed successfully")
    
    session.close()

# ✅ AFTER: Enhanced with automated RAG optimization
def update_crawl_status_new(status, org_id=None):
    """Enhanced crawl status update with automated RAG optimization."""
    from database.db import Database
    from database.session import get_db_session
    from automated_rag_integration import RAGIntegrationHooks  # 🆕 ADD THIS
    
    session = next(get_db_session())
    db = Database(session)
    
    # Update crawl status
    db.update_crawl_status(status, org_id)
    
    # If crawl completed, trigger RAG optimization check
    if status.state == "completed":
        print(f"Crawl {status.crawl_id} completed successfully")
        
        # 🆕 ADD THIS: Check if RAG optimization should be triggered
        try:
            crawl_results = {
                'pages_crawled': status.progress.pages_crawled,
                'content_extracted': status.progress.content_extracted,
                'pages_failed': status.progress.pages_failed
            }
            
            rag_result = RAGIntegrationHooks.on_crawl_completed(
                status.crawl_id, 
                org_id or status.domain,  # Use org_id or derive from domain
                crawl_results
            )
            
            print(f"RAG optimization check: {rag_result['status']}")
            
            if rag_result['status'] == 'processing':
                print(f"🚀 RAG optimization started for org {org_id}")
            elif rag_result['status'] == 'not_needed':
                print(f"⏭️ RAG optimization not needed: {rag_result['reason']}")
                
        except Exception as e:
            print(f"Warning: RAG optimization check failed: {e}")
            # Don't fail crawl completion if RAG check fails
    
    session.close()

# ==========================================
# EXAMPLE 3: RAG Query Enhancement
# ==========================================

# 🔄 BEFORE: Your existing RAG service method
class RAGServiceOld:
    def search_chunks(self, query, org_id, top_k=5, **kwargs):
        """Your existing chunk search method."""
        chunks = self.rag_system.retrieve_relevant_chunks(
            query=query,
            top_k=top_k,
            org_id=org_id,
            **kwargs
        )
        return chunks

# ✅ AFTER: Enhanced with lazy optimization
class RAGServiceNew:
    def search_chunks(self, query, org_id, top_k=5, **kwargs):
        """Enhanced chunk search with lazy RAG optimization."""
        from automated_rag_integration import RAGIntegrationHooks  # 🆕 ADD THIS
        
        # 🆕 ADD THIS: Ensure org is optimized before querying
        try:
            optimization_result = RAGIntegrationHooks.on_rag_query_requested(org_id, query)
            
            if optimization_result['status'] == 'processing':
                # RAG optimization was triggered - inform user
                print(f"🔄 Optimizing RAG system for org {org_id}...")
                # You might want to return a "please wait" message or queue the query
                
        except Exception as e:
            print(f"Warning: RAG optimization check failed: {e}")
            # Continue with query even if optimization check fails
        
        # Your existing search logic
        chunks = self.rag_system.retrieve_relevant_chunks(
            query=query,
            top_k=top_k,
            org_id=org_id,
            **kwargs
        )
        return chunks

# ==========================================
# EXAMPLE 4: FastAPI Application Setup
# ==========================================

# 🔄 BEFORE: Your existing FastAPI app
from fastapi import FastAPI

app_old = FastAPI(title="VoiceForge API")

# Your existing routers
# app.include_router(auth_router)
# app.include_router(crawl_router)
# app.include_router(content_router)

# ✅ AFTER: Enhanced with RAG endpoints
from fastapi import FastAPI
from api.rag_endpoints import rag_router  # 🆕 ADD THIS

app_new = FastAPI(title="VoiceForge API")

# Your existing routers
# app.include_router(auth_router)
# app.include_router(crawl_router)
# app.include_router(content_router)

# 🆕 ADD THIS: RAG optimization endpoints
app_new.include_router(rag_router)

# ==========================================
# EXAMPLE 5: Content Addition Hook
# ==========================================

# 🔄 BEFORE: Your existing content saving code
def save_content_old(content_data, org_id):
    """Your existing content saving function."""
    from database.db import Database
    from database.session import get_db_session
    
    session = next(get_db_session())
    db = Database(session)
    
    # Save content
    db.save_content(content_data, org_id)
    
    session.close()
    
    return {"status": "saved", "content_id": content_data["content_id"]}

# ✅ AFTER: Enhanced with content tracking
def save_content_new(content_data, org_id):
    """Enhanced content saving with RAG optimization tracking."""
    from database.db import Database
    from database.session import get_db_session
    from automated_rag_integration import RAGIntegrationHooks  # 🆕 ADD THIS
    
    session = next(get_db_session())
    db = Database(session)
    
    # Save content
    db.save_content(content_data, org_id)
    
    # 🆕 ADD THIS: Track content addition for RAG optimization
    try:
        # Get current content count for this org
        from database.models import Content
        content_count = session.query(Content).filter(Content.org_id == org_id).count()
        
        # Notify RAG system of new content
        rag_result = RAGIntegrationHooks.on_content_added(org_id, 1)  # 1 new item
        
        if rag_result['status'] == 'processing':
            print(f"🚀 RAG optimization triggered for org {org_id} (total content: {content_count})")
        elif rag_result['status'] == 'waiting':
            print(f"⏳ RAG optimization pending for org {org_id} ({rag_result['reason']})")
            
    except Exception as e:
        print(f"Warning: RAG content tracking failed: {e}")
        # Don't fail content saving if RAG tracking fails
    
    session.close()
    
    return {"status": "saved", "content_id": content_data["content_id"]}

# ==========================================
# EXAMPLE 6: Simple Testing Function
# ==========================================

def test_automated_rag_integration():
    """Test function to verify the automated RAG integration is working."""
    from automated_rag_integration import (
        auto_optimize_org, 
        check_org_optimization_status,
        is_org_ready_for_rag
    )
    
    test_org_id = "test-org-123"
    
    print("🧪 Testing Automated RAG Integration")
    print("=" * 50)
    
    # Test 1: Check readiness
    print(f"\n1️⃣ Checking RAG readiness for org {test_org_id}")
    ready, reason = is_org_ready_for_rag(test_org_id)
    print(f"   Ready: {ready}")
    print(f"   Reason: {reason}")
    
    # Test 2: Check status
    print(f"\n2️⃣ Checking optimization status for org {test_org_id}")
    status = check_org_optimization_status(test_org_id)
    if status:
        print(f"   Status: {status.get('status', 'unknown')}")
        print(f"   Last update: {status.get('completed_at', 'never')}")
    else:
        print("   No optimization history")
    
    # Test 3: Manual optimization (if needed)
    if not ready:
        print(f"\n3️⃣ Triggering manual optimization for org {test_org_id}")
        try:
            result = auto_optimize_org(test_org_id, force=True)
            print(f"   Result: {result['status']}")
            if result['status'] == 'processing':
                print(f"   Task ID: {result.get('task_id', 'N/A')}")
        except Exception as e:
            print(f"   Error: {e}")
    else:
        print(f"\n3️⃣ Org {test_org_id} is already ready - no optimization needed")
    
    print(f"\n✅ Testing complete!")

# ==========================================
# EXAMPLE 7: Environment Configuration
# ==========================================

def configure_automated_rag():
    """Configure the automated RAG system based on your needs."""
    from automated_rag_integration import automated_rag_service
    import os
    
    # Configure based on environment
    environment = os.getenv('ENVIRONMENT', 'development')
    
    if environment == 'production':
        # Production settings - more conservative
        automated_rag_service.config.update({
            'auto_optimize_new_orgs': True,
            'auto_optimize_on_content_threshold': 25,  # Higher threshold
            'min_optimization_interval': timedelta(hours=12),  # Less frequent
            'max_concurrent_optimizations': 2,  # Conservative limit
        })
        print("🏭 Configured for production environment")
        
    elif environment == 'staging':
        # Staging settings - moderate
        automated_rag_service.config.update({
            'auto_optimize_new_orgs': True,
            'auto_optimize_on_content_threshold': 15,
            'min_optimization_interval': timedelta(hours=6),
            'max_concurrent_optimizations': 3,
        })
        print("🧪 Configured for staging environment")
        
    else:
        # Development settings - aggressive for testing
        automated_rag_service.config.update({
            'auto_optimize_new_orgs': True,
            'auto_optimize_on_content_threshold': 5,  # Low threshold for testing
            'min_optimization_interval': timedelta(minutes=30),  # Frequent for testing
            'max_concurrent_optimizations': 5,
        })
        print("🔧 Configured for development environment")
    
    print(f"Current config: {automated_rag_service.config}")

# ==========================================
# USAGE INSTRUCTIONS
# ==========================================

"""
To integrate this into your existing VoiceForge codebase:

1. Copy the automated_rag_integration.py file to your backend directory

2. Replace your existing functions with the enhanced versions above:
   - create_organization_old → create_organization_new
   - update_crawl_status_old → update_crawl_status_new
   - RAGServiceOld → RAGServiceNew
   - app_old → app_new
   - save_content_old → save_content_new

3. Add the import statements where shown (marked with # 🆕 ADD THIS)

4. Test the integration:
   ```python
   test_automated_rag_integration()
   configure_automated_rag()
   ```

5. Your system will now automatically:
   ✅ Optimize new organizations when they get content
   ✅ Re-optimize when crawls complete with significant content
   ✅ Ensure RAG is ready before processing queries
   ✅ Provide API endpoints for manual control
   ✅ Track optimization status and health

No more manual RAG optimization needed! 🎉
"""

if __name__ == "__main__":
    # Run tests if this file is executed directly
    configure_automated_rag()
    test_automated_rag_integration()
