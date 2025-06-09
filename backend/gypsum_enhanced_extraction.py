#!/usr/bin/env python3
"""
Integrated buf.build content extraction for VoiceForge demo.
Combines direct content extraction with Gypsum persona enrichment.
"""

import requests
import json
import uuid
import sys
import os
from datetime import datetime
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
import logging

# Add VoiceForge backend to path for imports
sys.path.append('/Users/andrewbrown/Sites/noosphere/github/voice-forge/backend')

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GypsumEnhancedContentExtractor:
    """Extract buf.build content and enhance with Gypsum persona data for VoiceForge demo."""
    
    def __init__(self, org_id: str, gypsum_api_url: str = "http://localhost:3001"):
        self.org_id = org_id
        self.gypsum_api_url = gypsum_api_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        # Initialize VoiceForge database connection
        self.db = self._init_voiceforge_db()
        
        # Fetch Gypsum context data
        self.gypsum_context = self._fetch_gypsum_context()
        
    def _init_voiceforge_db(self):
        """Initialize VoiceForge database connection."""
        try:
            from database.session import get_db_session
            from database.db import Database
            
            session = get_db_session()
            db = Database(session)
            logger.info("✅ Connected to VoiceForge database")
            return db
        except Exception as e:
            logger.error(f"❌ Failed to connect to VoiceForge database: {e}")
            return None
    
    def _fetch_gypsum_context(self) -> Dict[str, Any]:
        """Fetch persona and messaging context from Gypsum."""
        try:
            logger.info(f"🔗 Fetching Gypsum context for org: {self.org_id}")
            
            # Use demo user ID if provided, otherwise use org_id
            demo_user_id = "123e4567-e89b-12d3-a456-426614174000"
            user_id = demo_user_id if self.org_id == "demo" else self.org_id
            
            # Fetch all context data
            messaging_response = requests.get(
                f"{self.gypsum_api_url}/api/messaging/context",
                params={"user_id": user_id},
                timeout=10
            )
            
            personas_response = requests.get(
                f"{self.gypsum_api_url}/api/personas/context", 
                params={"user_id": user_id},
                timeout=10
            )
            
            positioning_response = requests.get(
                f"{self.gypsum_api_url}/api/positioning/context",
                params={"user_id": user_id}, 
                timeout=10
            )
            
            context = {}
            
            if messaging_response.status_code == 200:
                context['messaging'] = messaging_response.json()
                logger.info("✅ Fetched messaging context from Gypsum")
            else:
                logger.warning(f"⚠️ Messaging context unavailable: {messaging_response.status_code}")
                context['messaging'] = self._get_default_messaging()
            
            if personas_response.status_code == 200:
                context['personas'] = personas_response.json()
                logger.info(f"✅ Fetched {len(context['personas'].get('personas', []))} personas from Gypsum")
            else:
                logger.warning(f"⚠️ Personas context unavailable: {personas_response.status_code}")
                context['personas'] = self._get_default_personas()
            
            if positioning_response.status_code == 200:
                context['positioning'] = positioning_response.json()
                logger.info("✅ Fetched positioning context from Gypsum")
            else:
                logger.warning(f"⚠️ Positioning context unavailable: {positioning_response.status_code}")
                context['positioning'] = self._get_default_positioning()
            
            return context
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to fetch Gypsum context: {e}")
            return {
                'messaging': self._get_default_messaging(),
                'personas': self._get_default_personas(),
                'positioning': self._get_default_positioning()
            }
    
    def _get_default_messaging(self) -> Dict[str, Any]:
        """Default messaging for demo when Gypsum unavailable."""
        return {
            "elevator_pitch": "AI-powered content extraction and analysis platform",
            "headline_message": "Transform any website into actionable business intelligence",
            "tone_voice": "professional",
            "key_differentiators": ["AI-powered extraction", "Multi-format support", "Enterprise-ready"]
        }
    
    def _get_default_personas(self) -> Dict[str, Any]:
        """Default personas for demo when Gypsum unavailable."""
        return {
            "personas": [
                {
                    "id": "default-cto",
                    "role": "Chief Technology Officer",
                    "seniority_level": "executive",
                    "pain_points": ["Managing complex tech stack", "API standardization"],
                    "goals": ["Improve developer productivity", "Standardize protocols"],
                    "industry": "B2B SaaS",
                    "tech_stack": ["Protocol Buffers", "gRPC", "Kubernetes"]
                }
            ]
        }
    
    def _get_default_positioning(self) -> Dict[str, Any]:
        """Default positioning for demo when Gypsum unavailable."""
        return {
            "target_market": "B2B SaaS companies",
            "category": "Content Intelligence Platform", 
            "differentiation": "AI-powered content extraction with persona enrichment"
        }

    def discover_buf_build_content(self) -> List[str]:
        """Discover high-value buf.build URLs for extraction."""
        
        logger.info("🔍 Discovering buf.build content URLs...")
        
        # Priority URLs for buf.build demo
        priority_urls = [
            "https://buf.build/product/bufstream",
            "https://buf.build/product", 
            "https://buf.build/platform",
            "https://buf.build/solutions",
            "https://buf.build/docs",
            "https://buf.build/blog",
            "https://buf.build"
        ]
        
        # Test which URLs are accessible
        accessible_urls = []
        
        for url in priority_urls:
            try:
                response = requests.head(url, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    accessible_urls.append(url)
                    logger.info(f"✅ Accessible: {url}")
                else:
                    logger.info(f"❌ Not accessible: {url} ({response.status_code})")
            except Exception as e:
                logger.info(f"❌ Error checking {url}: {e}")
        
        # Also try to discover additional URLs from main pages
        discovered_urls = self._discover_additional_urls(accessible_urls)
        
        # Combine and deduplicate
        all_urls = list(set(accessible_urls + discovered_urls))
        
        logger.info(f"🎯 Found {len(all_urls)} accessible URLs for extraction")
        return all_urls[:20]  # Limit to top 20 for demo
    
    def _discover_additional_urls(self, base_urls: List[str]) -> List[str]:
        """Discover additional URLs from accessible pages."""
        
        discovered = []
        
        for base_url in base_urls[:3]:  # Only check first 3 to save time
            try:
                response = requests.get(base_url, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Find internal links
                    links = soup.find_all('a', href=True)
                    for link in links:
                        href = link.get('href')
                        if href and self._is_valuable_link(href):
                            if href.startswith('/'):
                                full_url = f"https://buf.build{href}"
                            elif href.startswith('http') and 'buf.build' in href:
                                full_url = href
                            else:
                                continue
                            
                            if full_url not in discovered:
                                discovered.append(full_url)
                
            except Exception as e:
                logger.warning(f"Error discovering from {base_url}: {e}")
        
        return discovered[:10]  # Limit discoveries
    
    def _is_valuable_link(self, href: str) -> bool:
        """Determine if a link is valuable for extraction."""
        valuable_patterns = [
            'product', 'platform', 'solution', 'feature', 
            'blog', 'news', 'case-study', 'customer',
            'pricing', 'docs', 'guide', 'tutorial'
        ]
        
        exclude_patterns = [
            '.pdf', '.jpg', '.png', '.css', '.js',
            'login', 'signup', 'contact', 'privacy',
            'terms', 'legal', '#', 'mailto:', 'tel:'
        ]
        
        href_lower = href.lower()
        
        # Exclude unwanted patterns
        if any(pattern in href_lower for pattern in exclude_patterns):
            return False
        
        # Include valuable patterns
        return any(pattern in href_lower for pattern in valuable_patterns)

    def extract_enhanced_content(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract content and enhance with Gypsum persona context."""
        
        logger.info(f"📖 Extracting enhanced content from: {url}")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                element.decompose()
            
            # Extract basic content
            title = self._extract_title(soup)
            text_content = self._extract_text_content(soup)
            html_content = self._extract_html_content(soup)
            description = self._extract_description(soup)
            
            # Enhance with Gypsum context
            enhanced_metadata = self._enhance_with_gypsum_context(url, title, text_content)
            
            # Determine content type and persona relevance
            content_type = self._determine_content_type(url, title, text_content)
            persona_relevance = self._analyze_persona_relevance(text_content, title)
            
            return {
                'content_id': str(uuid.uuid4()),
                'url': url,
                'domain': 'https://buf.build',
                'text': text_content,
                'html': html_content,
                'crawl_id': str(uuid.uuid4()),
                'extracted_at': datetime.utcnow(),
                'metadata': {
                    'title': title,
                    'description': description,
                    'content_type': content_type,
                    'language': 'en',
                    'author': None,
                    'publication_date': None,
                    'last_modified': None,
                    'categories': [],
                    'tags': self._extract_tags(text_content, title),
                    'source_url': url,
                    
                    # Gypsum enhancements
                    'gypsum_enhanced': True,
                    'persona_relevance': persona_relevance,
                    'messaging_context': enhanced_metadata['messaging'],
                    'positioning_context': enhanced_metadata['positioning'],
                    'relevant_personas': enhanced_metadata['relevant_personas'],
                    
                    # Extraction metadata
                    'extraction_method': 'direct_gypsum_enhanced',
                    'extraction_timestamp': datetime.utcnow().isoformat(),
                    'word_count': len(text_content.split()),
                    'enhancement_version': '1.0'
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to extract content from {url}: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        if soup.title:
            return soup.title.string.strip()
        elif soup.find('h1'):
            return soup.find('h1').get_text().strip()
        return ""
    
    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract clean text content."""
        # Try to find main content areas
        main_content = None
        for selector in ['main', 'article', '[role="main"]', '.content', '.main-content']:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        if not main_content:
            main_content = soup.body
        
        if main_content:
            text = main_content.get_text(separator=' ', strip=True)
            return ' '.join(text.split())  # Clean up whitespace
        
        return ""
    
    def _extract_html_content(self, soup: BeautifulSoup) -> str:
        """Extract HTML content."""
        main_content = soup.select_one('main') or soup.body
        return str(main_content) if main_content else ""
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description."""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            return meta_desc.get('content', '')
        return ""
    
    def _determine_content_type(self, url: str, title: str, content: str) -> str:
        """Determine content type with buf.build specifics."""
        url_lower = url.lower()
        
        if '/product/' in url_lower:
            return 'product_page'
        elif any(kw in url_lower for kw in ['/blog/', '/news/']):
            return 'blog_post'
        elif '/docs/' in url_lower:
            return 'documentation'
        elif any(kw in url_lower for kw in ['/platform', '/solutions']):
            return 'platform_overview'
        elif '/pricing' in url_lower:
            return 'pricing_page'
        else:
            return 'webpage'
    
    def _extract_tags(self, text: str, title: str) -> List[str]:
        """Extract relevant tags based on content."""
        # buf.build specific tags
        buf_tags = []
        content_lower = (text + ' ' + title).lower()
        
        tag_patterns = {
            'protocol-buffers': ['protobuf', 'protocol buffer', '.proto'],
            'grpc': ['grpc', 'grpc-web'],
            'api-development': ['api', 'rest', 'graphql'],
            'microservices': ['microservice', 'distributed', 'service mesh'],
            'developer-tools': ['cli', 'sdk', 'tool', 'development'],
            'enterprise': ['enterprise', 'scale', 'production'],
            'integration': ['integrate', 'connect', 'plugin']
        }
        
        for tag, patterns in tag_patterns.items():
            if any(pattern in content_lower for pattern in patterns):
                buf_tags.append(tag)
        
        return buf_tags
    
    def _enhance_with_gypsum_context(self, url: str, title: str, content: str) -> Dict[str, Any]:
        """Enhance content with Gypsum persona and messaging context."""
        
        # Get messaging context
        messaging = self.gypsum_context.get('messaging', {})
        positioning = self.gypsum_context.get('positioning', {})
        personas = self.gypsum_context.get('personas', {}).get('personas', [])
        
        # Find relevant personas for this content
        relevant_personas = []
        for persona in personas:
            relevance_score = self._calculate_persona_relevance(persona, content, title)
            if relevance_score > 0.3:  # Threshold for relevance
                relevant_personas.append({
                    'persona_id': persona.get('id'),
                    'role': persona.get('role'),
                    'relevance_score': relevance_score,
                    'relevant_pain_points': self._find_relevant_pain_points(persona, content),
                    'relevant_goals': self._find_relevant_goals(persona, content)
                })
        
        return {
            'messaging': {
                'tone_voice': messaging.get('tone_voice', 'professional'),
                'key_differentiators': messaging.get('key_differentiators', []),
                'value_proposition': messaging.get('value_proposition', '')
            },
            'positioning': {
                'target_market': positioning.get('target_market', ''),
                'category': positioning.get('category', ''),
                'differentiation': positioning.get('differentiation', '')
            },
            'relevant_personas': relevant_personas
        }
    
    def _calculate_persona_relevance(self, persona: Dict, content: str, title: str) -> float:
        """Calculate how relevant this content is to a specific persona."""
        
        content_lower = (content + ' ' + title).lower()
        relevance_score = 0.0
        
        # Check tech stack alignment
        tech_stack = persona.get('tech_stack', [])
        for tech in tech_stack:
            if tech.lower() in content_lower:
                relevance_score += 0.2
        
        # Check pain points alignment
        pain_points = persona.get('pain_points', [])
        for pain_point in pain_points:
            if any(word in content_lower for word in pain_point.lower().split()[:3]):
                relevance_score += 0.15
        
        # Check goals alignment
        goals = persona.get('goals', [])
        for goal in goals:
            if any(word in content_lower for word in goal.lower().split()[:3]):
                relevance_score += 0.15
        
        # Check seniority level content alignment
        seniority = persona.get('seniority_level', '')
        if seniority == 'executive' and any(word in content_lower for word in ['strategy', 'business', 'roi', 'enterprise']):
            relevance_score += 0.1
        elif seniority == 'manager' and any(word in content_lower for word in ['team', 'process', 'productivity']):
            relevance_score += 0.1
        elif seniority in ['individual', 'developer'] and any(word in content_lower for word in ['code', 'api', 'development', 'tools']):
            relevance_score += 0.1
        
        return min(relevance_score, 1.0)  # Cap at 1.0
    
    def _find_relevant_pain_points(self, persona: Dict, content: str) -> List[str]:
        """Find persona pain points mentioned in the content."""
        content_lower = content.lower()
        relevant = []
        
        for pain_point in persona.get('pain_points', []):
            if any(word in content_lower for word in pain_point.lower().split()[:3]):
                relevant.append(pain_point)
        
        return relevant
    
    def _find_relevant_goals(self, persona: Dict, content: str) -> List[str]:
        """Find persona goals mentioned in the content."""
        content_lower = content.lower()
        relevant = []
        
        for goal in persona.get('goals', []):
            if any(word in content_lower for word in goal.lower().split()[:3]):
                relevant.append(goal)
        
        return relevant
    
    def _analyze_persona_relevance(self, content: str, title: str) -> Dict[str, float]:
        """Analyze which persona types this content is most relevant for."""
        
        content_lower = (content + ' ' + title).lower()
        
        relevance_scores = {
            'executive': 0.0,
            'director': 0.0, 
            'manager': 0.0,
            'individual_contributor': 0.0
        }
        
        # Executive relevance indicators
        if any(word in content_lower for word in ['strategy', 'business', 'roi', 'enterprise', 'scale', 'competitive']):
            relevance_scores['executive'] += 0.3
        
        # Director relevance indicators  
        if any(word in content_lower for word in ['architecture', 'platform', 'infrastructure', 'standards']):
            relevance_scores['director'] += 0.3
        
        # Manager relevance indicators
        if any(word in content_lower for word in ['team', 'process', 'productivity', 'workflow', 'collaboration']):
            relevance_scores['manager'] += 0.3
        
        # Individual contributor relevance indicators
        if any(word in content_lower for word in ['code', 'api', 'development', 'tools', 'implementation', 'tutorial']):
            relevance_scores['individual_contributor'] += 0.3
        
        return relevance_scores

    def save_to_voiceforge(self, content_data: Dict[str, Any]) -> bool:
        """Save enhanced content to VoiceForge database or JSON fallback."""
        
        if self.db:
            try:
                success = self.db.save_content(content_data, self.org_id)
                if success:
                    logger.info(f"✅ Saved enhanced content to database: {content_data['url']}")
                    return True
                else:
                    logger.error(f"❌ Failed to save content to database: {content_data['url']}")
                    return self._save_to_json_fallback(content_data)
                    
            except Exception as e:
                logger.error(f"❌ Error saving to database: {e}")
                return self._save_to_json_fallback(content_data)
        else:
            # No database connection - save to JSON for demo
            return self._save_to_json_fallback(content_data)
    
    def _save_to_json_fallback(self, content_data: Dict[str, Any]) -> bool:
        """Save content to JSON file as fallback for demo purposes."""
        try:
            # Create demo output directory
            import os
            output_dir = "demo_extracted_content"
            os.makedirs(output_dir, exist_ok=True)
            
            # Create filename from URL
            url_slug = content_data['url'].replace('https://', '').replace('/', '_').replace('?', '_')
            filename = f"{output_dir}/{url_slug}.json"
            
            # Convert datetime objects to strings for JSON serialization
            json_content = self._prepare_for_json(content_data)
            
            # Save to JSON file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(json_content, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Saved enhanced content to JSON: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving to JSON: {e}")
            return False
    
    def _prepare_for_json(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare content data for JSON serialization."""
        json_data = content_data.copy()
        
        # Convert datetime objects to ISO strings
        if isinstance(json_data.get('extracted_at'), datetime):
            json_data['extracted_at'] = json_data['extracted_at'].isoformat()
        
        if 'metadata' in json_data and 'extraction_timestamp' in json_data['metadata']:
            if isinstance(json_data['metadata']['extraction_timestamp'], datetime):
                json_data['metadata']['extraction_timestamp'] = json_data['metadata']['extraction_timestamp'].isoformat()
        
        return json_data

    def run_demo_extraction(self) -> Dict[str, Any]:
        """Run complete demo extraction process."""
        
        logger.info("🚀 Starting enhanced buf.build demo extraction")
        logger.info("=" * 60)
        
        # Step 1: Discover content URLs
        urls = self.discover_buf_build_content()
        
        if not urls:
            logger.error("❌ No accessible URLs found")
            return {'success': False, 'error': 'No accessible URLs'}
        
        # Step 2: Extract and enhance content
        extracted_count = 0
        saved_count = 0
        failed_count = 0
        
        for i, url in enumerate(urls, 1):
            logger.info(f"\n📖 Processing {i}/{len(urls)}: {url}")
            
            # Extract enhanced content
            content_data = self.extract_enhanced_content(url)
            
            if content_data:
                extracted_count += 1
                
                # Save to VoiceForge database
                if self.save_to_voiceforge(content_data):
                    saved_count += 1
                else:
                    failed_count += 1
            else:
                failed_count += 1
        
        # Step 3: Report results
        results = {
            'success': True,
            'urls_discovered': len(urls),
            'content_extracted': extracted_count,
            'content_saved': saved_count,
            'content_failed': failed_count,
            'gypsum_context_available': bool(self.gypsum_context),
            'personas_count': len(self.gypsum_context.get('personas', {}).get('personas', [])),
            'extraction_method': 'direct_gypsum_enhanced',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info("\n" + "=" * 60)
        logger.info("🎯 DEMO EXTRACTION COMPLETE")
        logger.info(f"✅ URLs discovered: {results['urls_discovered']}")
        logger.info(f"✅ Content extracted: {results['content_extracted']}")
        logger.info(f"✅ Content saved: {results['content_saved']}")
        logger.info(f"❌ Failed: {results['content_failed']}")
        logger.info(f"🧠 Gypsum personas: {results['personas_count']}")
        logger.info(f"🔗 Gypsum integration: {'✅' if results['gypsum_context_available'] else '❌'}")
        
        if not self.db:
            logger.info(f"📁 Content saved to: demo_extracted_content/ (JSON files)")
            logger.info(f"📝 For demo: Review JSON files to see persona-enhanced content")
        
        return results

def main():
    """Run the enhanced extraction demo."""
    
    print("🎯 GYPSUM-ENHANCED BUF.BUILD EXTRACTION")
    print("Direct content extraction with persona enrichment")
    print("=" * 60)
    
    # Configuration
    org_id = "demo"  # Use demo org for testing
    gypsum_api_url = "http://localhost:3001"
    
    # Initialize extractor
    try:
        extractor = GypsumEnhancedContentExtractor(org_id, gypsum_api_url)
        
        # Run extraction
        results = extractor.run_demo_extraction()
        
        if results['success'] and results['content_saved'] > 0:
            if extractor.db:
                print(f"\n🎉 DEMO SUCCESS!")
                print(f"   • {results['content_saved']} pages extracted and enhanced")
                print(f"   • {results['personas_count']} Gypsum personas integrated")
                print(f"   • Content now available in VoiceForge with persona context")
            else:
                print(f"\n🎉 DEMO SUCCESS!")
                print(f"   • {results['content_saved']} pages extracted and enhanced")
                print(f"   • {results['personas_count']} Gypsum personas integrated")
                print(f"   • Content saved to demo_extracted_content/ folder (JSON files)")
                print(f"   • Review JSON files to see persona-enhanced content")
            
            print(f"\n💡 Next Steps:")
            if extractor.db:
                print(f"   • Start VoiceForge and browse the extracted content")
                print(f"   • Test AI generation with persona-enhanced prompts")
            else:
                print(f"   • Review JSON files in demo_extracted_content/")
                print(f"   • Set up VoiceForge database connection for full integration")
            print(f"   • Demo the integrated Gypsum + VoiceForge workflow")
        else:
            print(f"\n❌ DEMO FAILED: {results.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"\n💥 EXTRACTION ERROR: {e}")
        print("Check that both VoiceForge backend and Gypsum API are running")

if __name__ == "__main__":
    main()
