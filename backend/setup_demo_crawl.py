#!/usr/bin/env python3
"""
Quick demo setup - find sites that work well for crawling demonstrations.
"""

import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def suggest_demo_sites():
    """Suggest websites that work well for crawling demos."""
    
    logger.info("🎯 DEMO-FRIENDLY WEBSITES")
    logger.info("=" * 60)
    
    demo_sites = [
        {
            "name": "Documentation Sites",
            "sites": [
                "docs.python.org",
                "docs.docker.com", 
                "kubernetes.io/docs",
                "reactjs.org/docs",
                "vuejs.org/guide"
            ],
            "why": "Rich content, good internal linking, crawler-friendly",
            "expected_pages": "20-100 pages",
            "demo_value": "Shows technical content extraction capabilities"
        },
        {
            "name": "Open Source Projects",
            "sites": [
                "github.com/microsoft/vscode/wiki",
                "numpy.org/doc",
                "fastapi.tiangolo.com",
                "flask.palletsprojects.com",
                "django-project.com"
            ],
            "why": "Public, well-structured, lots of content",
            "expected_pages": "50-200 pages", 
            "demo_value": "Demonstrates handling of complex technical documentation"
        },
        {
            "name": "News/Blog Sites",
            "sites": [
                "blog.github.com",
                "engineering.fb.com",
                "netflixtechblog.com",
                "aws.amazon.com/blogs",
                "medium.com/@your-favorite-tech-blog"
            ],
            "why": "Regular content updates, good for showing article extraction",
            "expected_pages": "30-100 pages",
            "demo_value": "Shows content categorization and metadata extraction"
        },
        {
            "name": "Company Pages (Usually Crawler-Friendly)",
            "sites": [
                "stripe.com/docs",
                "auth0.com/docs", 
                "twilio.com/docs",
                "sendgrid.com/docs",
                "mailgun.com/docs"
            ],
            "why": "Want their docs to be discoverable, usually allow crawlers",
            "expected_pages": "50-300 pages",
            "demo_value": "Shows real-world business use case"
        },
        {
            "name": "Educational/Tutorial Sites", 
            "sites": [
                "developer.mozilla.org",
                "w3schools.com",
                "tutorialspoint.com",
                "freeCodeCamp.org/news",
                "codecademy.com/articles"
            ],
            "why": "Designed to be accessible, lots of structured content",
            "expected_pages": "100-500 pages",
            "demo_value": "Shows educational content processing"
        }
    ]
    
    for category in demo_sites:
        logger.info(f"\n📁 {category['name']}")
        logger.info(f"   Why good for demo: {category['why']}")
        logger.info(f"   Expected pages: {category['expected_pages']}")
        logger.info(f"   Demo value: {category['demo_value']}")
        logger.info("   Recommended sites:")
        for site in category['sites']:
            logger.info(f"     • {site}")

def quick_demo_config():
    """Provide optimal configuration for demo crawling."""
    
    logger.info("\n⚡ QUICK DEMO CONFIGURATION")
    logger.info("=" * 60)
    
    configs = [
        {
            "name": "5-Minute Demo",
            "recommended_site": "docs.python.org/3/tutorial",
            "settings": {
                "max_pages": 25,
                "max_depth": 2,
                "delay": 1000
            },
            "expected_result": "15-25 pages of Python tutorial content",
            "demo_talking_points": [
                "Technical documentation extraction",
                "Code snippet preservation", 
                "Hierarchical content structure"
            ]
        },
        {
            "name": "10-Minute Demo", 
            "recommended_site": "fastapi.tiangolo.com",
            "settings": {
                "max_pages": 50,
                "max_depth": 3,
                "delay": 1000
            },
            "expected_result": "30-50 pages of API documentation",
            "demo_talking_points": [
                "API documentation crawling",
                "Multi-format content (markdown, code, examples)",
                "Cross-referenced documentation links"
            ]
        },
        {
            "name": "Comprehensive Demo",
            "recommended_site": "kubernetes.io/docs",
            "settings": {
                "max_pages": 100,
                "max_depth": 4,
                "delay": 1500
            },
            "expected_result": "50-100 pages of Kubernetes documentation", 
            "demo_talking_points": [
                "Large-scale documentation processing",
                "Complex technical content",
                "Deep link following and content discovery"
            ]
        }
    ]
    
    for config in configs:
        logger.info(f"\n🎯 {config['name']}")
        logger.info(f"   Recommended site: {config['recommended_site']}")
        logger.info(f"   Settings: {config['settings']}")
        logger.info(f"   Expected result: {config['expected_result']}")
        logger.info("   Demo talking points:")
        for point in config['demo_talking_points']:
            logger.info(f"     • {point}")

