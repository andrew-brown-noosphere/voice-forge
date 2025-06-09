import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from openai import OpenAI
from .content_driven_ai import ContentDrivenSignalAI

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class SignalIntelligenceService:
    def __init__(self, voiceforge_db=None, gypsum_client=None):
        self.content_ai = ContentDrivenSignalAI(voiceforge_db, gypsum_client)

    async def analyze_business_and_setup_sources(
        self, 
        business_description: str,
        target_audience: str,
        goals: List[str],
        platform: str = 'reddit'
    ) -> Dict[str, Any]:
        """AI-powered initial setup recommendations (legacy method)"""

        prompt = f"""
        Analyze this business and recommend a {platform} signal monitoring strategy:
        
        Business: {business_description}
        Target Audience: {target_audience}
        Goals: {', '.join(goals)}
        
        Provide specific recommendations for {platform}:
        1. 5-8 most relevant sources to monitor (subreddits for Reddit)
        2. 10-15 strategic keywords including variations
        3. Optimal scanning frequency
        4. Expected signal types to focus on
        
        Return JSON format:
        {{
            "recommended_sources": [
                {{"name": "source_name", "reasoning": "why relevant", "confidence": 0.85}}
            ],
            "recommended_keywords": [
                {{"keyword": "keyword", "reasoning": "why effective", "confidence": 0.90}}
            ],
            "suggested_frequency": "daily",
            "priority_signal_types": ["question", "complaint"],
            "strategy_notes": "Overall strategy explanation"
        }}
        """

        try:
            response = client.chat.completions.create(model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3)

            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {
                "recommended_sources": [],
                "recommended_keywords": [],
                "suggested_frequency": "daily",
                "priority_signal_types": ["question", "complaint"],
                "strategy_notes": f"AI analysis failed: {e}"
            }

    async def generate_content_driven_multi_platform_strategy(
        self,
        org_id: str,
        persona_id: Optional[str] = None,
        platforms: List[str] = ['reddit', 'linkedin', 'github', 'twitter'],
        options: Dict[str, Any] = {}
    ) -> Dict[str, Any]:
        """Generate content-driven signal discovery strategy across multiple platforms"""

        try:
            return await self.content_ai.generate_content_driven_searches(
                org_id=org_id,
                selected_persona_id=persona_id,  # Can be None
                platforms=platforms,
                options=options
            )
        except Exception as e:
            return {
                "error": f"Content-driven strategy generation failed: {str(e)}",
                "fallback": True,
                "platforms": platforms,
                "message": "Using fallback strategy generation"
            }

    async def validate_strategy_requirements(
        self,
        org_id: str,
        persona_id: str,
        platforms: List[str]
    ) -> Dict[str, Any]:
        """Validate that all requirements are met for content-driven strategy generation"""

        validation_result = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'recommendations': []
        }

        # Check VoiceForge content availability
        try:
            content_summary = await self.get_content_analysis_summary(org_id)
            if not content_summary['has_content']:
                validation_result['warnings'].append(
                    'No VoiceForge content found - using fallback product analysis'
                )
                validation_result['recommendations'].append(
                    'Add content to VoiceForge for more accurate signal targeting'
                )
        except Exception as e:
            validation_result['warnings'].append(f'Could not analyze VoiceForge content: {str(e)}')

        # Check Gypsum persona availability
        try:
            persona_context = await self.content_ai.get_gypsum_persona_context(org_id, persona_id)
            if not persona_context.get('persona') or persona_context.get('persona', {}).get('fallback'):
                validation_result['warnings'].append(
                    'Persona not found in Gypsum - using fallback persona'
                )
                validation_result['recommendations'].append(
                    'Configure target personas in Gypsum for better targeting'
                )
        except Exception as e:
            validation_result['warnings'].append(f'Could not fetch Gypsum persona: {str(e)}')

        # Check platform support
        supported_platforms = ['reddit', 'linkedin', 'github', 'twitter']
        unsupported = [p for p in platforms if p not in supported_platforms]
        if unsupported:
            validation_result['errors'].append(
                f'Unsupported platforms: {unsupported}. Supported: {supported_platforms}'
            )
            validation_result['valid'] = False

        # Check for active platforms
        active_platforms = ['reddit']  # Only Reddit is currently active
        inactive_requested = [p for p in platforms if p not in active_platforms]
        if inactive_requested:
            validation_result['warnings'].append(
                f'Platforms not yet active: {inactive_requested}. Only Reddit is currently active.'
            )

        return validation_result

    async def preview_content_driven_strategy(
        self,
        org_id: str,
        persona_id: str,
        platform: str
    ) -> Dict[str, Any]:
        """Preview content-driven strategy for a specific platform"""
        try:
            full_strategy = await self.content_ai.generate_content_driven_searches(
                org_id=org_id,
                selected_persona_id=persona_id,
                platforms=[platform]
            )

            platform_strategy = full_strategy.get('platform_strategies', {}).get(platform, {})

            return {
                'platform': platform,
                'preview': {
                    'recommended_sources': platform_strategy.get('recommended_sources', [])[:5],
                    'sample_queries': platform_strategy.get('search_queries', [])[:3],
                    'targeting_criteria': platform_strategy.get('targeting_criteria', {}),
                    'engagement_guidelines': platform_strategy.get('engagement_guidelines', {})
                },
                'content_insights': {
                    'value_props': full_strategy.get('content_analysis', {}).get('primary_value_propositions', [])[:2],
                    'key_problems': full_strategy.get('content_analysis', {}).get('problems_addressed', [])[:2]
                },
                'persona_match': {
                    'role': full_strategy.get('selected_persona', {}).get('role', 'Unknown'),
                    'industry': full_strategy.get('selected_persona', {}).get('industry', 'Unknown'),
                    'pain_points': full_strategy.get('selected_persona', {}).get('pain_points', [])[:2]
                }
            }
        except Exception as e:
            return {
                'platform': platform,
                'error': f'Strategy preview failed: {str(e)}',
                'fallback': True
            }

    def get_platform_capabilities(self) -> Dict[str, Any]:
        """Get capabilities and status of each platform"""
        return {
            'platforms': {
                'reddit': {
                    'status': 'active',
                    'capabilities': ['subreddit_monitoring', 'keyword_search', 'comment_analysis'],
                    'source_types': ['subreddit'],
                    'signal_types': ['question', 'complaint', 'feature_request', 'competitive_mention'],
                    'content_driven': True
                },
                'linkedin': {
                    'status': 'coming_soon',
                    'capabilities': ['hashtag_monitoring', 'company_monitoring', 'post_analysis'],
                    'source_types': ['hashtag', 'company', 'group'],
                    'signal_types': ['professional_challenge', 'industry_trend', 'thought_leadership'],
                    'content_driven': True
                },
                'github': {
                    'status': 'coming_soon',
                    'capabilities': ['repo_monitoring', 'issue_tracking', 'pr_analysis'],
                    'source_types': ['repository', 'organization', 'topic'],
                    'signal_types': ['technical_issue', 'feature_request', 'bug_report'],
                    'content_driven': True
                },
                'twitter': {
                    'status': 'coming_soon',
                    'capabilities': ['hashtag_monitoring', 'user_monitoring', 'trend_analysis'],
                    'source_types': ['hashtag', 'user', 'list'],
                    'signal_types': ['realtime_problem', 'trend_monitoring', 'brand_mention'],
                    'content_driven': True
                }
            },
            'content_driven_features': {
                'voiceforge_integration': True,
                'gypsum_personas': True,
                'multi_platform_strategy': True,
                'automated_optimization': True
            }
        }

    async def analyze_and_recommend_optimizations(
        self, 
        source: 'SignalSource', 
        recent_signals: List['Signal']
    ) -> List[Dict[str, Any]]:
        """Analyze source performance and generate optimization recommendations"""

        if not recent_signals:
            return []

        performance_data = self._analyze_signal_performance(recent_signals, source.keywords)

        prompt = f"""
        Analyze signal discovery performance and recommend optimizations:
        
        Current Configuration:
        - Platform: {source.platform}
        - Sources: {source.source_name}
        - Keywords: {source.keywords}
        - Business Context: {source.business_context}
        
        Performance Data:
        {json.dumps(performance_data, indent=2)}
        
        Provide optimization recommendations:
        1. Underperforming keywords to remove or modify
        2. New keywords to add based on successful signal patterns
        3. Additional sources to monitor
        4. Scanning frequency adjustments
        
        Return JSON array of recommendations:
        [
            {{
                "type": "keyword_remove",
                "item": "low-performing-keyword",
                "reasoning": "explanation",
                "confidence": 0.75,
                "predicted_improvement": {{"signal_quality": "+15%"}}
            }}
        ]
        """

        try:
            response = client.chat.completions.create(model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2)

            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return []

    def _analyze_signal_performance(self, signals: List['Signal'], keywords: List[str]) -> Dict:
        """Analyze signal performance metrics"""
        total_signals = len(signals)
        avg_relevance = sum(s.relevance_score for s in signals) / total_signals if total_signals > 0 else 0

        keyword_performance = {}
        for keyword in keywords:
            matching_signals = [s for s in signals if keyword.lower() in (s.title + s.content).lower()]
            keyword_performance[keyword] = {
                'signals_found': len(matching_signals),
                'avg_relevance': sum(s.relevance_score for s in matching_signals) / len(matching_signals) if matching_signals else 0,
                'signal_types': list(set(s.signal_type for s in matching_signals))
            }

        return {
            'total_signals': total_signals,
            'avg_relevance_score': avg_relevance,
            'keyword_performance': keyword_performance,
            'signal_type_distribution': {
                signal_type: len([s for s in signals if s.signal_type == signal_type])
                for signal_type in set(s.signal_type for s in signals)
            }
        }

    async def get_content_analysis_summary(self, org_id: str) -> Dict[str, Any]:
        """Get summary of VoiceForge content analysis for signal strategy"""
        try:
            content_analysis = await self.content_ai.analyze_voiceforge_content(org_id)
            return {
                'has_content': not content_analysis.get('fallback', False),
                'summary': content_analysis.get('summary', 'No content analysis available'),
                'key_themes': content_analysis.get('primary_value_propositions', [])[:3],
                'target_industries': [content_analysis.get('industry_positioning', {}).get('primary_industry', 'Unknown')],
                'content_pieces': content_analysis.get('content_metadata', {}).get('total_pieces', 0)
            }
        except Exception as e:
            return {
                'has_content': False,
                'summary': f'Content analysis failed: {str(e)}',
                'key_themes': [],
                'target_industries': [],
                'content_pieces': 0
            }
