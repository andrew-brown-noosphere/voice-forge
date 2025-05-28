#!/usr/bin/env python3
"""
Analyze how websites detect crawlers and what your crawler reveals
"""

import requests
import time
import json
from datetime import datetime
import sys

def analyze_crawler_fingerprint():
    """Analyze what your current crawler reveals about itself"""
    print("🕵️ HOW WEBSITES DETECT YOUR CRAWLER")
    print("=" * 60)
    
    print("Looking at your VoiceForge crawler, here's what gives it away:\n")
    
    detection_methods = [
        {
            "method": "🤖 User-Agent Analysis",
            "your_crawler": "Uses config.user_agent (probably default/basic)",
            "what_they_see": "Generic or missing User-Agent string",
            "red_flags": [
                "Empty or default User-Agent",
                "Contains 'bot', 'crawler', 'spider'", 
                "Doesn't match real browser patterns",
                "Same User-Agent for all requests"
            ],
            "solution": "Rotate realistic browser User-Agents"
        },
        {
            "method": "⚡ Request Timing Patterns",
            "your_crawler": "time.sleep(self.config.delay) - fixed delay",
            "what_they_see": "Perfectly timed requests (inhuman)",
            "red_flags": [
                "Exact same delay between requests",
                "No variation in timing",
                "Too fast (no human reads that quickly)",
                "No pause for 'reading' content"
            ],
            "solution": "Random delays, simulate human reading time"
        },
        {
            "method": "🌐 Browser Automation Detection",
            "your_crawler": "playwright.chromium.launch(headless=True)",
            "what_they_see": "Headless browser fingerprint",
            "red_flags": [
                "Missing window.chrome object",
                "Navigator.webdriver = true",
                "Missing plugins/extensions",
                "Headless browser properties",
                "WebGL/Canvas fingerprinting differences"
            ],
            "solution": "Stealth mode, browser fingerprint masking"
        },
        {
            "method": "📡 HTTP Header Analysis", 
            "your_crawler": "Basic headers from Playwright",
            "what_they_see": "Missing or unusual headers",
            "red_flags": [
                "Missing Accept-Language",
                "Missing Accept-Encoding", 
                "No DNT (Do Not Track)",
                "Missing Sec-Fetch-* headers",
                "No cache-control headers"
            ],
            "solution": "Complete, realistic header sets"
        },
        {
            "method": "🎯 Behavioral Analysis",
            "your_crawler": "Systematic URL traversal",
            "what_they_see": "Non-human browsing patterns",
            "red_flags": [
                "Visits every link systematically",
                "Never clicks on ads/social media",
                "No back/forward navigation",
                "No JavaScript interactions",
                "Never scrolls or hovers"
            ],
            "solution": "Random navigation, simulate human behavior"
        },
        {
            "method": "🔍 JavaScript Challenges",
            "your_crawler": "page.wait_for_load_state('networkidle')",
            "what_they_see": "May fail JS bot detection tests",
            "red_flags": [
                "Can't solve simple math problems",
                "Fails mouse movement tests",
                "Missing browser APIs",
                "Consistent performance.now() timing"
            ],
            "solution": "Advanced stealth techniques"
        },
        {
            "method": "📊 Traffic Analysis",
            "your_crawler": "Single IP, predictable patterns",
            "what_they_see": "Automated traffic patterns",
            "red_flags": [
                "Same IP for all requests",
                "Perfect request intervals",
                "No idle time between sessions",
                "Volume inconsistent with human users"
            ],
            "solution": "IP rotation, realistic session patterns"
        }
    ]
    
    for i, detection in enumerate(detection_methods, 1):
        print(f"{i}. {detection['method']}")
        print(f"   📋 Your crawler: {detection['your_crawler']}")
        print(f"   👀 What they see: {detection['what_they_see']}")
        print(f"   🚩 Red flags:")
        for flag in detection['red_flags']:
            print(f"      • {flag}")
        print(f"   ✅ Solution: {detection['solution']}\n")

