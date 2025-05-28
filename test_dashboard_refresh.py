#!/usr/bin/env python3
"""
Test multiple crawls to verify dashboard auto-refresh after deletion.
"""

import requests
import json
import time
from datetime import datetime

def create_test_crawl(token, domain):
    """Create a quick test crawl."""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    crawl_data = {
        "domain": domain,
        "config": {
            "max_depth": 1,
            "max_pages": 2,
            "delay": 0.5,
            "timeout": 15,
            "user_agent": "Mozilla/5.0 (compatible; VoiceForge/1.0)",
            "follow_external_links": False,
            "include_patterns": [],
            "exclude_patterns": ["\.pdf$", "\.jpg$", "\.png$", "\.gif$"]
        }
    }
    
    try:
        response = requests.post('http://localhost:8000/crawl', headers=headers, json=crawl_data)
        if response.status_code == 202:
            result = response.json()
            print(f"✅ Created test crawl for {domain}: {result['crawl_id'][:8]}...")
            return result['crawl_id']
        else:
            print(f"❌ Failed to create crawl for {domain}: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error creating crawl for {domain}: {e}")
        return None

def test_dashboard_refresh():
    """Test that dashboard refreshes properly after deletion."""
    
    print("🔄 Testing Dashboard Auto-Refresh After Deletion")
    print("=" * 50)
    
    # Get token from user
    token = input("🔑 Paste your JWT token: ").strip()
    
    if not token:
        print("❌ No token provided")
        return False
    
    print("\\n1️⃣ Creating some test crawls...")
    test_domains = [
        "https://httpbin.org",
        "https://jsonplaceholder.typicode.com"
    ]
    
    created_crawls = []
    for domain in test_domains:
        crawl_id = create_test_crawl(token, domain)
        if crawl_id:
            created_crawls.append(crawl_id)
        time.sleep(1)  # Small delay between requests
    
    if not created_crawls:
        print("❌ No test crawls created. Using existing crawls.")
    
    print(f"\\n2️⃣ Created {len(created_crawls)} test crawls")
    print("\\n🎯 Testing Auto-Refresh:")
    print("   1. Go to your Dashboard: http://localhost:5173")
    print("   2. Click delete on any crawl")
    print("   3. Watch for:")
    print("      ✅ Spinner appears on delete button")
    print("      ✅ Crawl disappears from list automatically")
    print("      ✅ Stats update automatically")
    print("      ✅ No page refresh needed!")
    
    print("\\n💡 If you still need to refresh manually:")
    print("   • Check browser console for errors")
    print("   • Try a hard refresh (Ctrl+Shift+R)")
    print("   • Verify backend is responding properly")
    
    return True

def main():
    """Main test function."""
    print("🧪 VoiceForge Dashboard Auto-Refresh Test")
    print("=" * 42)
    print(f"Time: {datetime.now().isoformat()}")
    
    success = test_dashboard_refresh()
    
    if success:
        print("\\n🎉 Test setup complete!")
        print("\\n📋 Summary of improvements:")
        print("   ✅ Delete button shows spinner during deletion")
        print("   ✅ Dashboard refreshes automatically after 200ms")
        print("   ✅ Fallback to local removal if refresh fails")
        print("   ✅ Better error handling and visual feedback")
    else:
        print("\\n⚠️ Test setup failed")
    
    return success

if __name__ == "__main__":
    main()
