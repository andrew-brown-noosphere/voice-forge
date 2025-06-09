#!/usr/bin/env python3
"""
Quick sitemap check for buf.build
"""

import requests
import re

def check_sitemap():
    print("🗺️ CHECKING BUF.BUILD SITEMAP")
    print("=" * 40)
    
    urls_to_check = [
        "https://buf.build/sitemap.xml",
        "https://buf.build/robots.txt", 
        "https://docs.buf.build/sitemap.xml"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    total_urls_found = 0
    
    for url in urls_to_check:
        print(f"\n📋 {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                content = response.text
                print(f"   ✅ Found! ({len(content)} chars)")
                
                if 'sitemap.xml' in url:
                    # Extract URLs from sitemap
                    urls = re.findall(r'<loc>(.*?)</loc>', content)
                    if urls:
                        print(f"   🎯 {len(urls)} URLs found:")
                        total_urls_found += len(urls)
                        
                        # Show first 10 URLs
                        for i, found_url in enumerate(urls[:10]):
                            print(f"      {i+1}. {found_url}")
                        
                        if len(urls) > 10:
                            print(f"      ... and {len(urls) - 10} more")
                    else:
                        print("   ⚠️ No URLs found in sitemap")
                
                elif 'robots.txt' in url:
                    lines = content.split('\n')
                    sitemap_refs = [line for line in lines if 'sitemap:' in line.lower()]
                    if sitemap_refs:
                        print("   🗺️ Sitemap references:")
                        for ref in sitemap_refs:
                            print(f"      {ref.strip()}")
                    
                    print("   📝 robots.txt content:")
                    for line in content.split('\n')[:10]:
                        if line.strip():
                            print(f"      {line.strip()}")
                
            else:
                print(f"   ❌ Status: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n🎯 TOTAL URLS DISCOVERED: {total_urls_found}")
    
    if total_urls_found > 0:
        print("\n💡 DEMO STRATEGY:")
        print(f"   • Use sitemap URLs for crawling")
        print(f"   • Expected: {min(total_urls_found, 50)} pages")
        print("   • Much better demo results!")
    else:
        print("\n💡 NO SITEMAP FOUND - ALTERNATIVE:")
        print("   • Try docs.buf.build subdomain")
        print("   • Use enhanced discovery")
        print("   • Multi-entry point strategy")

if __name__ == "__main__":
    check_sitemap()
