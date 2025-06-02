#!/usr/bin/env python3
"""
Demo script showing configurable user agent for VoiceForge crawler.
This demonstrates how users can configure whitelisted user agents for their own domains.
"""
import sys
import os
sys.path.append('/Users/andrewbrown/Sites/noosphere/github/voice-forge/backend')

from api.models import CrawlConfig

def demo_user_agent_configurations():
    """Demonstrate different user agent configurations."""
    
    print("🚀 VOICEFORGE CRAWLER - USER AGENT CONFIGURATION DEMO")
    print("=" * 60)
    
    # Demo 1: Default VoiceForge crawler
    print("\n1️⃣ DEFAULT VOICEFORGE CRAWLER")
    print("-" * 30)
    config1 = CrawlConfig(
        user_agent_mode="default",
        max_pages=5,
        delay=2.0
    )
    
    from crawler.engine import UserAgentGenerator
    ua1 = UserAgentGenerator.generate_user_agent(config1)
    print(f"User Agent: {ua1}")
    print("Use case: Standard VoiceForge crawler identification")
    print("Server config: Whitelist 'VoiceForge-Crawler' in your server rules")
    
    # Demo 2: Organization-branded crawler
    print("\n2️⃣ ORGANIZATION-BRANDED CRAWLER")
    print("-" * 30)
    config2 = CrawlConfig(
        user_agent_mode="default",
        organization_name="Example Corp",
        contact_email="admin@example.com",
        max_pages=5,
        delay=2.0
    )
    
    ua2 = UserAgentGenerator.generate_user_agent(config2)
    print(f"User Agent: {ua2}")
    print("Use case: Corporate branded crawler with contact info")
    print("Server config: Whitelist 'VoiceForge-Crawler' and 'Example Corp'")
    
    # Demo 3: Custom whitelisted crawler
    print("\n3️⃣ CUSTOM WHITELISTED CRAWLER")
    print("-" * 30)
    config3 = CrawlConfig(
        user_agent_mode="custom",
        custom_user_agent="ExampleCorp-ContentBot/1.0 (+https://example.com/bot-info)",
        max_pages=5,
        delay=2.0
    )
    
    ua3 = UserAgentGenerator.generate_user_agent(config3)
    print(f"User Agent: {ua3}")
    print("Use case: Fully custom user agent for specific whitelisting")
    print("Server config: Whitelist exact string 'ExampleCorp-ContentBot'")
    
    # Demo 4: Stealth mode (for demos only)
    print("\n4️⃣ STEALTH MODE (DEMO ONLY)")
    print("-" * 30)
    config4 = CrawlConfig(
        user_agent_mode="stealth",
        max_pages=3,
        delay=3.0
    )
    
    ua4 = UserAgentGenerator.generate_user_agent(config4)
    print(f"User Agent: {ua4}")
    print("Use case: Demo/testing mode to appear as regular browser")
    print("⚠️  Note: Only for demo purposes on buf.build, not for production")
    
    print(f"\n" + "=" * 60)
    print("📋 INTEGRATION GUIDE:")
    print("-" * 20)
    print("1. Choose appropriate user agent mode based on your use case")
    print("2. Configure your web server to whitelist the user agent")
    print("3. Test crawling with the configured user agent")
    print("4. Monitor server logs to ensure crawler is recognized")
    
    print(f"\n🛡️ SERVER CONFIGURATION EXAMPLES:")
    print("-" * 35)
    print("Apache (.htaccess):")
    print('  SetEnvIf User-Agent "VoiceForge-Crawler" allowed_bot')
    print('  <RequireAll>')
    print('    Require env allowed_bot')
    print('  </RequireAll>')
    
    print(f"\nNginx:")
    print('  if ($http_user_agent ~* "VoiceForge-Crawler") {')
    print('    # Allow access')
    print('  }')
    
    print(f"\nCloudflare Page Rules:")
    print('  1. Create rule for your domain')
    print('  2. Add condition: User-Agent contains "VoiceForge-Crawler"')
    print('  3. Set Security Level to "Essentially Off" for crawler')
    
    return [config1, config2, config3, config4]

def test_buf_build_demo():
    """Test buf.build crawling with stealth mode for demo purposes."""
    
    print(f"\n🧪 BUF.BUILD DEMO TEST")
    print("=" * 30)
    print("Testing buf.build with stealth mode (demo purposes only)")
    
    # Stealth configuration for buf.build demo
    demo_config = CrawlConfig(
        user_agent_mode="stealth",
        max_pages=3,
        max_depth=1,
        delay=3.0,
        timeout=45,
        respect_robots_txt=False
    )
    
    ua = UserAgentGenerator.generate_user_agent(demo_config)
    print(f"Demo User Agent: {ua}")
    print(f"Max Pages: {demo_config.max_pages}")
    print(f"Delay: {demo_config.delay}s")
    print(f"Mode: {demo_config.user_agent_mode}")
    
    print(f"\n⚠️  IMPORTANT NOTES:")
    print("- This is stealth mode for demonstration purposes only")
    print("- For production, users should whitelist VoiceForge on their own domains")
    print("- buf.build crawling is just to show the crawler works")
    print("- Real use case: Users crawl their own websites with whitelisted agents")
    
    return demo_config

if __name__ == "__main__":
    # Show different user agent configurations
    configs = demo_user_agent_configurations()
    
    # Demo buf.build testing (stealth mode)
    buf_config = test_buf_build_demo()
    
    print(f"\n🎯 NEXT STEPS:")
    print("1. Choose appropriate configuration for your use case")
    print("2. Update VoiceForge backend with new crawler code")
    print("3. Test crawling with different user agent modes")
    print("4. Configure your servers to whitelist VoiceForge crawler")
