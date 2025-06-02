#!/usr/bin/env python3
"""
Quick test to diagnose buf.build crawling issues and anti-bot detection.
"""
import asyncio
import logging
from playwright.async_api import async_playwright
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_buf_build_access():
    """Test different approaches to accessing buf.build."""
    
    print("🧪 TESTING BUF.BUILD ACCESS")
    print("=" * 50)
    
    async with async_playwright() as p:
        # Test 1: Basic crawler approach (what VoiceForge currently does)
        print("\n1️⃣ TESTING BASIC CRAWLER APPROACH")
        print("-" * 30)
        
        try:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(
                user_agent="VoiceForge Intelligencer (+https://voiceforge.voyant.io)"
            )
            
            response = await page.goto("https://buf.build", timeout=30000)
            print(f"✅ Basic approach - Status: {response.status}")
            print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
            print(f"   Response size: {len(await page.content())} chars")
            
            await browser.close()
            
        except Exception as e:
            print(f"❌ Basic approach failed: {str(e)}")
        
        # Test 2: Stealth approach
        print("\n2️⃣ TESTING STEALTH APPROACH")
        print("-" * 30)
        
        try:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-first-run",
                    "--no-default-browser-check",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-features=TranslateUI"
                ]
            )
            
            context = await browser.new_context(
                viewport={'width': 1366, 'height': 768},
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            page = await context.new_page()
            
            # Set realistic headers
            await page.set_extra_http_headers({
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1"
            })
            
            # Hide automation
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                delete window.__playwright;
            """)
            
            response = await page.goto("https://buf.build", wait_until='networkidle', timeout=45000)
            print(f"✅ Stealth approach - Status: {response.status}")
            print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
            
            content = await page.content()
            print(f"   Response size: {len(content)} chars")
            
            # Check for anti-bot indicators
            if "cloudflare" in content.lower():
                print("⚠️  Cloudflare protection detected")
            if "captcha" in content.lower():
                print("⚠️  CAPTCHA detected")
            if "access denied" in content.lower():
                print("⚠️  Access denied message detected")
            if "bot" in content.lower():
                print("⚠️  Bot detection message detected")
            
            # Try to find navigation links
            nav_links = await page.evaluate("""
                Array.from(document.querySelectorAll('a[href*="buf.build"]')).slice(0, 5).map(a => a.href)
            """)
            print(f"   Found {len(nav_links)} internal links")
            for link in nav_links:
                print(f"     - {link}")
            
            await browser.close()
            
        except Exception as e:
            print(f"❌ Stealth approach failed: {str(e)}")
        
        # Test 3: Check robots.txt
        print("\n3️⃣ CHECKING ROBOTS.TXT")
        print("-" * 30)
        
        try:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            response = await page.goto("https://buf.build/robots.txt", timeout=15000)
            print(f"Status: {response.status}")
            
            if response.status == 200:
                robots_content = await page.content()
                # Extract text from HTML
                text_content = await page.evaluate("document.body.textContent")
                print("Robots.txt content:")
                print(text_content[:500] + "..." if len(text_content) > 500 else text_content)
            else:
                print("No robots.txt found or access denied")
            
            await browser.close()
            
        except Exception as e:
            print(f"❌ Robots.txt check failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_buf_build_access())