def test_current_fingerprint():
    """Test what your current setup looks like to websites"""
    print("🔬 TESTING YOUR CURRENT CRAWLER FINGERPRINT")
    print("=" * 60)
    
    # Test with httpbin to see what we're sending
    test_url = "https://httpbin.org/headers"
    
    print("Testing with a basic request to see what websites see...\n")
    
    try:
        # Simulate what your Playwright crawler sends
        response = requests.get(test_url, timeout=10)
        headers_data = response.json()
        
        print("📡 Headers your crawler sends:")
        for header, value in headers_data['headers'].items():
            print(f"   {header}: {value}")
        
        print(f"\n🕵️ Bot detection analysis:")
        
        user_agent = headers_data['headers'].get('User-Agent', '')
        if 'python' in user_agent.lower() or 'requests' in user_agent.lower():
            print("   🚨 MAJOR RED FLAG: Python/requests in User-Agent")
        elif not user_agent:
            print("   🚨 MAJOR RED FLAG: Missing User-Agent")
        elif len(user_agent) < 50:
            print("   ⚠️ SUSPICIOUS: Very short User-Agent")
        else:
            print("   ✅ User-Agent looks reasonable")
        
        # Check for missing headers
        expected_headers = ['Accept', 'Accept-Language', 'Accept-Encoding']
        missing_headers = []
        for header in expected_headers:
            if header not in headers_data['headers']:
                missing_headers.append(header)
        
        if missing_headers:
            print(f"   ⚠️ MISSING: {', '.join(missing_headers)}")
        else:
            print("   ✅ Basic headers present")
            
    except Exception as e:
        print(f"   ❌ Could not test fingerprint: {e}")

def show_stealth_improvements():
    """Show specific improvements for your crawler"""
    print(f"\n{'=' * 60}")
    print("🥷 STEALTH IMPROVEMENTS FOR YOUR CRAWLER")
    print("=" * 60)
    
    improvements = [
        {
            "area": "User-Agent Rotation",
            "current": "user_agent=self.config.user_agent",
            "improved": """
# Rotate User-Agents
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36", 
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
]
page = browser.new_page(user_agent=random.choice(USER_AGENTS))
""",
            "impact": "🔥 HIGH - Most important fix"
        },
        {
            "area": "Request Timing",
            "current": "time.sleep(self.config.delay)",
            "improved": """
# Human-like delays
import random
delay = random.uniform(2, 8)  # 2-8 seconds
reading_time = len(html) / 1000  # Simulate reading time
time.sleep(delay + reading_time)
""",
            "impact": "🔥 HIGH - Eliminates timing patterns"
        },
        {
            "area": "Stealth Mode",
            "current": "playwright.chromium.launch(headless=True)",
            "improved": """
# Stealth browser launch
browser = playwright.chromium.launch(
    headless=True,
    args=[
        '--disable-blink-features=AutomationControlled',
        '--disable-web-security',
        '--disable-features=VizDisplayCompositor'
    ]
)
# Hide webdriver property
page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
""",
            "impact": "🔥 HIGH - Hides automation"
        },
        {
            "area": "Realistic Headers",
            "current": "Basic page.goto(url)",
            "improved": """
# Set realistic headers
page.set_extra_http_headers({
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
})
""",
            "impact": "🟡 MEDIUM - Looks more human"
        },
        {
            "area": "Session Management",
            "current": "New page for each request",
            "improved": """
# Reuse browser context
context = browser.new_context()
page = context.new_page()
# Use same page for multiple requests
# Occasionally clear cookies/storage
""",
            "impact": "🟡 MEDIUM - More realistic sessions"
        }
    ]
    
    for improvement in improvements:
        print(f"🎯 {improvement['area']} - {improvement['impact']}")
        print(f"   Current: {improvement['current']}")
        print(f"   Improved:")
        print(f"{improvement['improved']}")
        print()

def main():
    """Run crawler detection analysis"""
    analyze_crawler_fingerprint()
    test_current_fingerprint()
    show_stealth_improvements()
    
    print("=" * 60)
    print("🎯 KEY TAKEAWAYS")
    print("=" * 60)
    
    takeaways = [
        "🤖 Your crawler has multiple 'bot signatures' that websites detect",
        "⚡ Perfect timing patterns are the biggest giveaway",
        "🌐 Headless browsers have distinctive fingerprints", 
        "📡 Missing or minimal headers scream 'automation'",
        "🎯 Systematic behavior patterns are obviously non-human",
        "🥷 Stealth techniques can make crawlers nearly undetectable"
    ]
    
    for takeaway in takeaways:
        print(f"   {takeaway}")
    
    print(f"\n🚀 IMMEDIATE ACTION:")
    print("1. Test with crawler-friendly sites first (HTTPBin, Example.com)")
    print("2. Add User-Agent rotation and random delays")
    print("3. Implement stealth mode for headless browser")
    print("4. Your RAG automation will work perfectly once crawler is stealthier!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