def backup_demo_sites():
    """Provide backup sites if primary recommendations don't work."""
    
    logger.info("\n🔄 BACKUP DEMO SITES")
    logger.info("=" * 60)
    
    backup_sites = [
        {
            "site": "httpbin.org",
            "why": "Always works, shows HTTP request/response handling",
            "pages": "5-10 pages",
            "note": "Fallback if other sites have issues"
        },
        {
            "site": "example.com (and subpages)",
            "why": "Designed for testing, always accessible",
            "pages": "1-5 pages", 
            "note": "Last resort for basic functionality demo"
        },
        {
            "site": "jsonplaceholder.typicode.com",
            "why": "API testing site, crawler-friendly",
            "pages": "10-20 pages",
            "note": "Good for showing API endpoint discovery"
        }
    ]
    
    logger.info("If your primary demo sites don't work, try these:")
    for site in backup_sites:
        logger.info(f"\n• {site['site']}")
        logger.info(f"  Why: {site['why']}")
        logger.info(f"  Expected pages: {site['pages']}")
        logger.info(f"  Note: {site['note']}")

def production_talking_points():
    """Key points to mention about production use vs demo."""
    
    logger.info("\n💼 PRODUCTION VS DEMO TALKING POINTS")
    logger.info("=" * 60)
    
    points = [
        {
            "topic": "User Agent Whitelisting",
            "demo_limitation": "Demo uses generic crawlers that may be blocked",
            "production_reality": "Customers whitelist your specific user-agent for full access",
            "customer_benefit": "No bot protection issues, complete site access"
        },
        {
            "topic": "Crawl Scope",
            "demo_limitation": "Demo crawls public documentation sites",
            "production_reality": "Customers crawl their own internal/private content", 
            "customer_benefit": "Access to proprietary knowledge bases and internal docs"
        },
        {
            "topic": "Rate Limiting",
            "demo_limitation": "Demo must be respectful of public sites",
            "production_reality": "Customers control their own infrastructure",
            "customer_benefit": "Faster crawling, higher throughput"
        },
        {
            "topic": "Content Types",
            "demo_limitation": "Demo shows mostly technical documentation", 
            "production_reality": "Customers have diverse content: support docs, wikis, blogs, etc.",
            "customer_benefit": "Complete organizational knowledge capture"
        }
    ]
    
    for point in points:
        logger.info(f"\n📋 {point['topic']}")
        logger.info(f"   Demo: {point['demo_limitation']}")
        logger.info(f"   Production: {point['production_reality']}")
        logger.info(f"   Value: {point['customer_benefit']}")

if __name__ == "__main__":
    logger.info("🎬 DEMO SETUP GUIDE")
    logger.info("Setting up crawler for effective demonstration")
    
    suggest_demo_sites()
    quick_demo_config()
    backup_demo_sites()
    production_talking_points()
    
    logger.info("\n" + "=" * 60)
    logger.info("🎯 RECOMMENDED QUICK START:")
    logger.info("1. Try: docs.python.org/3/tutorial")
    logger.info("2. Settings: 25 pages, depth 2")
    logger.info("3. Expected: 15-25 pages in ~2 minutes")
    logger.info("4. Backup: fastapi.tiangolo.com if Python docs don't work")
