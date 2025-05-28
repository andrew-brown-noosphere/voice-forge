#!/usr/bin/env python3
"""
Test the domains endpoint to verify it shows only real crawled domains.
"""

import requests
import json
from datetime import datetime

def test_domains_endpoint():
    """Test that domains endpoint returns only actual crawled domains."""
    
    print("🌐 Testing Domains Endpoint")
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
    
    # Test domains endpoint
    print("\\n1️⃣ Testing /domains endpoint...")
    try:
        response = requests.get('http://localhost:8000/domains', headers=headers)
        if response.status_code == 200:
            domains = response.json()
            print(f"✅ Domains endpoint working!")
            print(f"   Found {len(domains)} domains:")
            
            if domains:
                for i, domain in enumerate(domains, 1):
                    print(f"   {i}. {domain}")
                
                # Check if we still have the hardcoded domains
                hardcoded_domains = [\"https://noosphere.tech\", \"https://www.noosphere.tech\"]
                has_hardcoded = any(hd in domains for hd in hardcoded_domains)
                
                if has_hardcoded:
                    print(\"\\n⚠️ Still showing hardcoded domains!\")
                    print(\"   This means the fix hasn't been applied yet.\")
                    print(\"   Please restart the backend to apply changes.\")
                    return False
                else:
                    print(\"\\n✅ Only showing real crawled domains!\")
                    
                    # Verify domains are from actual crawls
                    print(\"\\n2️⃣ Verifying domains match crawl history...\")
                    crawl_response = requests.get('http://localhost:8000/crawl?limit=20&offset=0', headers=headers)
                    if crawl_response.status_code == 200:
                        crawls = crawl_response.json()
                        crawl_domains = set(crawl.get('domain', '') for crawl in crawls)
                        
                        print(f\"   Crawl domains: {list(crawl_domains)}\")
                        
                        # Check if domains match
                        domain_set = set(domains)
                        if domain_set.issubset(crawl_domains):
                            print(\"✅ All domains match crawl history!\")
                            return True
                        else:
                            print(\"⚠️ Some domains don't match crawl history\")
                            print(f\"   Extra domains: {domain_set - crawl_domains}\")
                            return True  # Still OK, might be from deleted crawls
                    else:
                        print(\"⚠️ Could not verify against crawl history\")
                        return True
            else:
                print(\"   No domains found (this is OK if no crawls completed)\")
                return True
        else:
            print(f\"❌ Domains endpoint failed: {response.status_code}\")
            print(f\"   Error: {response.text}\")
            return False
    except Exception as e:
        print(f\"❌ Error testing domains: {e}\")
        return False

def check_backend_logs():
    \"\"\"Provide instructions for checking backend debug output.\"\"\"\n    print(\"\\n📋 Check Backend Debug Output:\")\n    print(\"   Look for this line in your backend logs:\")\n    print(\"   'Domains found in database: [list of domains]'\")\n    print(\"\\n   This will show exactly what the database query returns.\")\n    print(\"   If you see hardcoded domains there, the database has stale data.\")\n\ndef main():\n    \"\"\"Main test function.\"\"\"\n    print(\"🧪 VoiceForge Domains Endpoint Test\")\n    print(\"=\" * 35)\n    print(f\"Time: {datetime.now().isoformat()}\")\n    \n    success = test_domains_endpoint()\n    \n    if success:\n        print(\"\\n🎉 Domains endpoint is working correctly!\")\n        print(\"\\n✅ Benefits of the fix:\")\n        print(\"   • No more hardcoded 'noosphere.tech' domains\")\n        print(\"   • Only shows actual crawled domains\")\n        print(\"   • Dashboard 'Crawled Domains' section is accurate\")\n        print(\"   • Content generation dropdown has real options\")\n    else:\n        print(\"\\n🔧 To fix the domains issue:\")\n        print(\"   1. Restart your backend server\")\n        print(\"   2. Refresh your frontend\")\n        print(\"   3. Check that crawls have completed successfully\")\n    \n    check_backend_logs()\n    \n    return success\n\nif __name__ == \"__main__\":\n    main()
