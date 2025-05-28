#!/usr/bin/env python3
"""
Quick fix: Override the VoiceForge Crawler User-Agent for testing
"""

import json

def get_stealth_crawl_config():
    """Get a crawler config that won't get blocked"""
    
    # Realistic browser User-Agent (Chrome on macOS)
    stealth_user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    return {
        "domain": "https://httpbin.org",  # Crawler-friendly test site
        "config": {
            "max_pages": 3,
            "max_depth": 1,
            "delay": 3,  # 3 seconds between requests
            "timeout": 15,
            "follow_external_links": False,
            "user_agent": stealth_user_agent,  # 🎯 THIS IS THE KEY FIX
            "exclude_patterns": [],
            "include_patterns": []
        }
    }

def get_production_user_agents():
    """Get a rotation of realistic User-Agents for production"""
    return [
        # Chrome on different platforms
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        
        # Safari
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        
        # Firefox  
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0",
        
        # Edge
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
    ]

def test_user_agent_comparison():
    """Compare the blocking potential of different User-Agents"""
    
    print("🕵️ USER-AGENT BLOCKING ANALYSIS")
    print("=" * 50)
    
    test_agents = [
        {
            "name": "Your Current (VoiceForge)",
            "agent": "VoiceForge Crawler (+https://voiceforge.example.com)",
            "blocking_risk": "🔴 EXTREMELY HIGH",
            "why": "Contains 'Crawler', custom bot name, obvious automation"
        },
        {
            "name": "Python Requests Default", 
            "agent": "python-requests/2.31.0",
            "blocking_risk": "🔴 EXTREMELY HIGH",
            "why": "Obviously Python script, immediate bot detection"
        },
        {
            "name": "Generic Bot",
            "agent": "Mozilla/5.0 (compatible; MyBot/1.0)",
            "blocking_risk": "🟠 HIGH",
            "why": "Contains 'Bot', minimal browser info"
        },
        {
            "name": "Realistic Chrome",
            "agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "blocking_risk": "🟢 LOW",
            "why": "Looks like real Chrome browser, detailed platform info"
        },
        {
            "name": "Realistic Safari",
            "agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
            "blocking_risk": "🟢 LOW", 
            "why": "Looks like real Safari browser, Apple platform"
        }
    ]
    
    for agent_info in test_agents:
        print(f"\n📱 {agent_info['name']}")
        print(f"   Agent: {agent_info['agent']}")
        print(f"   Risk: {agent_info['blocking_risk']}")
        print(f"   Why: {agent_info['why']}")
    
    print(f"\n{'=' * 50}")
    print("🎯 RECOMMENDATION")
    print("=" * 50)
    print("❌ NEVER use User-Agents with:")
    print("   • Words like 'bot', 'crawler', 'spider', 'scraper'")
    print("   • Company names or custom identifiers")
    print("   • Programming language names (python, node, etc.)")
    print("   • Version numbers that don't match real browsers")
    
    print("\n✅ ALWAYS use User-Agents that:")
    print("   • Match real, current browsers exactly")
    print("   • Include detailed platform information")
    print("   • Rotate between different realistic options")
    print("   • Are indistinguishable from human traffic")

def generate_test_curl_commands():
    """Generate curl commands to test different User-Agents"""
    
    print(f"\n{'=' * 50}")
    print("🧪 TEST DIFFERENT USER-AGENTS WITH CURL")
    print("=" * 50)
    
    test_url = "https://httpbin.org/headers"
    
    agents = [
        ("Your Current VoiceForge", "VoiceForge Crawler (+https://voiceforge.example.com)"),
        ("Realistic Chrome", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    ]
    
    for name, agent in agents:
        print(f"\n🔍 Test {name}:")
        print(f'curl -H "User-Agent: {agent}" {test_url}')
    
    print(f"\n📊 Compare the responses to see which one looks more natural!")

def main():
    """Show User-Agent analysis and solutions"""
    
    print("🚨 VOICEFORGE CRAWLER USER-AGENT ANALYSIS")
    print("=" * 60)
    
    current_ua = "VoiceForge Crawler (+https://voiceforge.example.com)"
    
    print(f"Your current User-Agent:")
    print(f"   {current_ua}")
    print(f"\n🔥 This is getting you blocked! Here's why:")
    print(f"   🤖 Contains word 'Crawler' = instant bot detection")
    print(f"   🏷️ Custom company name = not a real browser")
    print(f"   🌐 No browser version info = obvious automation")
    print(f"   📝 Website URL = commercial scraping indicator")
    
    test_user_agent_comparison()
    
    print(f"\n{'=' * 60}")
    print("⚡ IMMEDIATE FIX")
    print("=" * 60)
    
    config = get_stealth_crawl_config()
    print("Use this config for testing:")
    print(json.dumps(config, indent=2))
    
    print(f"\n🎯 Key change:")
    print(f"   FROM: {current_ua}")
    print(f"   TO:   {config['config']['user_agent']}")
    
    generate_test_curl_commands()
    
    print(f"\n🎉 RESULT:")
    print("With a realistic User-Agent, your crawler will:")
    print("   ✅ Get past basic bot detection")
    print("   ✅ Load pages instead of timing out") 
    print("   ✅ Trigger your RAG automation successfully")
    print("   ✅ Work with a much wider range of websites")
    
    print(f"\n🚀 Next step: Test your RAG automation with this config!")
    
    return 0

if __name__ == "__main__":
    exit(main())
