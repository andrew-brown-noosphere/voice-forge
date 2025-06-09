"""
Content-Driven Signal Intelligence Service
Uses VoiceForge vectorized content as primary intelligence source for multi-platform signal discovery
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from openai import AsyncOpenAI

aclient = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
logger = logging.getLogger(__name__)


class ContentDrivenSignalAI:
    """AI service that analyzes VoiceForge content to generate intelligent signal discovery strategies"""

    def __init__(self, voiceforge_db=None, gypsum_client=None):
        self.voiceforge_db = voiceforge_db
        self.gypsum_client = gypsum_client
        self.logger = logging.getLogger(__name__)

    async def generate_content_driven_searches(
        self, 
        org_id: str, 
        selected_persona_id: Optional[str], 
        platforms: List[str],
        options: Dict[str, Any] = {}
    ) -> Dict[str, Any]:
        """
        Generate multi-platform searches based on VoiceForge content + Gypsum personas
        
        Args:
            org_id: Organization ID
            selected_persona_id: ID of target persona from Gypsum
            platforms: List of platforms to generate searches for (reddit, linkedin, github, twitter)
            options: Configuration options
        
        Returns:
            Comprehensive search strategy for all platforms
        """
        try:
            self.logger.info(f'🧠 Starting content-driven signal generation for platforms: {platforms}')

            # Step 1: Analyze VoiceForge content to understand the product/messaging
            content_analysis = await self.analyze_voiceforge_content(org_id)
            self.logger.info(f'📄 Content analysis complete: {content_analysis.get("summary", "No summary")}')

            # Step 2: Get target persona from Gypsum (or use default if none selected)
            persona_context = await self.get_gypsum_persona_context(org_id, selected_persona_id)
            selected_persona = persona_context.get('persona')

            if not selected_persona:
                if selected_persona_id:
                    raise ValueError(f'Selected persona {selected_persona_id} not found')
                else:
                    # Use fallback persona when none is selected
                    selected_persona = self.get_fallback_persona()
                    self.logger.info('Using fallback persona for strategy generation')

            # Step 3: Generate unified search strategy
            search_strategy = await self.generate_unified_search_strategy(
                content_analysis, 
                selected_persona, 
                platforms, 
                options
            )

            # Step 4: Create platform-specific queries and sources
            platform_strategies = {}
            for platform in platforms:
                platform_strategies[platform] = await self.create_platform_strategy(
                    platform, 
                    search_strategy, 
                    content_analysis, 
                    selected_persona
                )

            return {
                'content_analysis': content_analysis,
                'selected_persona': selected_persona,
                'search_strategy': search_strategy,
                'platform_strategies': platform_strategies,
                'execution_plan': self.create_execution_plan(platform_strategies),
                'metadata': {
                    'generated_at': datetime.utcnow().isoformat(),
                    'platforms': platforms,
                    'persona_id': selected_persona_id,
                    'org_id': org_id
                }
            }

        except Exception as e:
            self.logger.error(f'Error in content-driven search generation: {str(e)}')
            raise

    async def analyze_voiceforge_content(self, org_id: str) -> Dict[str, Any]:
        """
        Analyze VoiceForge vectorized content to extract product understanding
        """
        try:
            self.logger.info(f'📊 Analyzing VoiceForge content for org {org_id}')

            # Get content samples from VoiceForge database
            content_samples = await self.get_voiceforge_content_samples(org_id)

            if not content_samples:
                self.logger.warning('❌ No VoiceForge content found, using fallback analysis')
                fallback = self.get_fallback_content_analysis()
                fallback['content_analysis_status'] = 'no_content_found'
                return fallback

            self.logger.info(f'✅ Found {len(content_samples)} content samples, analyzing with OpenAI...')

            # Use OpenAI to analyze content and extract key insights
            analysis_prompt = self.build_content_analysis_prompt(content_samples)

            response = await aclient.chat.completions.create(model="gpt-4",
            messages=[{"role": "user", "content": analysis_prompt}],
            temperature=0.2)

            # Parse AI response
            ai_analysis = json.loads(response.choices[0].message.content)
            
            self.logger.info(f'🧠 OpenAI content analysis complete:')
            self.logger.info(f'   Primary industry: {ai_analysis.get("industry_positioning", {}).get("primary_industry", "unknown")}')
            self.logger.info(f'   Technical keywords: {ai_analysis.get("technical_keywords", [])}')
            self.logger.info(f'   Key features: {ai_analysis.get("key_features", [])}')
            self.logger.info(f'   Problems addressed: {ai_analysis.get("problems_addressed", [])}')

            # Enhance with our own analysis
            enhanced_analysis = {
                **ai_analysis,
                'content_metadata': {
                    'total_pieces': len(content_samples),
                    'content_types': self.get_content_types(content_samples),
                    'analyzed_at': datetime.utcnow().isoformat(),
                    'source': 'voiceforge_vectorized'
                },
                'raw_insights': self.extract_raw_insights(content_samples),
                'content_analysis_status': 'success'
            }

            return enhanced_analysis

        except Exception as e:
            self.logger.error(f'❌ Error analyzing VoiceForge content: {str(e)}')
            fallback = self.get_fallback_content_analysis()
            fallback['content_analysis_status'] = f'error: {str(e)}'
            return fallback

    async def get_voiceforge_content_samples(self, org_id: str, limit: int = 100) -> List[Dict]:
        """Get representative content samples from VoiceForge with progressive fallback"""
        try:
            if not self.voiceforge_db:
                self.logger.warning('VoiceForge database not available')
                return []

            self.logger.info(f'Starting content search for org {org_id}')

            # STEP 1: Try specific high-value content types first
            specific_content_query = {
                'org_id': org_id,
                'content_types': ['landing_page', 'product_description', 'blog_post', 'about_page', 'feature_page'],
                'limit': limit,
                'sort_by': 'relevance',
                'min_length': 100,
                'include_metadata': True
            }
            
            content_samples = self.voiceforge_db.search_content(specific_content_query)
            self.logger.info(f'Specific content types search returned {len(content_samples)} samples')
            
            # STEP 2: If no specific content found, try broader search (lower min_length)
            if not content_samples:
                self.logger.info(f'No specific content types found, trying broader search with lower length requirement')
                
                broad_content_query = {
                    'org_id': org_id,
                    'content_types': ['landing_page', 'product_description', 'blog_post', 'about_page', 'feature_page'],
                    'limit': limit,
                    'min_length': 50,  # Lower minimum length
                    'include_metadata': True
                }
                
                content_samples = self.voiceforge_db.search_content(broad_content_query)
                self.logger.info(f'Broader search returned {len(content_samples)} samples')
            
            # STEP 3: If still no content, try ANY content type with length filter
            if not content_samples:
                self.logger.info(f'No content with specific types, trying any content type with length filter')
                
                any_content_query = {
                    'org_id': org_id,
                    'limit': limit,
                    'min_length': 50,
                    'include_metadata': True
                }
                
                content_samples = self.voiceforge_db.search_content(any_content_query)
                self.logger.info(f'Any content type search returned {len(content_samples)} samples')
            
            # STEP 4: If still no content, remove ALL filters and just get any content
            if not content_samples:
                self.logger.info(f'No content with length filter, trying any content without filters')
                
                minimal_query = {
                    'org_id': org_id,
                    'limit': limit,
                    'include_metadata': True
                }
                
                content_samples = self.voiceforge_db.search_content(minimal_query)
                self.logger.info(f'Minimal query returned {len(content_samples)} samples')
            
            # STEP 5: Debug what content actually exists
            if not content_samples:
                self.logger.warning(f'Still no content found! Checking what content exists for org {org_id}')
                
                # Try to get any content for debugging
                try:
                    debug_query = {'org_id': org_id, 'limit': 5}
                    debug_content = self.voiceforge_db.search_content(debug_query)
                    
                    if debug_content:
                        self.logger.info(f'Debug: Found {len(debug_content)} content pieces exist')
                        for i, content in enumerate(debug_content[:3]):
                            self.logger.info(f'Debug content {i+1}: type={content.get("content_type", "unknown")}, length={len(content.get("text", ""))}, title={content.get("title", "no title")[:50]}')
                    else:
                        self.logger.warning(f'Debug: No content found at all for org {org_id}')
                        
                        # Check if there are any crawls for this org
                        try:
                            from database.db import DatabaseService
                            db_service = DatabaseService()
                            recent_crawls = db_service.get_recent_crawls(org_id, limit=5)
                            self.logger.info(f'Debug: Found {len(recent_crawls)} recent crawls for org {org_id}')
                            
                            for crawl in recent_crawls:
                                self.logger.info(f'Debug crawl: {crawl.get("crawl_id", "unknown")} - {crawl.get("domain", "unknown")} - status: {crawl.get("status", "unknown")} - pages: {crawl.get("pages_found", 0)}')
                                
                        except Exception as debug_error:
                            self.logger.error(f'Debug crawl check failed: {str(debug_error)}')
                            
                except Exception as e:
                    self.logger.error(f'Debug content check failed: {str(e)}')
            
            # Log final results
            if content_samples:
                sample_info = [
                    {
                        'type': s.get('content_type', 'unknown'),
                        'domain': s.get('domain', 'unknown'),
                        'length': len(s.get('text', ''))
                    }
                    for s in content_samples[:3]
                ]
                self.logger.info(f'Final result: {len(content_samples)} content samples found. Sample info: {sample_info}')
            else:
                self.logger.warning(f'Final result: No content samples found for org {org_id}')
            
            return content_samples

        except Exception as e:
            self.logger.error(f'Error fetching VoiceForge content: {str(e)}')
            return []

    def build_content_analysis_prompt(self, content_samples: List[Dict]) -> str:
        """Build prompt for AI content analysis"""

        # Extract text content from samples
        content_texts = []
        for sample in content_samples[:20]:  # Limit to avoid token limits
            text = sample.get('text') or sample.get('content') or ''
            if text and len(text) > 50:
                content_texts.append(text[:500])  # Truncate long content

        combined_content = '\n\n---\n\n'.join(content_texts)

        return f"""
        Analyze this business content from VoiceForge to understand the product, positioning, and messaging:

        CONTENT SAMPLES:
        {combined_content}

        Extract and return JSON with the following structure:
        {{
            "primary_value_propositions": [
                "Main value prop 1",
                "Main value prop 2"
            ],
            "key_features": [
                "feature 1",
                "feature 2"
            ],
            "target_use_cases": [
                "use case 1",
                "use case 2"
            ],
            "problems_addressed": [
                "problem 1",
                "problem 2"
            ],
            "competitive_advantages": [
                "advantage 1",
                "advantage 2"
            ],
            "industry_positioning": {{
                "primary_industry": "industry name",
                "secondary_industries": ["industry 1", "industry 2"],
                "market_category": "category"
            }},
            "messaging_themes": [
                "theme 1",
                "theme 2"
            ],
            "customer_pain_points": [
                "pain point 1",
                "pain point 2"
            ],
            "solution_benefits": [
                "benefit 1",
                "benefit 2"
            ],
            "technical_keywords": [
                "keyword 1",
                "keyword 2"
            ],
            "emotional_triggers": [
                "trigger 1",
                "trigger 2"
            ],
            "summary": "Brief summary of what this business offers and its unique positioning"
        }}

        Focus on extracting concrete, actionable insights that can be used to find relevant discussions on social platforms.
        """

    async def get_gypsum_persona_context(self, org_id: str, persona_id: str) -> Dict[str, Any]:
        """Get persona context using VoiceForge's Gypsum personas"""
        try:
            # Handle None persona_id - use default business persona
            if not persona_id:
                self.logger.info('No persona_id provided, using default business persona')
                return {
                    'persona': self.get_fallback_persona(),
                    'context': {},
                    'retrieved_at': datetime.utcnow().isoformat()
                }
            
            # Import the static personas from our gypsum router
            from api.gypsum import STATIC_PERSONAS
            
            # Find the specific persona by ID
            selected_persona = None
            for persona in STATIC_PERSONAS:
                if persona['id'] == persona_id:
                    selected_persona = persona
                    break
            
            if selected_persona:
                self.logger.info(f'Retrieved persona: {selected_persona.get("role", "Unknown")} from VoiceForge Gypsum')
                return {
                    'persona': selected_persona,
                    'context': {},
                    'retrieved_at': datetime.utcnow().isoformat()
                }
            else:
                self.logger.warning(f'Persona {persona_id} not found in static personas')
                # Return first available persona as fallback
                if STATIC_PERSONAS:
                    self.logger.info(f'Using first available persona as fallback: {STATIC_PERSONAS[0].get("role", "Unknown")}')
                    return {
                        'persona': STATIC_PERSONAS[0],
                        'context': {},
                        'retrieved_at': datetime.utcnow().isoformat()
                    }
                
        except Exception as e:
            self.logger.error(f'Error accessing VoiceForge Gypsum personas: {str(e)}')
        
        # Ultimate fallback
        self.logger.warning('Using generic fallback persona')
        return {'persona': self.get_fallback_persona()}

    async def generate_unified_search_strategy(
        self, 
        content_analysis: Dict, 
        persona: Dict, 
        platforms: List[str], 
        options: Dict
    ) -> Dict[str, Any]:
        """Generate unified search strategy across all platforms"""

        # Use OpenAI for intelligent strategy generation
        strategy_prompt = f"""
        Create a unified signal discovery strategy based on this business analysis and target persona:

        BUSINESS ANALYSIS:
        - Value Propositions: {content_analysis.get('primary_value_propositions', [])}
        - Problems Addressed: {content_analysis.get('problems_addressed', [])}
        - Key Features: {content_analysis.get('key_features', [])}
        - Industry: {content_analysis.get('industry_positioning', {}).get('primary_industry', 'unknown')}

        TARGET PERSONA:
        - Role: {persona.get('role', 'unknown')}
        - Industry: {persona.get('industry', 'unknown')}
        - Pain Points: {persona.get('pain_points', [])}
        - Goals: {persona.get('goals', [])}
        - Company Size: {persona.get('company_size', 'unknown')}

        PLATFORMS: {platforms}

        Generate a JSON strategy with:
        {{
            "core_themes": [
                {{
                    "theme": "theme name",
                    "rationale": "why this theme is important",
                    "search_angles": ["angle 1", "angle 2"]
                }}
            ],
            "priority_problems": [
                {{
                    "problem": "specific problem",
                    "persona_relevance": "why this matters to the persona",
                    "search_patterns": ["pattern 1", "pattern 2"]
                }}
            ],
            "competitive_intelligence": [
                {{
                    "angle": "competitive angle",
                    "search_terms": ["term 1", "term 2"]
                }}
            ],
            "engagement_opportunities": [
                {{
                    "opportunity_type": "type",
                    "description": "what to look for",
                    "response_approach": "how to engage"
                }}
            ],
            "cross_platform_keywords": [
                {{
                    "keyword": "keyword",
                    "platforms": ["reddit", "linkedin"],
                    "search_context": "how to use this keyword"
                }}
            ]
        }}
        """

        try:
            response = await aclient.chat.completions.create(model="gpt-4",
            messages=[{"role": "user", "content": strategy_prompt}],
            temperature=0.3)

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            self.logger.error(f'Error generating unified strategy: {str(e)}')
            return self.get_enhanced_fallback_strategy(content_analysis, persona, platforms)

    async def create_platform_strategy(
        self, 
        platform: str, 
        unified_strategy: Dict, 
        content_analysis: Dict, 
        persona: Dict
    ) -> Dict[str, Any]:
        """Create platform-specific strategy"""

        if platform == 'reddit':
            return self.create_reddit_strategy(unified_strategy, content_analysis, persona)
        elif platform == 'linkedin':
            return self.create_linkedin_strategy(unified_strategy, content_analysis, persona)
        elif platform == 'github':
            return self.create_github_strategy(unified_strategy, content_analysis, persona)
        elif platform == 'twitter':
            return self.create_twitter_strategy(unified_strategy, content_analysis, persona)
        else:
            return self.create_generic_strategy(platform, unified_strategy, content_analysis, persona)

    def create_reddit_strategy(self, unified_strategy: Dict, content_analysis: Dict, persona: Dict) -> Dict:
        """Create Reddit-specific strategy"""

        # Generate subreddit recommendations
        subreddits = self.recommend_subreddits(content_analysis, persona)

        # Generate Reddit-specific search queries
        queries = []

        # Problem-based queries
        for problem in unified_strategy.get('priority_problems', []):
            queries.append({
                'query': f'"{problem["problem"]}" {persona.get("industry", "")}',
                'type': 'problem_discussion',
                'rationale': problem['persona_relevance'],
                'expected_results': 'Users experiencing this specific problem'
            })

        # Feature/solution queries
        for feature in content_analysis.get('key_features', [])[:5]:
            queries.append({
                'query': f'looking for {feature} {persona.get("role", "")}',
                'type': 'solution_seeking',
                'rationale': f'Find users seeking {feature} functionality',
                'expected_results': 'Feature requirement discussions'
            })

        # Competitive queries
        for comp in unified_strategy.get('competitive_intelligence', []):
            queries.append({
                'query': ' '.join(comp['search_terms']),
                'type': 'competitive_intelligence',
                'rationale': comp['angle'],
                'expected_results': 'Competitive discussions and comparisons'
            })

        return {
            'platform': 'reddit',
            'recommended_sources': subreddits,
            'search_queries': queries[:15],  # Limit to 15 queries
            'targeting_criteria': {
                'time_filter': 'week',
                'min_score': 5,
                'relevance_threshold': 0.7,
                'engagement_focus': ['questions', 'complaints', 'feature_requests']
            },
            'engagement_guidelines': {
                'response_style': 'helpful_expert',
                'mention_product': 'contextually_appropriate',
                'focus_on': 'solving_problems'
            }
        }

    def create_linkedin_strategy(self, unified_strategy: Dict, content_analysis: Dict, persona: Dict) -> Dict:
        """Create LinkedIn-specific strategy"""

        # LinkedIn sources: hashtags, companies, industry groups
        hashtags = self.recommend_linkedin_hashtags(content_analysis, persona)
        companies = self.recommend_linkedin_companies(persona)

        queries = []

        # Professional problem discussions
        for problem in unified_strategy.get('priority_problems', []):
            queries.append({
                'query': f'{persona.get("role", "")} challenges {problem["problem"]}',
                'type': 'professional_challenge',
                'rationale': f'Find {persona.get("role", "")} discussing this challenge',
                'expected_results': 'Professional discussions about business problems'
            })

        # Industry trend queries
        for theme in unified_strategy.get('core_themes', [])[:3]:
            queries.append({
                'query': f'{theme["theme"]} trends {persona.get("industry", "")}',
                'type': 'industry_trend',
                'rationale': theme['rationale'],
                'expected_results': 'Industry trend discussions'
            })

        return {
            'platform': 'linkedin',
            'recommended_sources': {
                'hashtags': hashtags,
                'companies': companies,
                'industry_groups': self.recommend_linkedin_groups(persona)
            },
            'search_queries': queries[:10],
            'targeting_criteria': {
                'time_filter': 'month',
                'min_engagement': 10,
                'relevance_threshold': 0.75,
                'focus_roles': [persona.get('role', '')],
                'focus_industries': [persona.get('industry', '')]
            },
            'engagement_guidelines': {
                'response_style': 'professional_thought_leader',
                'content_type': 'insights_and_solutions',
                'networking_focus': True
            }
        }

    def create_github_strategy(self, unified_strategy: Dict, content_analysis: Dict, persona: Dict) -> Dict:
        """Create GitHub-specific strategy"""

        # GitHub sources: repositories, organizations
        repos = self.recommend_github_repos(content_analysis, persona)

        queries = []

        # Technical problem queries
        for keyword in content_analysis.get('technical_keywords', [])[:5]:
            queries.append({
                'query': f'{keyword} issues problems',
                'type': 'technical_issue',
                'rationale': f'Find developers struggling with {keyword}',
                'expected_results': 'GitHub issues and discussions'
            })

        # Feature request queries
        for feature in content_analysis.get('key_features', [])[:3]:
            queries.append({
                'query': f'feature request {feature}',
                'type': 'feature_request',
                'rationale': f'Find requests for {feature} functionality',
                'expected_results': 'Feature request issues and discussions'
            })

        return {
            'platform': 'github',
            'recommended_sources': {
                'repositories': repos,
                'organizations': self.recommend_github_orgs(persona),
                'topics': content_analysis.get('technical_keywords', [])[:10]
            },
            'search_queries': queries[:8],
            'targeting_criteria': {
                'time_filter': 'month',
                'issue_types': ['bug', 'feature', 'question'],
                'relevance_threshold': 0.8
            },
            'engagement_guidelines': {
                'response_style': 'technical_helpful',
                'contribution_type': 'solutions_and_code',
                'open_source_focus': True
            }
        }

    def create_twitter_strategy(self, unified_strategy: Dict, content_analysis: Dict, persona: Dict) -> Dict:
        """Create Twitter-specific strategy"""

        hashtags = self.recommend_twitter_hashtags(content_analysis, persona)
        users = self.recommend_twitter_users(persona)

        queries = []

        # Real-time problem discussions
        for problem in unified_strategy.get('priority_problems', [])[:3]:
            queries.append({
                'query': f'{problem["problem"]} {persona.get("industry", "")}',
                'type': 'realtime_problem',
                'rationale': problem['persona_relevance'],
                'expected_results': 'Real-time problem discussions'
            })

        # Trend monitoring
        for theme in unified_strategy.get('core_themes', [])[:3]:
            queries.append({
                'query': theme['theme'],
                'type': 'trend_monitoring',
                'rationale': theme['rationale'],
                'expected_results': 'Trending discussions'
            })

        return {
            'platform': 'twitter',
            'recommended_sources': {
                'hashtags': hashtags,
                'users': users,
                'lists': self.recommend_twitter_lists(persona)
            },
            'search_queries': queries[:12],
            'targeting_criteria': {
                'time_filter': 'day',
                'min_engagement': 5,
                'relevance_threshold': 0.65,
                'real_time_focus': True
            },
            'engagement_guidelines': {
                'response_style': 'concise_helpful',
                'character_limit': 280,
                'hashtag_usage': True
            }
        }

    def create_execution_plan(self, platform_strategies: Dict) -> Dict:
        """Create execution plan across all platforms"""

        total_queries = sum(len(strategy['search_queries']) for strategy in platform_strategies.values())
        total_sources = sum(
            len(strategy.get('recommended_sources', [])) if isinstance(strategy.get('recommended_sources'), list)
            else sum(len(sources) if isinstance(sources, list) else 1 
                    for sources in strategy.get('recommended_sources', {}).values() 
                    if isinstance(strategy.get('recommended_sources'), dict))
            for strategy in platform_strategies.values()
        )

        return {
            'total_platforms': len(platform_strategies),
            'total_queries': total_queries,
            'total_sources': total_sources,
            'estimated_signals_per_day': total_queries * 3,  # Rough estimate

            'execution_phases': [
                {
                    'phase': 'Problem Discovery',
                    'priority': 'high',
                    'platforms': list(platform_strategies.keys()),
                    'query_types': ['problem_discussion', 'technical_issue', 'professional_challenge'],
                    'estimated_duration': '30 minutes'
                },
                {
                    'phase': 'Solution Seeking',
                    'priority': 'medium',
                    'platforms': list(platform_strategies.keys()),
                    'query_types': ['solution_seeking', 'feature_request'],
                    'estimated_duration': '20 minutes'
                },
                {
                    'phase': 'Competitive Intelligence',
                    'priority': 'low',
                    'platforms': ['reddit', 'linkedin', 'twitter'],
                    'query_types': ['competitive_intelligence', 'trend_monitoring'],
                    'estimated_duration': '15 minutes'
                }
            ],

            'recommended_schedule': {
                'scan_frequency': 'every_6_hours',
                'peak_hours': ['9am', '1pm', '5pm'],
                'platform_priority': ['reddit', 'linkedin', 'github', 'twitter']
            },

            'success_metrics': {
                'target_signals_per_day': total_queries * 2,
                'min_relevance_score': 0.7,
                'target_engagement_rate': 0.15,
                'response_time_target': '2 hours'
            }
        }

    # Helper methods for platform-specific recommendations
    def recommend_subreddits(self, content_analysis: Dict, persona: Dict) -> List[Dict]:
        """Recommend relevant subreddits based on content analysis + persona"""
        subreddits = []
        
        # PRIORITY 1: Content-driven subreddit recommendations
        technical_keywords = content_analysis.get('technical_keywords', [])
        key_features = content_analysis.get('key_features', [])
        problems_addressed = content_analysis.get('problems_addressed', [])
        industry_category = content_analysis.get('industry_positioning', {}).get('market_category', '')
        primary_industry = content_analysis.get('industry_positioning', {}).get('primary_industry', '')
        
        self.logger.info(f'📊 Content-driven subreddit discovery:')
        self.logger.info(f'   Technical keywords: {technical_keywords}')
        self.logger.info(f'   Key features: {key_features}')
        self.logger.info(f'   Problems addressed: {problems_addressed}')
        self.logger.info(f'   Industry: {primary_industry} / {industry_category}')
        
        # Technical keyword mapping (content-driven)
        technical_subreddit_mapping = {
            # Security & Code Signing
            'security': ['netsec', 'cybersecurity', 'InfoSecCareers', 'AskNetsec'],
            'code signing': ['programming', 'devops', 'sysadmin', 'golang'],
            'certificate': ['sysadmin', 'devops', 'cybersecurity', 'ITCareerQuestions'],
            'authentication': ['cybersecurity', 'programming', 'webdev', 'devops'],
            'encryption': ['crypto', 'cybersecurity', 'netsec', 'privacy'],
            'pki': ['sysadmin', 'cybersecurity', 'networking', 'ITCareerQuestions'],
            
            # Development & APIs
            'api': ['webdev', 'programming', 'node', 'golang', 'restapi'],
            'microservice': ['programming', 'devops', 'golang', 'kubernetes', 'docker'],
            'integration': ['programming', 'webdev', 'devops', 'sysadmin'],
            'webhook': ['webdev', 'programming', 'node', 'apis'],
            'sdk': ['programming', 'gamedev', 'webdev', 'mobiledev'],
            'golang': ['golang', 'programming', 'backend', 'devops'],
            'grpc': ['golang', 'programming', 'grpc', 'microservices'],
            
            # DevOps & Infrastructure  
            'ci/cd': ['devops', 'programming', 'docker', 'kubernetes'],
            'docker': ['docker', 'devops', 'selfhosted', 'homelab'],
            'kubernetes': ['kubernetes', 'devops', 'docker', 'sysadmin'],
            'automation': ['devops', 'sysadmin', 'programming', 'Python'],
            'pipeline': ['devops', 'programming', 'cicd', 'gitlab'],
            'deployment': ['devops', 'programming', 'sysadmin', 'webdev'],
            
            # General Tech
            'javascript': ['javascript', 'webdev', 'node', 'react'],
            'python': ['Python', 'programming', 'MachineLearning', 'webdev'],
            'java': ['java', 'programming', 'spring', 'androiddev'],
            'dotnet': ['dotnet', 'csharp', 'programming', 'webdev'],
            'cloud': ['aws', 'azure', 'googlecloud', 'devops']
        }
        
        # Map technical keywords to subreddits
        for keyword in technical_keywords:
            keyword_lower = keyword.lower()
            for tech_term, subs in technical_subreddit_mapping.items():
                if tech_term in keyword_lower or keyword_lower in tech_term:
                    for sub in subs[:2]:  # Limit to 2 per keyword
                        subreddits.append({
                            'name': sub,
                            'reasoning': f'Matches technical keyword "{keyword}" from your content analysis',
                            'confidence': 0.9,
                            'priority': 'high'
                        })
                    break
        
        # Map features to subreddits
        feature_subreddit_mapping = {
            'signing': ['programming', 'devops', 'cybersecurity'],
            'certificate': ['sysadmin', 'cybersecurity', 'devops'],
            'validation': ['programming', 'webdev', 'testing'],
            'compliance': ['cybersecurity', 'ITCareerQuestions', 'compliance'],
            'audit': ['cybersecurity', 'ITCareerQuestions', 'sysadmin']
        }
        
        for feature in key_features:
            feature_lower = feature.lower()
            for feature_term, subs in feature_subreddit_mapping.items():
                if feature_term in feature_lower:
                    for sub in subs[:2]:  # Limit to 2 per feature
                        subreddits.append({
                            'name': sub,
                            'reasoning': f'Supports feature "{feature}" identified in your content',
                            'confidence': 0.85,
                            'priority': 'high'
                        })
                    break
        
        # Map problems to subreddits
        problem_subreddit_mapping = {
            'manual': ['automation', 'devops', 'sysadmin', 'programming'],
            'integration': ['webdev', 'programming', 'devops', 'apis'],
            'security': ['cybersecurity', 'netsec', 'privacy'],
            'process': ['devops', 'sysadmin', 'programming'],
            'deployment': ['devops', 'docker', 'kubernetes']
        }
        
        for problem in problems_addressed:
            problem_lower = problem.lower()
            for problem_term, subs in problem_subreddit_mapping.items():
                if problem_term in problem_lower:
                    for sub in subs[:2]:  # Limit to 2 per problem
                        subreddits.append({
                            'name': sub,
                            'reasoning': f'Addresses problem "{problem}" from your content analysis',
                            'confidence': 0.8,
                            'priority': 'medium'
                        })
                    break
        
        # PRIORITY 2: Persona-driven additions (only if we have good content matches)
        persona_role = persona.get('role', '').lower()
        persona_industry = persona.get('industry', '').lower()
        
        if 'developer' in persona_role or 'engineer' in persona_role:
            subreddits.extend([
                {
                    'name': 'programming',
                    'reasoning': f'Relevant to {persona.get("role", "developer")} role',
                    'confidence': 0.7,
                    'priority': 'medium'
                },
                {
                    'name': 'devops',
                    'reasoning': f'Technical community for {persona.get("role", "developer")}',
                    'confidence': 0.7,
                    'priority': 'medium'
                }
            ])
        
        # PRIORITY 3: Industry-specific (only add if we don't have enough content-driven ones)
        if len(subreddits) < 5:
            industry_mapping = {
                'technology': ['technology', 'programming', 'startups'],
                'security': ['cybersecurity', 'netsec', 'privacy'],
                'saas': ['SaaS', 'startups', 'entrepreneur']
            }
            
            industry_subs = industry_mapping.get(primary_industry.lower(), 
                                               industry_mapping.get(persona_industry, []))
            
            for sub in industry_subs[:3]:
                subreddits.append({
                    'name': sub,
                    'reasoning': f'Relevant to {primary_industry or persona_industry} industry',
                    'confidence': 0.6,
                    'priority': 'low'
                })
        
        # LAST RESORT: Only add generic business subs if we have very few matches
        if len(subreddits) < 3:
            self.logger.warning('⚠️ Very few content-driven subreddits found, adding minimal generic ones')
            generic_subs = ['programming', 'devops', 'startups']
            for sub in generic_subs:
                subreddits.append({
                    'name': sub,
                    'reasoning': 'Fallback recommendation - content analysis may need more data',
                    'confidence': 0.4,
                    'priority': 'low'
                })
        
        # Remove duplicates while preserving order and priority
        seen = set()
        unique_subreddits = []
        
        # Sort by priority and confidence first
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        subreddits.sort(key=lambda x: (priority_order.get(x.get('priority', 'low'), 1), x.get('confidence', 0)), reverse=True)
        
        for sub in subreddits:
            if sub['name'] not in seen:
                seen.add(sub['name'])
                unique_subreddits.append(sub)
        
        result = unique_subreddits[:10]  # Limit to top 10
        
        self.logger.info(f'🎯 Final subreddit recommendations: {[s["name"] for s in result]}')
        self.logger.info(f'   High priority: {[s["name"] for s in result if s.get("priority") == "high"]}')
        self.logger.info(f'   Content-driven: {len([s for s in result if s.get("confidence", 0) > 0.7])}/{len(result)}')
        
        return result

    def recommend_linkedin_hashtags(self, content_analysis: Dict, persona: Dict) -> List[str]:
        """Recommend LinkedIn hashtags"""
        industry = persona.get('industry', '')

        hashtags = [
            f"#{industry.replace(' ', '')}",
            f"#{persona.get('role', '').replace(' ', '')}",
            '#innovation',
            '#technology',
            '#business',
            '#productivity'
        ]

        # Add feature-based hashtags
        for feature in content_analysis.get('key_features', [])[:3]:
            if feature:
                hashtag = f"#{feature.replace(' ', '').replace('-', '')}"
                hashtags.append(hashtag)

        return [h for h in hashtags if h != '#'][:10]

    def recommend_linkedin_companies(self, persona: Dict) -> List[str]:
        """Recommend LinkedIn companies to monitor"""
        industry = persona.get('industry', '').lower()

        # Industry leaders
        company_mapping = {
            'technology': ['Microsoft', 'Google', 'Apple', 'Amazon'],
            'saas': ['Salesforce', 'HubSpot', 'Slack', 'Zoom'],
            'fintech': ['PayPal', 'Stripe', 'Square', 'Robinhood'],
            'healthcare': ['Teladoc', 'Veracyte', 'Epic Systems']
        }

        return company_mapping.get(industry, ['Microsoft', 'Google', 'Amazon'])[:5]

    def recommend_linkedin_groups(self, persona: Dict) -> List[str]:
        """Recommend LinkedIn groups"""
        return [
            f"{persona.get('industry', 'Business')} Professionals",
            f"{persona.get('role', 'Business')} Network",
            "Startup Founders",
            "Tech Professionals"
        ]

    def recommend_github_repos(self, content_analysis: Dict, persona: Dict) -> List[str]:
        """Recommend GitHub repositories"""
        keywords = content_analysis.get('technical_keywords', [])

        # Popular repos by keyword
        repo_mapping = {
            'api': ['public-apis/public-apis', 'postmanlabs/newman'],
            'javascript': ['microsoft/vscode', 'facebook/react'],
            'python': ['python/cpython', 'django/django'],
            'automation': ['ansible/ansible', 'puppetlabs/puppet'],
            'ai': ['openai/openai-python', 'huggingface/transformers']
        }

        repos = []
        for keyword in keywords[:3]:
            if keyword.lower() in repo_mapping:
                repos.extend(repo_mapping[keyword.lower()])

        # Add generic popular repos
        generic_repos = ['microsoft/vscode', 'facebook/react', 'tensorflow/tensorflow']
        repos.extend(generic_repos)

        return list(set(repos))[:8]

    def recommend_github_orgs(self, persona: Dict) -> List[str]:
        """Recommend GitHub organizations"""
        industry = persona.get('industry', '').lower()

        org_mapping = {
            'technology': ['microsoft', 'google', 'facebook'],
            'saas': ['salesforce', 'atlassian', 'shopify'],
            'fintech': ['stripe', 'square', 'paypal']
        }

        return org_mapping.get(industry, ['microsoft', 'google', 'facebook'])[:5]

    def recommend_twitter_hashtags(self, content_analysis: Dict, persona: Dict) -> List[str]:
        """Recommend Twitter hashtags"""
        industry = persona.get('industry', '')

        hashtags = [
            f"#{industry.replace(' ', '')}",
            f"#{persona.get('role', '').replace(' ', '')}",
            '#startup',
            '#tech',
            '#business',
            '#innovation'
        ]

        return [h for h in hashtags if h != '#'][:8]

    def recommend_twitter_users(self, persona: Dict) -> List[str]:
        """Recommend Twitter users to monitor"""
        # Industry thought leaders
        return [
            '@paulg',  # Y Combinator
            '@naval',  # AngelList
            '@dhh',    # Basecamp
            '@jasonfried'  # Basecamp
        ][:5]

    def recommend_twitter_lists(self, persona: Dict) -> List[str]:
        """Recommend Twitter lists"""
        return [
            'Tech Leaders',
            'Startup Founders',
            f'{persona.get("industry", "Business")} Experts'
        ]

    def create_generic_strategy(self, platform: str, unified_strategy: Dict, content_analysis: Dict, persona: Dict) -> Dict:
        """Create generic strategy for unsupported platforms"""
        return {
            'platform': platform,
            'status': 'not_implemented',
            'message': f'Strategy generation for {platform} is not yet implemented',
            'fallback_keywords': content_analysis.get('technical_keywords', [])[:10]
        }

    # Fallback methods
    def get_fallback_content_analysis(self) -> Dict:
        """Fallback content analysis when VoiceForge content is unavailable"""
        self.logger.info('🔄 Using enhanced fallback content analysis for SignPath-style business')
        return {
            'primary_value_propositions': [
                'Secure code signing and artifact verification',
                'Automated certificate management',
                'Compliance and audit trail capabilities',
                'Streamlined CI/CD integration'
            ],
            'key_features': [
                'Code signing certificates',
                'Artifact signing and verification', 
                'Certificate lifecycle management',
                'API integration',
                'Compliance reporting',
                'HSM integration',
                'CI/CD pipeline support'
            ],
            'target_use_cases': [
                'Secure software distribution',
                'Compliance requirements (SOX, GDPR)',
                'CI/CD security automation',
                'Certificate management',
                'Software supply chain security'
            ],
            'problems_addressed': [
                'Manual code signing processes',
                'Certificate management complexity',
                'Compliance audit requirements',
                'Insecure software distribution',
                'Supply chain security vulnerabilities'
            ],
            'competitive_advantages': [
                'Automated certificate management',
                'Enterprise-grade security',
                'Seamless CI/CD integration',
                'Comprehensive audit trails'
            ],
            'industry_positioning': {
                'primary_industry': 'Cybersecurity',
                'secondary_industries': ['Software Development', 'DevOps', 'Enterprise IT'],
                'market_category': 'Code Signing and PKI Management'
            },
            'messaging_themes': [
                'Security automation',
                'Developer productivity',
                'Compliance simplification',
                'Trust and verification'
            ],
            'customer_pain_points': [
                'Complex certificate management',
                'Manual signing processes',
                'Compliance burden',
                'Security vulnerabilities in CI/CD',
                'Lack of audit visibility'
            ],
            'solution_benefits': [
                'Automated secure signing',
                'Simplified compliance',
                'Enhanced security posture',
                'Developer workflow integration',
                'Comprehensive audit trails'
            ],
            'technical_keywords': [
                'code signing',
                'PKI',
                'certificates',
                'HSM',
                'API integration',
                'CI/CD automation',
                'security',
                'compliance',
                'artifact verification',
                'digital signatures'
            ],
            'emotional_triggers': [
                'Security confidence',
                'Compliance peace of mind',
                'Developer efficiency',
                'Trust and reliability'
            ],
            'summary': 'Code signing and PKI management platform that automates secure software distribution and simplifies compliance for development teams',
            'fallback': True
        }

    def get_fallback_persona(self) -> Dict:
        """Fallback persona when Gypsum is unavailable"""
        return {
            'role': 'Business Manager',
            'industry': 'Technology',
            'pain_points': ['Manual processes', 'Data integration'],
            'goals': ['Increase efficiency', 'Reduce costs'],
            'company_size': 'SMB',
            'fallback': True
        }

    def get_enhanced_fallback_strategy(self, content_analysis: Dict, persona: Dict, platforms: List[str]) -> Dict:
        """Enhanced fallback strategy that uses persona data intelligently"""
        
        persona_role = persona.get('role', 'Business Manager').lower()
        persona_industry = persona.get('industry', 'Technology').lower()
        persona_pain_points = persona.get('pain_points', [])
        
        # Build themes based on persona
        core_themes = []
        if 'developer' in persona_role or 'engineer' in persona_role:
            core_themes.extend([
                {
                    'theme': 'API Integration Challenges',
                    'rationale': 'Developers frequently discuss API integration difficulties',
                    'search_angles': ['api integration problems', 'microservice communication']
                },
                {
                    'theme': 'Developer Tooling',
                    'rationale': 'Tool efficiency is crucial for developers',
                    'search_angles': ['developer tools', 'code generation', 'automation']
                }
            ])
        
        if 'manager' in persona_role or 'director' in persona_role:
            core_themes.extend([
                {
                    'theme': 'Team Productivity',
                    'rationale': 'Managers focus on team efficiency and productivity',
                    'search_angles': ['team productivity tools', 'workflow optimization']
                },
                {
                    'theme': 'Process Automation',
                    'rationale': 'Managers seek to automate repetitive processes',
                    'search_angles': ['business process automation', 'workflow automation']
                }
            ])
        
        # Build priority problems from persona pain points
        priority_problems = []
        for pain_point in persona_pain_points[:3]:
            priority_problems.append({
                'problem': pain_point,
                'persona_relevance': f'This directly impacts {persona_role} productivity',
                'search_patterns': [pain_point.lower(), f'{pain_point} solutions']
            })
        
        # Add generic problems if no pain points
        if not priority_problems:
            priority_problems = [
                {
                    'problem': 'Manual processes taking too much time',
                    'persona_relevance': 'Time efficiency is crucial for business success',
                    'search_patterns': ['manual processes', 'automation solutions']
                },
                {
                    'problem': 'Data integration challenges',
                    'persona_relevance': 'Data silos prevent informed decision making',
                    'search_patterns': ['data integration', 'api connectivity']
                }
            ]
        
        # Build competitive intelligence based on industry
        competitive_intelligence = []
        if 'technology' in persona_industry or 'saas' in persona_industry:
            competitive_intelligence.extend([
                {
                    'angle': 'Developer tool alternatives',
                    'search_terms': ['developer tools comparison', 'api tools review']
                },
                {
                    'angle': 'Integration platform comparison',
                    'search_terms': ['integration platforms', 'api management tools']
                }
            ])
        
        # Build engagement opportunities
        engagement_opportunities = [
            {
                'opportunity_type': 'Problem Solving',
                'description': 'Users asking for help with technical challenges',
                'response_approach': 'Provide helpful solutions and mention relevant features'
            },
            {
                'opportunity_type': 'Tool Recommendations', 
                'description': 'Users seeking tool recommendations',
                'response_approach': 'Share experience and suggest appropriate solutions'
            },
            {
                'opportunity_type': 'Best Practices',
                'description': 'Discussions about industry best practices',
                'response_approach': 'Share insights and thought leadership'
            }
        ]
        
        # Build cross-platform keywords
        cross_platform_keywords = [
            {
                'keyword': 'api integration',
                'platforms': platforms,
                'search_context': 'Discussions about connecting different systems'
            },
            {
                'keyword': 'workflow automation',
                'platforms': platforms,
                'search_context': 'Process improvement and automation discussions'
            },
            {
                'keyword': 'developer tools',
                'platforms': platforms,
                'search_context': 'Tool recommendations and comparisons'
            }
        ]
        
        # Add persona-specific keywords
        if 'developer' in persona_role:
            cross_platform_keywords.extend([
                {
                    'keyword': 'code generation',
                    'platforms': platforms,
                    'search_context': 'Automated code generation discussions'
                },
                {
                    'keyword': 'microservices',
                    'platforms': platforms,
                    'search_context': 'Microservice architecture discussions'
                }
            ])
        
        return {
            'core_themes': core_themes,
            'priority_problems': priority_problems,
            'competitive_intelligence': competitive_intelligence,
            'engagement_opportunities': engagement_opportunities,
            'cross_platform_keywords': cross_platform_keywords,
            'strategy_confidence': 0.7,  # Lower confidence for fallback
            'fallback_mode': True,
            'persona_driven': True
        }

    def get_fallback_strategy(self) -> Dict:
        """Fallback strategy when AI generation fails"""
        return {
            'core_themes': [
                {
                    'theme': 'Workflow Automation',
                    'rationale': 'Common business need',
                    'search_angles': ['automation tools', 'workflow optimization']
                }
            ],
            'priority_problems': [
                {
                    'problem': 'Manual data entry',
                    'persona_relevance': 'Time-consuming for business users',
                    'search_patterns': ['data entry automation', 'manual process problems']
                }
            ],
            'cross_platform_keywords': [
                {
                    'keyword': 'automation',
                    'platforms': ['reddit', 'linkedin'],
                    'search_context': 'General business automation discussions'
                }
            ],
            'fallback': True
        }

    def extract_raw_insights(self, content_samples: List[Dict]) -> Dict:
        """Extract raw insights from content samples using simple text analysis"""
        insights = {
            'common_words': {},
            'content_types': set(),
            'domains': set(),
            'total_words': 0
        }

        for sample in content_samples:
            # Count content types
            content_type = sample.get('content_type', 'unknown')
            insights['content_types'].add(content_type)

            # Count domains
            domain = sample.get('domain', 'unknown')
            insights['domains'].add(domain)

            # Count words
            text = sample.get('text') or sample.get('content') or ''
            words = text.lower().split()
            insights['total_words'] += len(words)

            # Count common words
            for word in words:
                if len(word) > 4:  # Skip short words
                    insights['common_words'][word] = insights['common_words'].get(word, 0) + 1

        # Convert sets to lists for JSON serialization
        insights['content_types'] = list(insights['content_types'])
        insights['domains'] = list(insights['domains'])

        # Keep top 20 most common words
        insights['common_words'] = dict(
            sorted(insights['common_words'].items(), key=lambda x: x[1], reverse=True)[:20]
        )

        return insights

    def get_content_types(self, content_samples: List[Dict]) -> List[str]:
        """Get unique content types from samples"""
        types = set()
        for sample in content_samples:
            content_type = sample.get('content_type', 'unknown')
            types.add(content_type)
        return list(types)

    def get_enhanced_fallback_strategy(self, content_analysis: Dict, persona: Dict, platforms: List[str]) -> Dict:
        """Enhanced fallback strategy that uses persona data intelligently"""
        
        persona_role = persona.get('role', 'Business Manager').lower()
        persona_industry = persona.get('industry', 'Technology').lower()
        persona_pain_points = persona.get('pain_points', [])
        
        # Build themes based on persona
        core_themes = []
        if 'developer' in persona_role or 'engineer' in persona_role:
            core_themes.extend([
                {
                    'theme': 'API Integration Challenges',
                    'rationale': 'Developers frequently discuss API integration difficulties',
                    'search_angles': ['api integration problems', 'microservice communication']
                },
                {
                    'theme': 'Developer Tooling',
                    'rationale': 'Tool efficiency is crucial for developers',
                    'search_angles': ['developer tools', 'code generation', 'automation']
                }
            ])
        
        if 'manager' in persona_role or 'director' in persona_role:
            core_themes.extend([
                {
                    'theme': 'Team Productivity',
                    'rationale': 'Managers focus on team efficiency and productivity',
                    'search_angles': ['team productivity tools', 'workflow optimization']
                },
                {
                    'theme': 'Process Automation',
                    'rationale': 'Managers seek to automate repetitive processes',
                    'search_angles': ['business process automation', 'workflow automation']
                }
            ])
        
        # Build priority problems from persona pain points
        priority_problems = []
        for pain_point in persona_pain_points[:3]:
            priority_problems.append({
                'problem': pain_point,
                'persona_relevance': f'This directly impacts {persona_role} productivity',
                'search_patterns': [pain_point.lower(), f'{pain_point} solutions']
            })
        
        # Add generic problems if no pain points
        if not priority_problems:
            priority_problems = [
                {
                    'problem': 'Manual processes taking too much time',
                    'persona_relevance': 'Time efficiency is crucial for business success',
                    'search_patterns': ['manual processes', 'automation solutions']
                },
                {
                    'problem': 'Data integration challenges',
                    'persona_relevance': 'Data silos prevent informed decision making',
                    'search_patterns': ['data integration', 'api connectivity']
                }
            ]
        
        # Build competitive intelligence based on industry
        competitive_intelligence = []
        if 'technology' in persona_industry or 'saas' in persona_industry:
            competitive_intelligence.extend([
                {
                    'angle': 'Developer tool alternatives',
                    'search_terms': ['developer tools comparison', 'api tools review']
                },
                {
                    'angle': 'Integration platform comparison',
                    'search_terms': ['integration platforms', 'api management tools']
                }
            ])
        
        # Build engagement opportunities
        engagement_opportunities = [
            {
                'opportunity_type': 'Problem Solving',
                'description': 'Users asking for help with technical challenges',
                'response_approach': 'Provide helpful solutions and mention relevant features'
            },
            {
                'opportunity_type': 'Tool Recommendations', 
                'description': 'Users seeking tool recommendations',
                'response_approach': 'Share experience and suggest appropriate solutions'
            },
            {
                'opportunity_type': 'Best Practices',
                'description': 'Discussions about industry best practices',
                'response_approach': 'Share insights and thought leadership'
            }
        ]
        
        # Build cross-platform keywords
        cross_platform_keywords = [
            {
                'keyword': 'api integration',
                'platforms': platforms,
                'search_context': 'Discussions about connecting different systems'
            },
            {
                'keyword': 'workflow automation',
                'platforms': platforms,
                'search_context': 'Process improvement and automation discussions'
            },
            {
                'keyword': 'developer tools',
                'platforms': platforms,
                'search_context': 'Tool recommendations and comparisons'
            }
        ]
        
        # Add persona-specific keywords
        if 'developer' in persona_role:
            cross_platform_keywords.extend([
                {
                    'keyword': 'code generation',
                    'platforms': platforms,
                    'search_context': 'Automated code generation discussions'
                },
                {
                    'keyword': 'microservices',
                    'platforms': platforms,
                    'search_context': 'Microservice architecture discussions'
                }
            ])
        
        return {
            'core_themes': core_themes,
            'priority_problems': priority_problems,
            'competitive_intelligence': competitive_intelligence,
            'engagement_opportunities': engagement_opportunities,
            'cross_platform_keywords': cross_platform_keywords,
            'strategy_confidence': 0.7,  # Lower confidence for fallback
            'fallback_mode': True,
            'persona_driven': True
        }
