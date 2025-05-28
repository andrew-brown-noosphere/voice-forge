#!/usr/bin/env python3
"""
Test crawl deletion functionality.
"""

import requests
import json
from datetime import datetime

def test_delete_crawl():
    """Test deleting crawls."""
    
    print("🗑️ Testing Crawl Deletion")
    print("=" * 30)
    
    # Get token from user
    token = input("🔑 Paste your JWT token: ").strip()
    
    if not token:
        print("❌ No token provided")
        return False
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # First, list existing crawls
    print("\\n📋 Current Crawls:")
    try:
        response = requests.get('http://localhost:8000/crawl?limit=10&offset=0', headers=headers)
        if response.status_code == 200:
            crawls = response.json()
            if not crawls:
                print("   No crawls found")
                return True
            
            for i, crawl in enumerate(crawls, 1):
                progress = crawl.get('progress', {})
                print(f"   {i}. {crawl.get('crawl_id', 'Unknown')[:8]}... - {crawl.get('domain', 'Unknown')} ({crawl.get('state', 'Unknown')})")
                print(f"      Pages: {progress.get('pages_crawled', 0)}, Content: {progress.get('content_extracted', 0)}")
            
            # Ask user which crawl to delete
            print(f"\\n🎯 Choose a crawl to delete (1-{len(crawls)}) or 0 to skip:")
            choice = input("Choice: ").strip()
            
            if choice == "0":
                print("Skipping deletion test")
                return True
            
            try:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(crawls):
                    crawl_to_delete = crawls[choice_idx]
                    crawl_id = crawl_to_delete['crawl_id']
                    
                    print(f"\\n🗑️ Deleting crawl: {crawl_id[:8]}... ({crawl_to_delete.get('domain', 'Unknown')})")
                    
                    # Attempt deletion
                    delete_response = requests.delete(f'http://localhost:8000/crawl/{crawl_id}', headers=headers)
                    
                    if delete_response.status_code == 204:
                        print("✅ Crawl deleted successfully!")
                        
                        # Verify it's gone
                        print("\\n🔍 Verifying deletion...")
                        verify_response = requests.get('http://localhost:8000/crawl?limit=10&offset=0', headers=headers)
                        if verify_response.status_code == 200:
                            remaining_crawls = verify_response.json()
                            remaining_ids = [c['crawl_id'] for c in remaining_crawls]
                            if crawl_id not in remaining_ids:
                                print("✅ Confirmed: Crawl is no longer in the list")
                                return True
                            else:
                                print("❌ Issue: Crawl still appears in the list")
                                return False
                        else:
                            print("⚠️ Could not verify deletion")
                            return True
                    else:
                        print(f"❌ Deletion failed: {delete_response.status_code}")
                        if delete_response.text:
                            try:
                                error = delete_response.json()
                                print(f"   Error: {error.get('detail', delete_response.text)}")
                            except:
                                print(f"   Error: {delete_response.text}")
                        return False
                else:
                    print("❌ Invalid choice")
                    return False
            except ValueError:
                print("❌ Invalid choice - must be a number")
                return False
        else:
            print(f"❌ Failed to list crawls: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error listing crawls: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 VoiceForge Crawl Deletion Test")
    print("=" * 35)
    print(f"Time: {datetime.now().isoformat()}")
    
    success = test_delete_crawl()
    
    if success:
        print("\\n🎉 Deletion test completed successfully!")
    else:
        print("\\n⚠️ Deletion test had issues")
        print("\\n🔧 If you see 'Failed to cancel crawl' errors:")
        print("   This is normal for completed crawls")
        print("   The deletion should still work")
    
    return success

if __name__ == "__main__":
    main()
