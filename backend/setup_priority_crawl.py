#!/usr/bin/env python3
"""
Enhanced Firecrawl configuration for product/blog prioritized crawling.
"""

import os
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_priority_crawl_urls():
    """Get prioritized URLs for buf.build demo focusing on product and blog content."""
    
    # High-priority URLs for buf.build demo
    priority_urls = {
        "product_pages": [
            "https://buf.build/product",
            "https://buf.build/features", 
            "https://buf.build/platform",
            "https://buf.build/solutions",
            "https://buf.build/pricing",
            "https://buf.build/use-cases"
        ],
        "blog_content": [
            "https://buf.build/blog",
            "https://blog.buf.build",
            "https://buf.build/news",
            "https://buf.build/announcements"
        ],
        "fallback_urls": [
            "https://buf.build/docs",
            "https://docs.buf.build",
            "https://buf.build"
        ]
    }
    
    return priority_urls

def create_enhanced_firecrawl_config():
    """Create optimized Firecrawl configuration for product/blog content."""
    
    configs = {
        "product_focused": {
            "name": "Product-Focused Demo",
            "description": "Prioritize product pages and features for business demo",
            "start_urls": [
                "https://buf.build/product",
                "https://buf.build/features",
                "https://buf.build/platform"
            ],
            "settings": {
                "max_pages": 30,
                "max_depth": 3,
                "delay": 2000,
                "include_patterns": [
                    ".*product.*",
                    ".*feature.*", 
                    ".*solution.*",
                    ".*platform.*",
                    ".*pricing.*",
                    ".*use-case.*"
                ],
                "exclude_patterns": [
                    ".*\\.pdf$",
                    ".*\\.(jpg|png|gif)$",
                    ".*\\.css$",
                    ".*\\.js$",
                    ".*legal.*",
                    ".*privacy.*",
                    ".*contact.*"
                ]
            }
        },
        
        "blog_focused": {
            "name": "Blog/Content-Focused Demo", 
            "description": "Prioritize blog and thought leadership content",
            "start_urls": [
                "https://buf.build/blog",
                "https://blog.buf.build",
                "https://buf.build/news"
            ],
            "settings": {
                "max_pages": 25,
                "max_depth": 2,
                "delay": 2500,
                "include_patterns": [
                    ".*blog.*",
                    ".*news.*",
                    ".*article.*",
                    ".*post.*",
                    ".*announcement.*"
                ],
                "exclude_patterns": [
                    ".*\\.pdf$",
                    ".*\\.(jpg|png|gif)$", 
                    ".*\\.css$",
                    ".*\\.js$"
                ]
            }
        },
        
        "combined_demo": {
            "name": "Combined Product + Blog Demo",
            "description": "Best of both: product features + thought leadership",
            "start_urls": [
                "https://buf.build/product",
                "https://buf.build/blog",
                "https://buf.build/features"
            ],
            "settings": {
                "max_pages": 50,
                "max_depth": 3,
                "delay": 2000,
                "include_patterns": [
                    ".*product.*",
                    ".*feature.*",
                    ".*blog.*",
                    ".*news.*",
                    ".*solution.*",
                    ".*platform.*"
                ],
                "exclude_patterns": [
                    ".*\\.pdf$",
                    ".*\\.(jpg|png|gif)$",
                    ".*\\.css$", 
                    ".*\\.js$",
                    ".*docs/reference.*",  # Skip heavy API docs
                    ".*legal.*",
                    ".*privacy.*"
                ]
            }
        }
    }
    
    return configs

def update_firecrawl_engine_for_priority():
    """Generate code to update the Firecrawl engine with priority URL handling."""
    
    logger.info("🔧 FIRECRAWL ENGINE UPDATES FOR PRIORITY CRAWLING")
    logger.info("=" * 60)
    
    code_updates = '''
# Add this to your FirecrawlCrawler class in firecrawl_engine.py

def get_priority_urls(self, domain: str) -> List[str]:
    """Get prioritized URLs for crawling based on domain."""
    
    priority_patterns = {
        "buf.build": [
            f"{domain}/product",
            f"{domain}/features", 
            f"{domain}/blog",
            f"{domain}/platform",
            f"{domain}/solutions",
            f"{domain}/pricing"
        ]
    }
    
    # Extract base domain for pattern matching
    base_domain = domain.replace('https://', '').replace('http://', '').split('/')[0]
    
    if any(pattern in base_domain for pattern in priority_patterns.keys()):
        return priority_patterns.get("buf.build", [domain])
    
    return [domain]

def is_priority_content(self, url: str, title: str = "", content: str = "") -> bool:
    """Determine if content is high-priority for the demo."""
    
    priority_indicators = [
        # Product-related
        'product', 'feature', 'solution', 'platform', 'pricing',
        'use case', 'customer story', 'case study',
        
        # Blog/content-related  
        'blog', 'news', 'article', 'post', 'announcement',
        'thought leadership', 'insights', 'trends'
    ]
    
    url_lower = url.lower()
    title_lower = title.lower()
    
    # Check URL for priority indicators
    url_score = sum(1 for indicator in priority_indicators if indicator in url_lower)
    
    # Check title for priority indicators
    title_score = sum(1 for indicator in priority_indicators if indicator in title_lower)
    
    # Priority if either URL or title has indicators
    return url_score > 0 or title_score > 0

# Update the crawl method to use priority URLs:

def crawl_with_priority(self):
    """Enhanced crawl method that prioritizes product and blog content."""
    
    logger.info(f"🎯 Starting priority-focused crawl for {self.domain}")
    
    # Get priority URLs to try
    priority_urls = self.get_priority_urls(self.domain)
    
    for attempt_url in priority_urls:
        logger.info(f"🔄 Attempting priority URL: {attempt_url}")
        
        # Test single page access
        if self._test_single_page_access(attempt_url):
            # If accessible, use this as starting point
            return self._crawl_from_url(attempt_url)
    
    # Fallback to original domain
    logger.info("🔄 Falling back to original crawl method")
    return self.crawl()
'''
    
    logger.info("Code updates to add to your Firecrawl engine:")
    logger.info(code_updates)

def generate_demo_commands():
    """Generate specific commands for running the prioritized demo."""
    
    logger.info("\\n🎬 DEMO EXECUTION COMMANDS")
    logger.info("=" * 60)
    
    commands = [
        {
            "step": "1. Discover Priority URLs",
            "command": "python prioritize_product_blog_crawl.py",
            "description": "Find all product and blog URLs on buf.build"
        },
        {
            "step": "2. Test Priority URLs",
            "command": "python check_buf_build_sitemap.py", 
            "description": "Check which URLs are actually accessible"
        },
        {
            "step": "3. Configure Crawler",
            "description": "Set these in your crawler UI:",
            "settings": {
                "Primary URL": "https://buf.build/product",
                "Fallback URLs": ["https://buf.build/blog", "https://buf.build/features"],
                "Max Pages": 30,
                "Max Depth": 3,
                "Delay": 2000
            }
        },
        {
            "step": "4. Demo Talking Points",
            "description": "Emphasize these aspects:",
            "points": [
                "Product feature extraction for competitive analysis",
                "Blog content for thought leadership insights", 
                "Business-focused content categorization",
                "Marketing and sales enablement use cases"
            ]
        }
    ]
    
    for cmd in commands:
        logger.info(f"\\n{cmd['step']}")
        if 'command' in cmd:
            logger.info(f"   Command: {cmd['command']}")
        if 'settings' in cmd:
            logger.info("   Settings:")
            for key, value in cmd['settings'].items():
                logger.info(f"     {key}: {value}")
        if 'points' in cmd:
            logger.info("   Points:")
            for point in cmd['points']:
                logger.info(f"     • {point}")
        logger.info(f"   Description: {cmd['description']}")

def main():
    logger.info("🎯 PRODUCT & BLOG PRIORITIZED CRAWLING SETUP")
    logger.info("Optimizing buf.build crawl for maximum demo impact")
    
    # Show priority URLs
    priority_urls = get_priority_crawl_urls()
    logger.info("\\n📋 PRIORITY URLS TO TARGET:")
    for category, urls in priority_urls.items():
        logger.info(f"\\n{category.upper()}:")
        for url in urls:
            logger.info(f"   • {url}")
    
    # Show configurations
    configs = create_enhanced_firecrawl_config()
    logger.info("\\n⚙️ RECOMMENDED CONFIGURATIONS:")
    for config_name, config in configs.items():
        logger.info(f"\\n{config['name']}:")
        logger.info(f"   Description: {config['description']}")
        logger.info(f"   Start URLs: {len(config['start_urls'])} URLs")
        logger.info(f"   Max Pages: {config['settings']['max_pages']}")
    
    # Generate updates
    update_firecrawl_engine_for_priority()
    
    # Generate commands
    generate_demo_commands()
    
    logger.info("\\n💡 QUICK START RECOMMENDATION:")
    logger.info("   1. Run: python prioritize_product_blog_crawl.py")
    logger.info("   2. Use 'Combined Demo' configuration")
    logger.info("   3. Start with: https://buf.build/product")
    logger.info("   4. Expected: 20-40 high-value pages")

if __name__ == "__main__":
    main()
