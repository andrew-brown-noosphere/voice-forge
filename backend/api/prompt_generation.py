"""
Enhanced Intelligent Prompt Generation API with Gypsum Integration
Generates smart default prompts based on crawled content AND Gypsum persona data/messaging frameworks
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from api.dependencies import get_db, get_rag_service
from auth.clerk_auth import get_current_user_with_org, AuthUser, get_org_id_from_user
from api.models import ContentPlatform, ContentTone, FunnelStage
from signals.content_driven_ai import ContentDrivenSignalAI

logger = logging.getLogger(__name__)

# Create router for prompt generation endpoints
prompt_router = APIRouter(prefix="/api/prompts", tags=["Intelligent Prompt Generation"])

# Pydantic models
class GeneratedPrompt(BaseModel):
    """A generated prompt suggestion enhanced with Gypsum persona insights"""
    title: str = Field(..., description="Short title for the prompt")
    prompt: str = Field(..., description="The actual prompt text")
    platform: ContentPlatform = Field(..., description="Recommended platform")
    tone: ContentTone = Field(..., description="Recommended tone")
    funnel_stage: FunnelStage = Field(..., description="Target funnel stage")
    category: str = Field(..., description="Content category")
    confidence: float = Field(..., description="Confidence score 0-1")
    reasoning: str = Field(..., description="Why this prompt was suggested")
    keywords: List[str] = Field(..., description="Key topics/keywords from content")
    persona_alignment: Dict[str, Any] = Field(..., description="How this aligns with target persona")
    messaging_framework: Dict[str, Any] = Field(..., description="Messaging framework elements")

class PromptGenerationRequest(BaseModel):
    """Request for generating prompts with Gypsum integration"""
    domain: Optional[str] = Field(None, description="Filter by specific domain")
    platform: Optional[ContentPlatform] = Field(None, description="Target platform")
    funnel_stage: Optional[FunnelStage] = Field(None, description="Target funnel stage for content")
    max_prompts: int = Field(1, ge=1, le=10, description="Maximum prompts to generate")
    focus_areas: Optional[List[str]] = Field(None, description="Specific areas to focus on")
    persona_id: Optional[str] = Field(None, description="Target Gypsum persona ID")
    include_messaging_framework: bool = Field(True, description="Include messaging framework data")

class PromptGenerationResponse(BaseModel):
    """Response containing generated prompts with Gypsum insights"""
    prompts: List[GeneratedPrompt] = Field(..., description="Generated prompt suggestions")
    content_summary: Dict[str, Any] = Field(..., description="Summary of analyzed content")
    persona_context: Dict[str, Any] = Field(..., description="Gypsum persona context")
    messaging_insights: Dict[str, Any] = Field(..., description="Messaging framework insights")
    metadata: Dict[str, Any] = Field(..., description="Generation metadata")

class GypsumEnhancedPromptGenerator:
    """Enhanced prompt generator that integrates VoiceForge content with Gypsum persona data"""
    
    def __init__(self, db, gypsum_client=None):
        self.db = db
        self.gypsum_client = gypsum_client
        # Remove ContentDrivenSignalAI dependency for now
        # self.content_driven_ai = ContentDrivenSignalAI(db, gypsum_client)
        
        # Enhanced prompt templates with messaging framework integration
        self.prompt_templates = {
            'software_technical': [
                {
                    'title': 'Persona-Targeted Implementation Guide',
                    'template': 'Write a {tone} implementation guide showing {persona_role} at {persona_company_size} companies how to integrate {company}\'s {main_service} to solve {persona_pain_point}, addressing their specific concerns about {persona_barrier} and highlighting {value_prop}.',
                    'platform': ContentPlatform.BLOG,
                    'tone': ContentTone.INFORMATIVE,
                    'category': 'persona_targeted_guide',
                    'keywords': ['implementation', 'integration', 'persona-specific'],
                    'persona_elements': ['role', 'company_size', 'pain_points', 'barriers'],
                    'messaging_elements': ['value_propositions', 'competitive_advantages']
                },
                {
                    'title': 'Pain Point Solution Case Study',
                    'template': 'Create a compelling case study showing how {company}\'s {key_feature} helped a {persona_role} overcome {specific_pain_point}, resulting in {quantified_benefit}. Focus on the {emotional_trigger} and include technical details that matter to {persona_role}.',
                    'platform': ContentPlatform.LINKEDIN,
                    'tone': ContentTone.PROFESSIONAL,
                    'category': 'pain_point_case_study',
                    'keywords': ['case study', 'pain point', 'solution'],
                    'persona_elements': ['role', 'pain_points', 'goals'],
                    'messaging_elements': ['emotional_triggers', 'quantified_benefits']
                }
            ],
            'saas_business': [
                {
                    'title': 'ROI-Focused Value Proposition',
                    'template': 'Develop a {tone} analysis showing {persona_role} at {persona_industry} companies how {company}\'s platform delivers {primary_value_prop} by addressing {industry_challenge}, with specific ROI calculations relevant to {persona_company_size} organizations and messaging that resonates with {persona_motivation}.',
                    'platform': ContentPlatform.WEBSITE,
                    'tone': ContentTone.AUTHORITATIVE,
                    'category': 'roi_value_proposition',
                    'keywords': ['roi', 'value proposition', 'industry-specific'],
                    'persona_elements': ['role', 'industry', 'company_size', 'motivations'],
                    'messaging_elements': ['primary_value_propositions', 'industry_positioning']
                },
                {
                    'title': 'Competitive Positioning Content',
                    'template': 'Write content that positions {company} against competitors by highlighting {competitive_advantage} in a way that speaks directly to {persona_role}\'s concerns about {competitor_weakness}, using {messaging_theme} to reinforce our unique position.',
                    'platform': ContentPlatform.BLOG,
                    'tone': ContentTone.PERSUASIVE,
                    'category': 'competitive_positioning',
                    'keywords': ['competitive', 'positioning', 'differentiation'],
                    'persona_elements': ['role', 'decision_criteria'],
                    'messaging_elements': ['competitive_advantages', 'messaging_themes']
                }
            ],
            'persona_general': [
                {
                    'title': 'Persona Journey Content',
                    'template': 'Create content that guides {persona_role} through their journey from {current_state} to {desired_state}, addressing {persona_barrier} with {solution_benefit} and using {messaging_theme} to build trust.',
                    'platform': ContentPlatform.EMAIL,
                    'tone': ContentTone.FRIENDLY,
                    'category': 'persona_journey',
                    'keywords': ['persona journey', 'transformation', 'trust building'],
                    'persona_elements': ['role', 'current_state', 'desired_state', 'barriers'],
                    'messaging_elements': ['solution_benefits', 'messaging_themes']
                }
            ]
        }
    
    async def generate_prompts(self, org_id: str, request: PromptGenerationRequest) -> PromptGenerationResponse:
        """Generate intelligent prompts enhanced with Gypsum persona data"""
        try:
            logger.info(f"Generating enhanced prompts for org {org_id} with persona {request.persona_id}")
            
            # Step 1: Get actual Gypsum messaging data (simulated for now)
            gypsum_data = await self._get_gypsum_messaging_data(org_id)
            
            # Step 2: Get persona context
            persona_context = await self._get_persona_context(org_id, request.persona_id)
            
            # Step 3: Use AI to generate creative, varied prompts based on Gypsum data
            ai_generated_prompts = await self._generate_ai_prompts(
                gypsum_data,
                persona_context,
                request.platform,
                request.funnel_stage,
                request.max_prompts
            )
            
            return PromptGenerationResponse(
                prompts=ai_generated_prompts,
                content_summary={
                    'business_type': gypsum_data.get('positioning', {}).get('category', 'API Development Platform'),
                    'value_propositions': [gypsum_data.get('messaging', {}).get('headline_message', '')],
                    'key_features': gypsum_data.get('messaging', {}).get('key_differentiators', []),
                    'total_content': 'Gypsum messaging data',
                    'key_topics': gypsum_data.get('messaging', {}).get('key_differentiators', [])[:3]
                },
                persona_context={
                    'persona_id': request.persona_id,
                    'role': persona_context.get('role', 'Business Manager'),
                    'industry': persona_context.get('industry', 'Technology'),
                    'pain_points': persona_context.get('pain_points', []),
                    'goals': persona_context.get('goals', []),
                    'company_size': persona_context.get('company_size', 'Enterprise')
                },
                messaging_insights={
                    'framework_included': True,
                    'confidence_score': 0.9,
                    'messaging_elements': gypsum_data.get('messaging', {})
                },
                metadata={
                    'generated_at': datetime.now().isoformat(),
                    'analysis_successful': True,
                    'persona_integrated': bool(request.persona_id),
                    'prompt_count': len(ai_generated_prompts),
                    'org_id': org_id,
                    'ai_generated': True
                }
            )
            
        except Exception as e:
            logger.error(f"Enhanced prompt generation failed for org {org_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate enhanced prompts: {str(e)}"
            )
    
    async def _get_gypsum_messaging_data(self, org_id: str) -> Dict[str, Any]:
        """Get Gypsum messaging data (simulated for now)"""
        # This simulates the data we know exists from the frontend console logs
        return {
            'messaging': {
                'headline_message': 'Build APIs 10x faster with enterprise-grade schema management',
                'elevator_pitch': 'Buf is the platform that makes Protobuf and gRPC accessible to any team while preventing API-related bugs and accelerating API development',
                'key_differentiators': [
                    'Enterprise-grade schema management',
                    'Prevents breaking changes',
                    'Accelerates API development', 
                    'Centralized schema registry',
                    'Seamless CI/CD integration'
                ],
                'tone_voice': 'Technical yet approachable, emphasizing developer productivity and enterprise reliability',
                'supporting_points': 'Centralized schema registry prevents breaking changes and integration fits into existing development workflows'
            },
            'positioning': {
                'target_market': 'Software development teams building and maintaining APIs and microservices',
                'category': 'API Development and Schema Management Platform',
                'differentiation': 'Complete platform for API-first development that makes Protobuf and gRPC accessible to any team'
            }
        }
    
    async def _get_persona_context(self, org_id: str, persona_id: Optional[str]) -> Dict[str, Any]:
        """Get persona context (simulated for now)"""
        # This simulates the personas we know exist from the frontend console logs
        personas = {
            '073b7355-16d3-4611-902b-4029dd3aeb84': {
                'role': 'DevOps Engineer',
                'industry': 'Software Development', 
                'pain_points': ['Manual certificate management', 'Compliance overhead', 'Security vulnerabilities'],
                'goals': ['Automate workflows', 'Ensure security', 'Reduce manual work'],
                'company_size': 'Enterprise'
            }
        }
        
        if persona_id and persona_id in personas:
            return personas[persona_id]
        
        # Default persona
        return {
            'role': 'Business Manager',
            'industry': 'Technology',
            'pain_points': ['Manual processes', 'Integration challenges', 'Scalability issues'],
            'goals': ['Improve efficiency', 'Reduce costs', 'Scale operations'],
            'company_size': 'Enterprise'
        }
    
    async def _generate_ai_prompts(
        self, 
        gypsum_data: Dict[str, Any], 
        persona_context: Dict[str, Any],
        target_platform: Optional[str],
        funnel_stage: Optional[FunnelStage],
        max_prompts: int
    ) -> List[GeneratedPrompt]:
        """Use AI to generate creative, varied content prompts based on Gypsum messaging"""
        try:
            from openai import AsyncOpenAI
            import os
            
            client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            # Extract key information
            messaging = gypsum_data.get('messaging', {})
            positioning = gypsum_data.get('positioning', {})
            
            # Define funnel stage context
            funnel_guidance = self._get_funnel_stage_guidance(funnel_stage)
            
            # Build AI prompt for generating content prompts
            ai_prompt = f"""
            You are a content marketing expert. Generate {max_prompts} creative, engaging content prompts based on this company's messaging and target persona.
            
            COMPANY MESSAGING:
            - Headline: {messaging.get('headline_message', '')}
            - Elevator Pitch: {messaging.get('elevator_pitch', '')}
            - Key Features: {', '.join(messaging.get('key_differentiators', []))}
            - Target Market: {positioning.get('target_market', '')}
            - Tone: {messaging.get('tone_voice', '')}
            
            TARGET PERSONA:
            - Role: {persona_context.get('role', '')}
            - Industry: {persona_context.get('industry', '')}
            - Pain Points: {', '.join(persona_context.get('pain_points', []))}
            - Goals: {', '.join(persona_context.get('goals', []))}
            - Company Size: {persona_context.get('company_size', '')}
            
            PLATFORM: {target_platform or 'Any platform'}
            FUNNEL STAGE: {funnel_stage.value.upper() if funnel_stage else 'Any stage'}
            
            {funnel_guidance}
            
            Generate {max_prompts} diverse, creative content prompts that:
            1. Use the company's actual messaging and value propositions
            2. Address the persona's specific pain points and goals
            3. Are engaging and actionable (not generic)
            4. Focus on CONTENT IDEAS rather than specific formats
            5. Are completely platform-agnostic (avoid words like "blog post", "article", "guide", "whitepaper")
            6. Are specifically designed for the {funnel_stage.value.upper() if funnel_stage else 'specified'} funnel stage
            7. Use action words like "discuss", "explain", "share", "highlight", "compare" instead of format words
            
            AVOID format-specific language:
            - Don't say: "Create a blog post about...", "Write an article on...", "Develop a guide for..."
            - Instead say: "Discuss...", "Explain...", "Share insights about...", "Highlight..."
            
            Return as JSON array with this structure:
            [
                {{
                    "title": "Compelling title for the content idea",
                    "prompt": "Platform-agnostic content prompt focused on the core idea",
                    "platform": "recommended platform",
                    "tone": "recommended tone",
                    "funnel_stage": "{funnel_stage.value if funnel_stage else 'tofu'}",
                    "category": "content category",
                    "reasoning": "why this content idea is effective for this persona and funnel stage",
                    "keywords": ["keyword1", "keyword2", "keyword3"]
                }}
            ]
            
            Remember: Focus on WHAT to communicate, not HOW to format it. The user will choose the platform and format later.
            """
            
            response = await client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert content marketing strategist who creates highly targeted, brand-specific content prompts."},
                    {"role": "user", "content": ai_prompt}
                ],
                temperature=0.7
            )
            
            import json
            ai_prompts_data = json.loads(response.choices[0].message.content)
            
            # Convert to GeneratedPrompt objects
            generated_prompts = []
            for i, prompt_data in enumerate(ai_prompts_data[:max_prompts]):
                # Map funnel stage from AI response or use requested stage
                ai_funnel_stage = prompt_data.get('funnel_stage', '')
                mapped_funnel_stage = self._map_funnel_stage(ai_funnel_stage) if ai_funnel_stage else (funnel_stage or FunnelStage.TOFU)
                
                generated_prompt = GeneratedPrompt(
                    title=prompt_data.get('title', f'Content Prompt {i+1}'),
                    prompt=prompt_data.get('prompt', ''),
                    platform=self._map_platform(prompt_data.get('platform', 'blog')),
                    tone=self._map_tone(prompt_data.get('tone', 'professional')),
                    funnel_stage=mapped_funnel_stage,
                    category=prompt_data.get('category', 'business_content'),
                    confidence=0.85,  # High confidence since AI-generated with real data
                    reasoning=prompt_data.get('reasoning', f'AI-generated based on company messaging and persona for {mapped_funnel_stage.value.upper()} stage'),
                    keywords=prompt_data.get('keywords', [])[:5],
                    persona_alignment={
                        'role_match': 1.0,
                        'pain_point_addressed': 0.9,
                        'goal_alignment': 0.9,
                        'overall_score': 0.9
                    },
                    messaging_framework={
                        'primary_message': messaging.get('headline_message', ''),
                        'emotional_trigger': 'productivity and efficiency',
                        'competitive_angle': 'enterprise-grade reliability',
                        'supporting_benefits': messaging.get('key_differentiators', [])[:3]
                    }
                )
                generated_prompts.append(generated_prompt)
            
            return generated_prompts
            
        except Exception as e:
            logger.error(f"AI prompt generation failed: {e}")
            # Fallback to template-based prompts if AI fails
            return self._create_template_prompts(gypsum_data, persona_context, funnel_stage, max_prompts)
    
    def _map_platform(self, platform_str: str) -> ContentPlatform:
        """Map platform string to enum"""
        platform_mapping = {
            'twitter': ContentPlatform.TWITTER,
            'linkedin': ContentPlatform.LINKEDIN,
            'facebook': ContentPlatform.FACEBOOK,
            'instagram': ContentPlatform.INSTAGRAM,
            'email': ContentPlatform.EMAIL,
            'blog': ContentPlatform.BLOG,
            'website': ContentPlatform.WEBSITE,
            'customer_support': ContentPlatform.CUSTOMER_SUPPORT
        }
        return platform_mapping.get(platform_str.lower(), ContentPlatform.BLOG)
    
    def _map_tone(self, tone_str: str) -> ContentTone:
        """Map tone string to enum"""
        tone_mapping = {
            'professional': ContentTone.PROFESSIONAL,
            'casual': ContentTone.CASUAL,
            'friendly': ContentTone.FRIENDLY,
            'enthusiastic': ContentTone.ENTHUSIASTIC,
            'informative': ContentTone.INFORMATIVE,
            'persuasive': ContentTone.PERSUASIVE,
            'authoritative': ContentTone.AUTHORITATIVE
        }
        return tone_mapping.get(tone_str.lower(), ContentTone.PROFESSIONAL)
    
    def _map_funnel_stage(self, stage_str: str) -> FunnelStage:
        """Map funnel stage string to enum"""
        stage_mapping = {
            'tofu': FunnelStage.TOFU,
            'mofu': FunnelStage.MOFU,
            'bofu': FunnelStage.BOFU,
            'awareness': FunnelStage.TOFU,
            'consideration': FunnelStage.MOFU,
            'decision': FunnelStage.BOFU
        }
        return stage_mapping.get(stage_str.lower(), FunnelStage.TOFU)
    
    def _get_funnel_stage_guidance(self, funnel_stage: Optional[FunnelStage]) -> str:
        """Get guidance text for the specified funnel stage"""
        if not funnel_stage:
            return "Focus on content that could work across all funnel stages."
        
        guidance_map = {
            FunnelStage.TOFU: """
            TOFU (TOP OF FUNNEL - AWARENESS STAGE) FOCUS:
            - Educational content ideas that build awareness
            - Problem identification and industry insights
            - Thought leadership concepts and perspectives
            - Trend analysis and market observations
            - Focus on core messaging, not content format
            - Use verbs like "discuss", "explain", "explore", "highlight"
            - NEVER mention specific formats like "blog post", "article", "guide"
            - Examples: "Discuss the main challenges in [Industry]", "Explain why [Problem] matters to [Audience]", "Highlight emerging trends in [Field]"
            """,
            
            FunnelStage.MOFU: """
            MOFU (MIDDLE OF FUNNEL - CONSIDERATION STAGE) FOCUS:
            - Solution-focused content ideas for evaluation
            - Comparison concepts and decision frameworks
            - Success stories and example outcomes
            - Best practices and proven methodologies
            - Use action words like "compare", "evaluate", "analyze", "share"
            - AVOID format words like "case study", "whitepaper", "guide"
            - Focus on solution concepts that work across all platforms
            - Examples: "Compare different approaches to [Problem]", "Evaluate options for [Challenge]", "Share success stories about [Solution]"
            """,
            
            FunnelStage.BOFU: """
            BOFU (BOTTOM OF FUNNEL - DECISION STAGE) FOCUS:
            - Product-specific content ideas that drive decisions
            - ROI and business value messaging
            - Implementation insights and practical advice
            - Feature benefits and competitive advantages
            - Success measurement and outcome focus
            - Use action words like "explain", "demonstrate", "show", "highlight"
            - AVOID format words like "calculator", "checklist", "template"
            - Focus on persuasive messaging that works on any platform
            - Examples: "Explain the ROI of [Solution]", "Demonstrate the value of [Feature]", "Show implementation success stories"
            """
        }
        
        return guidance_map.get(funnel_stage, "")
    
    def _create_template_prompts(
        self, 
        gypsum_data: Dict[str, Any], 
        persona_context: Dict[str, Any], 
        funnel_stage: Optional[FunnelStage],
        max_prompts: int
    ) -> List[GeneratedPrompt]:
        """Fallback template-based prompts if AI generation fails"""
        messaging = gypsum_data.get('messaging', {})
        positioning = gypsum_data.get('positioning', {})
        
        # Create funnel-aware templates
        templates = self._get_funnel_aware_templates(messaging, positioning, persona_context, funnel_stage)
        
        generated_prompts = []
        for i, template in enumerate(templates[:max_prompts]):
            generated_prompt = GeneratedPrompt(
                title=template['title'],
                prompt=template['prompt'],
                platform=ContentPlatform.BLOG,
                tone=ContentTone.INFORMATIVE,
                funnel_stage=template.get('funnel_stage', funnel_stage or FunnelStage.TOFU),
                category=template['category'],
                confidence=0.75,
                reasoning=f"Template-based prompt incorporating Gypsum messaging for {persona_context.get('role', 'target audience')} in {template.get('funnel_stage', funnel_stage or FunnelStage.TOFU).value.upper()} stage",
                keywords=messaging.get('key_differentiators', [])[:3],
                persona_alignment={
                    'role_match': 0.8,
                    'pain_point_addressed': 0.7,
                    'goal_alignment': 0.8,
                    'overall_score': 0.75
                },
                messaging_framework={
                    'primary_message': messaging.get('headline_message', ''),
                    'emotional_trigger': 'productivity improvement',
                    'competitive_angle': 'enterprise reliability',
                    'supporting_benefits': messaging.get('key_differentiators', [])[:3]
                }
            )
            generated_prompts.append(generated_prompt)
        
        return generated_prompts
    
    def _get_funnel_aware_templates(
        self, 
        messaging: Dict[str, Any], 
        positioning: Dict[str, Any], 
        persona_context: Dict[str, Any],
        funnel_stage: Optional[FunnelStage]
    ) -> List[Dict[str, Any]]:
        """Get templates appropriate for the specified funnel stage"""
        
        # If no funnel stage specified, return a mix
        if not funnel_stage:
            return self._get_mixed_funnel_templates(messaging, positioning, persona_context)
        
        # Funnel-specific templates
        if funnel_stage == FunnelStage.TOFU:
            return [
                {
                    'title': f'Key Challenges Facing {persona_context.get("industry", "Technology")} Teams',
                    'prompt': f"Discuss the main challenges {persona_context.get('role', 'professionals')} face in the {persona_context.get('industry', 'technology')} industry. Focus on problem awareness and industry insights. Address pain points like {', '.join(persona_context.get('pain_points', ['operational challenges'])[:2])} and provide thought leadership on emerging trends.",
                    'category': 'awareness_education',
                    'funnel_stage': FunnelStage.TOFU
                },
                {
                    'title': f'Industry Trends Shaping {positioning.get("target_market", "Software Development")}',
                    'prompt': f"Share insights about key trends affecting {positioning.get('target_market', 'your industry')}. Discuss how these trends relate to challenges like {persona_context.get('pain_points', ['current challenges'])[0]} and what {persona_context.get('role', 'professionals')} should be aware of. Keep it educational and industry-focused.",
                    'category': 'thought_leadership',
                    'funnel_stage': FunnelStage.TOFU
                },
                {
                    'title': f'Understanding {messaging.get("key_differentiators", ["Modern Solutions"])[0]}',
                    'prompt': f"Explain the fundamentals of {messaging.get('key_differentiators', ['your solution area'])[0].lower()}. Help {persona_context.get('role', 'readers')} understand what it is, why it matters, and how it addresses common industry challenges. Focus on education rather than promotion.",
                    'category': 'educational_content',
                    'funnel_stage': FunnelStage.TOFU
                }
            ]
        
        elif funnel_stage == FunnelStage.MOFU:
            return [
                {
                    'title': f'Choosing the Right Solution for {persona_context.get("pain_points", ["Your Challenges"])[0]}',
                    'prompt': f"Compare different approaches to solving {persona_context.get('pain_points', ['their main challenge'])[0]} for {persona_context.get('role', 'decision makers')}. Include evaluation criteria, key questions to consider, and different solution approaches. Reference how solutions like {messaging.get('elevator_pitch', 'modern platforms')} address these needs.",
                    'category': 'evaluation_guide',
                    'funnel_stage': FunnelStage.MOFU
                },
                {
                    'title': f'Success Story: How {persona_context.get("company_size", "Enterprise")} Teams Solved {persona_context.get("pain_points", ["API Management Challenges"])[0]}',
                    'prompt': f"Share a success story showing how a {persona_context.get('company_size', 'similar-sized')} company in the {persona_context.get('industry', 'technology')} industry successfully addressed {persona_context.get('pain_points', ['their main challenge'])[0]}. Include their evaluation process, solution selection approach, and measurable results that {persona_context.get('role', 'similar professionals')} can learn from.",
                    'category': 'success_story',
                    'funnel_stage': FunnelStage.MOFU
                },
                {
                    'title': f'Best Practices for Implementing {messaging.get("key_differentiators", ["Modern Solutions"])[0]}',
                    'prompt': f"Discuss proven best practices that {persona_context.get('role', 'teams')} can use to successfully implement {messaging.get('key_differentiators', ['your solution type'])[0].lower()}. Include common pitfalls to avoid and step-by-step methodology. Address concerns like {', '.join(persona_context.get('pain_points', ['implementation challenges'])[:2])} and show how to achieve goals like {persona_context.get('goals', ['improved efficiency'])[0]}.",
                    'category': 'best_practices',
                    'funnel_stage': FunnelStage.MOFU
                }
            ]
        
        elif funnel_stage == FunnelStage.BOFU:
            return [
                {
                    'title': f'ROI of {messaging.get("headline_message", "Your Solution").split()[0]} Solutions',
                    'prompt': f"Explain the business impact and ROI for {persona_context.get('role', 'decision makers')} considering {messaging.get('headline_message', 'solution investments').lower()}. Include specific benefits, cost considerations, and timeline for seeing returns. Address how {', '.join(messaging.get('key_differentiators', [])[:2])} translate to measurable business outcomes for {persona_context.get('company_size', 'organizations')} like theirs.",
                    'category': 'roi_analysis',
                    'funnel_stage': FunnelStage.BOFU
                },
                {
                    'title': f'Getting Started with {messaging.get("key_differentiators", ["Your Solution"])[0]}',
                    'prompt': f"Share practical insights for {persona_context.get('role', 'teams')} ready to implement {messaging.get('key_differentiators', ['your solution'])[0].lower()}. Include preparation steps, key considerations, team onboarding tips, and success metrics. Address how to achieve {persona_context.get('goals', ['their objectives'])[0]} and measure progress.",
                    'category': 'implementation_insights',
                    'funnel_stage': FunnelStage.BOFU
                },
                {
                    'title': f'Measuring Success with {messaging.get("headline_message", "Solution Implementation").split()[-2:][0]} Implementation',
                    'prompt': f"Discuss how to measure success and track key metrics after implementing {messaging.get('headline_message', 'your solution').lower()}. Include specific metrics that matter to {persona_context.get('role', 'stakeholders')}, reporting approaches, and benchmarks for {persona_context.get('company_size', 'organizations')} in the {persona_context.get('industry', 'technology')} industry. Show how to demonstrate ROI and continuous improvement.",
                    'category': 'success_measurement',
                    'funnel_stage': FunnelStage.BOFU
                }
            ]
        
        return []
    
    def _get_mixed_funnel_templates(
        self, 
        messaging: Dict[str, Any], 
        positioning: Dict[str, Any], 
        persona_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get a mix of templates across all funnel stages when no specific stage is requested"""
        return [
            {
                'title': f'Industry Overview: Key Trends in {persona_context.get("industry", "Technology")}',
                'prompt': f"Share insights about key industry trends affecting {persona_context.get('role', 'professionals')} in {persona_context.get('industry', 'technology')}. Focus on broad industry insights and emerging challenges.",
                'category': 'industry_overview',
                'funnel_stage': FunnelStage.TOFU
            },
            {
                'title': f'Solution Comparison: Evaluating Options for {persona_context.get("pain_points", ["Business Challenges"])[0]}',
                'prompt': f"Compare different approaches for {persona_context.get('role', 'decision makers')} evaluating solutions to {persona_context.get('pain_points', ['their challenges'])[0]}. Include evaluation criteria and methodology.",
                'category': 'solution_comparison',
                'funnel_stage': FunnelStage.MOFU
            },
            {
                'title': f'Implementation Insights: Getting Started with {messaging.get("key_differentiators", ["Your Solution"])[0]}',
                'prompt': f"Share practical insights for {persona_context.get('role', 'teams')} ready to get started with {messaging.get('key_differentiators', ['solutions'])[0].lower()}. Include specific steps and success metrics.",
                'category': 'implementation_insights',
                'funnel_stage': FunnelStage.BOFU
            }
        ]
    
    async def _generate_messaging_insights(
        self, 
        content_analysis: Dict, 
        persona: Dict,
        include_framework: bool = True
    ) -> Dict[str, Any]:
        """Generate messaging insights by combining content analysis with persona data"""
        
        if not include_framework:
            return {'framework_included': False}
        
        try:
            # Extract messaging elements from content analysis
            messaging_elements = {
                'value_propositions': content_analysis.get('primary_value_propositions', []),
                'emotional_triggers': content_analysis.get('emotional_triggers', []),
                'messaging_themes': content_analysis.get('messaging_themes', []),
                'competitive_advantages': content_analysis.get('competitive_advantages', []),
                'pain_points_addressed': content_analysis.get('customer_pain_points', [])
            }
            
            # Combine with persona insights
            persona_alignment = {
                'role_relevance': self._calculate_role_relevance(messaging_elements, persona),
                'pain_point_match': self._match_pain_points(
                    content_analysis.get('problems_addressed', []),
                    persona.get('pain_points', [])
                ),
                'goal_alignment': self._align_with_goals(
                    content_analysis.get('solution_benefits', []),
                    persona.get('goals', [])
                ),
                'messaging_fit': self._assess_messaging_fit(messaging_elements, persona)
            }
            
            # Generate messaging framework recommendations
            framework_recommendations = {
                'primary_message': self._generate_primary_message(content_analysis, persona),
                'supporting_points': self._generate_supporting_points(messaging_elements, persona),
                'tone_recommendations': self._recommend_tone_for_persona(persona),
                'channel_preferences': self._recommend_channels_for_persona(persona),
                'objection_handling': self._generate_objection_handling(content_analysis, persona)
            }
            
            return {
                'framework_included': True,
                'messaging_elements': messaging_elements,
                'persona_alignment': persona_alignment,
                'framework_recommendations': framework_recommendations,
                'confidence_score': self._calculate_messaging_confidence(content_analysis, persona)
            }
            
        except Exception as e:
            logger.error(f"Error generating messaging insights: {e}")
            return {'framework_included': False, 'error': str(e)}
    
    async def _create_enhanced_prompts(
        self,
        content_analysis: Dict,
        persona: Dict,
        messaging_insights: Dict,
        request: PromptGenerationRequest
    ) -> List[GeneratedPrompt]:
        """Create enhanced prompts using content analysis + persona + messaging framework"""
        
        prompts = []
        
        # Determine business category for template selection
        industry = content_analysis.get('industry_positioning', {}).get('primary_industry', '').lower()
        if 'software' in industry or 'tech' in industry:
            if persona.get('role', '').lower() in ['developer', 'engineer', 'architect']:
                template_category = 'software_technical'
            else:
                template_category = 'saas_business'
        elif 'saas' in industry:
            template_category = 'saas_business'
        else:
            template_category = 'persona_general'
        
        # Get relevant templates
        templates = self.prompt_templates.get(template_category, self.prompt_templates['persona_general'])
        
        # Extract key information for prompt customization
        company_name = self._extract_company_name(content_analysis)
        persona_variables = self._extract_persona_variables(persona)
        messaging_variables = self._extract_messaging_variables(content_analysis, messaging_insights)
        
        # Generate prompts from templates
        for i, template in enumerate(templates[:request.max_prompts]):
            try:
                # Create enhanced prompt with persona and messaging integration
                enhanced_prompt = await self._create_enhanced_prompt(
                    template,
                    content_analysis,
                    persona,
                    messaging_insights,
                    company_name,
                    persona_variables,
                    messaging_variables,
                    request
                )
                
                if enhanced_prompt:
                    prompts.append(enhanced_prompt)
                    
            except Exception as e:
                logger.warning(f"Failed to generate enhanced prompt {i}: {e}")
                continue
        
        # Sort by confidence and persona alignment
        prompts.sort(key=lambda x: (x.confidence + x.persona_alignment.get('overall_score', 0)) / 2, reverse=True)
        
        return prompts[:request.max_prompts]
    
    async def _create_enhanced_prompt(
        self,
        template: Dict,
        content_analysis: Dict,
        persona: Dict,
        messaging_insights: Dict,
        company_name: str,
        persona_variables: Dict,
        messaging_variables: Dict,
        request: PromptGenerationRequest
    ) -> Optional[GeneratedPrompt]:
        """Create a single enhanced prompt with full integration"""
        
        try:
            # Build template variables
            template_vars = {
                'company': company_name,
                'tone': template['tone'].value.lower(),
                **persona_variables,
                **messaging_variables
            }
            
            # Fill in the template
            prompt_text = template['template'].format(**template_vars)
            
            # Calculate confidence score
            base_confidence = 0.6
            content_bonus = min(0.2, len(content_analysis.get('key_features', [])) * 0.05)
            persona_bonus = 0.2 if persona.get('role') != 'unknown' else 0.0
            messaging_bonus = 0.1 if messaging_insights.get('framework_included') else 0.0
            
            confidence = min(1.0, base_confidence + content_bonus + persona_bonus + messaging_bonus)
            
            # Calculate persona alignment
            persona_alignment = {
                'role_match': 1.0 if persona.get('role', '').lower() in template_vars.get('persona_role', '').lower() else 0.5,
                'pain_point_addressed': self._check_pain_point_addressed(template, persona),
                'goal_alignment': self._check_goal_alignment(template, persona),
                'overall_score': confidence
            }
            
            # Extract messaging framework elements
            messaging_framework = {
                'primary_message': messaging_variables.get('primary_value_prop', ''),
                'emotional_trigger': messaging_variables.get('emotional_trigger', ''),
                'competitive_angle': messaging_variables.get('competitive_advantage', ''),
                'supporting_benefits': messaging_variables.get('solution_benefits', [])
            }
            
            # Create reasoning
            reasoning = self._create_enhanced_reasoning(
                template, persona, content_analysis, messaging_insights, company_name
            )
            
            # Filter by platform if requested
            if request.platform and template['platform'] != request.platform:
                return None
            
            return GeneratedPrompt(
                title=template['title'],
                prompt=prompt_text,
                platform=template['platform'],
                tone=template['tone'],
                category=template['category'],
                confidence=confidence,
                reasoning=reasoning,
                keywords=template['keywords'] + content_analysis.get('technical_keywords', [])[:3],
                persona_alignment=persona_alignment,
                messaging_framework=messaging_framework
            )
            
        except Exception as e:
            logger.error(f"Error creating enhanced prompt: {e}")
            return None
    
    def _extract_company_name(self, content_analysis: Dict) -> str:
        """Extract company name from content analysis"""
        # Try to get from content metadata or domains
        domains = content_analysis.get('content_metadata', {}).get('domains', [])
        if domains:
            domain = domains[0]
            name = domain.replace('https://', '').replace('http://', '').replace('www.', '')
            name = name.split('.')[0]
            return name.capitalize()
        return "[Company Name]"
    
    def _extract_persona_variables(self, persona: Dict) -> Dict[str, str]:
        """Extract persona variables for template filling"""
        return {
            'persona_role': persona.get('role', 'business professional'),
            'persona_industry': persona.get('industry', 'technology'),
            'persona_company_size': persona.get('company_size', 'mid-size'),
            'persona_pain_point': ', '.join(persona.get('pain_points', ['operational inefficiencies']))[:100],
            'persona_barrier': persona.get('barriers', ['budget constraints'])[0] if persona.get('barriers') else 'implementation complexity',
            'persona_motivation': ', '.join(persona.get('goals', ['improve efficiency']))[:100],
            'current_state': 'manual processes and inefficiencies',
            'desired_state': 'automated and optimized workflows'
        }
    
    def _extract_messaging_variables(self, content_analysis: Dict, messaging_insights: Dict) -> Dict[str, str]:
        """Extract messaging variables for template filling"""
        return {
            'primary_value_prop': content_analysis.get('primary_value_propositions', ['streamlined operations'])[0],
            'key_feature': content_analysis.get('key_features', ['automation platform'])[0],
            'main_service': content_analysis.get('key_features', ['platform'])[0],
            'competitive_advantage': content_analysis.get('competitive_advantages', ['innovative approach'])[0],
            'emotional_trigger': content_analysis.get('emotional_triggers', ['peace of mind'])[0],
            'solution_benefit': content_analysis.get('solution_benefits', ['increased productivity'])[0],
            'messaging_theme': content_analysis.get('messaging_themes', ['reliability and efficiency'])[0],
            'quantified_benefit': '30% productivity increase',
            'industry_challenge': 'operational complexity',
            'specific_pain_point': content_analysis.get('customer_pain_points', ['manual processes'])[0],
            'competitor_weakness': 'complexity and poor user experience'
        }
    
    def _calculate_role_relevance(self, messaging_elements: Dict, persona: Dict) -> float:
        """Calculate how relevant messaging is to persona role"""
        role = persona.get('role', '').lower()
        if not role:
            return 0.5
        
        # Check if messaging elements mention role-specific terms
        role_terms = {
            'developer': ['api', 'integration', 'code', 'technical'],
            'manager': ['efficiency', 'team', 'productivity', 'roi'],
            'founder': ['growth', 'scale', 'business', 'revenue']
        }
        
        relevant_terms = role_terms.get(role, [])
        messaging_text = ' '.join([
            ' '.join(messaging_elements.get('value_propositions', [])),
            ' '.join(messaging_elements.get('messaging_themes', []))
        ]).lower()
        
        matches = sum(1 for term in relevant_terms if term in messaging_text)
        return min(1.0, matches / len(relevant_terms) if relevant_terms else 0.5)
    
    def _match_pain_points(self, content_problems: List[str], persona_pain_points: List[str]) -> float:
        """Calculate match between content problems and persona pain points"""
        if not content_problems or not persona_pain_points:
            return 0.3
        
        matches = 0
        for content_problem in content_problems:
            for persona_pain in persona_pain_points:
                if any(word in content_problem.lower() for word in persona_pain.lower().split()):
                    matches += 1
                    break
        
        return min(1.0, matches / len(persona_pain_points))
    
    def _align_with_goals(self, solution_benefits: List[str], persona_goals: List[str]) -> float:
        """Calculate alignment between solution benefits and persona goals"""
        if not solution_benefits or not persona_goals:
            return 0.3
        
        matches = 0
        for benefit in solution_benefits:
            for goal in persona_goals:
                if any(word in benefit.lower() for word in goal.lower().split()):
                    matches += 1
                    break
        
        return min(1.0, matches / len(persona_goals))
    
    def _assess_messaging_fit(self, messaging_elements: Dict, persona: Dict) -> float:
        """Assess overall messaging fit for persona"""
        role_relevance = self._calculate_role_relevance(messaging_elements, persona)
        
        # Additional factors
        industry_match = 1.0 if persona.get('industry', '').lower() in ' '.join(messaging_elements.get('messaging_themes', [])).lower() else 0.5
        
        return (role_relevance + industry_match) / 2
    
    def _generate_primary_message(self, content_analysis: Dict, persona: Dict) -> str:
        """Generate primary message for persona"""
        value_prop = content_analysis.get('primary_value_propositions', ['improved efficiency'])[0]
        persona_role = persona.get('role', 'professionals')
        
        return f"Help {persona_role} achieve {value_prop} through our innovative solution"
    
    def _generate_supporting_points(self, messaging_elements: Dict, persona: Dict) -> List[str]:
        """Generate supporting points for messaging"""
        return [
            f"Addresses {persona.get('pain_points', ['common challenges'])[0]}",
            f"Delivers {messaging_elements.get('value_propositions', ['value'])[0]}",
            f"Provides {messaging_elements.get('competitive_advantages', ['unique benefits'])[0]}"
        ]
    
    def _recommend_tone_for_persona(self, persona: Dict) -> List[str]:
        """Recommend tone based on persona"""
        role = persona.get('role', '').lower()
        
        tone_mapping = {
            'developer': ['technical', 'informative', 'precise'],
            'manager': ['professional', 'authoritative', 'results-focused'],
            'founder': ['enthusiastic', 'visionary', 'growth-oriented']
        }
        
        return tone_mapping.get(role, ['professional', 'friendly', 'informative'])
    
    def _recommend_channels_for_persona(self, persona: Dict) -> List[str]:
        """Recommend channels based on persona"""
        role = persona.get('role', '').lower()
        
        channel_mapping = {
            'developer': ['blog', 'github', 'technical forums'],
            'manager': ['linkedin', 'email', 'webinars'],
            'founder': ['linkedin', 'twitter', 'industry events']
        }
        
        return channel_mapping.get(role, ['email', 'linkedin', 'website'])
    
    def _generate_objection_handling(self, content_analysis: Dict, persona: Dict) -> List[Dict[str, str]]:
        """Generate objection handling based on persona"""
        return [
            {
                'objection': f"Concerns about {persona.get('barriers', ['implementation'])[0]}",
                'response': f"Address through {content_analysis.get('competitive_advantages', ['proven approach'])[0]}"
            }
        ]
    
    def _calculate_messaging_confidence(self, content_analysis: Dict, persona: Dict) -> float:
        """Calculate confidence in messaging framework"""
        base_confidence = 0.5
        
        # More content elements = higher confidence
        content_richness = len(content_analysis.get('primary_value_propositions', [])) + \
                          len(content_analysis.get('competitive_advantages', []))
        content_bonus = min(0.3, content_richness * 0.05)
        
        # Persona completeness = higher confidence  
        persona_completeness = len([v for v in persona.values() if v and v != 'unknown'])
        persona_bonus = min(0.2, persona_completeness * 0.03)
        
        return min(1.0, base_confidence + content_bonus + persona_bonus)
    
    def _check_pain_point_addressed(self, template: Dict, persona: Dict) -> float:
        """Check if template addresses persona pain points"""
        template_text = template['template'].lower()
        pain_points = persona.get('pain_points', [])
        
        if not pain_points:
            return 0.5
        
        addressed = sum(1 for pain in pain_points if any(word in template_text for word in pain.lower().split()))
        return min(1.0, addressed / len(pain_points))
    
    def _check_goal_alignment(self, template: Dict, persona: Dict) -> float:
        """Check if template aligns with persona goals"""
        template_text = template['template'].lower()
        goals = persona.get('goals', [])
        
        if not goals:
            return 0.5
        
        aligned = sum(1 for goal in goals if any(word in template_text for word in goal.lower().split()))
        return min(1.0, aligned / len(goals))
    
    def _create_enhanced_reasoning(
        self, 
        template: Dict, 
        persona: Dict, 
        content_analysis: Dict, 
        messaging_insights: Dict,
        company_name: str
    ) -> str:
        """Create enhanced reasoning with persona and messaging context"""
        
        role = persona.get('role', 'professional')
        industry = persona.get('industry', 'business')
        
        reasoning = f"This prompt is specifically designed for {role}s in the {industry} industry, "
        reasoning += f"addressing their key pain point of {persona.get('pain_points', ['operational challenges'])[0]}. "
        
        if messaging_insights.get('framework_included'):
            reasoning += f"It leverages {company_name}'s core value proposition of "
            reasoning += f"{content_analysis.get('primary_value_propositions', ['improved efficiency'])[0]} "
            reasoning += f"and uses messaging that resonates with this persona's goals. "
        
        reasoning += f"The {template['category']} format and {template['tone'].value} tone "
        reasoning += f"are optimized for {template['platform'].value} engagement with this audience."
        
        return reasoning
    
    def _create_fallback_prompts(self, persona: Dict) -> List[GeneratedPrompt]:
        """Create fallback prompts when no content is available"""
        
        role = persona.get('role', 'business professional')
        industry = persona.get('industry', 'technology')
        
        fallback_prompts = [
            GeneratedPrompt(
                title=f"Persona-Targeted Company Introduction",
                prompt=f"Write an engaging introduction to your company specifically for {role}s in the {industry} industry, explaining how your solutions address their unique challenges and goals.",
                platform=ContentPlatform.WEBSITE,
                tone=ContentTone.PROFESSIONAL,
                category="persona_introduction",
                confidence=0.4,
                reasoning=f"Generic prompt customized for {role} persona. Crawl your website content to get highly personalized, content-driven prompts.",
                keywords=["company", "introduction", "persona-targeted"],
                persona_alignment={
                    'role_match': 1.0,
                    'pain_point_addressed': 0.3,
                    'goal_alignment': 0.3,
                    'overall_score': 0.4
                },
                messaging_framework={
                    'primary_message': f'Solutions designed for {role}s',
                    'emotional_trigger': 'professional success',
                    'competitive_angle': 'persona-specific approach',
                    'supporting_benefits': ['tailored solutions', 'industry expertise']
                }
            )
        ]
        
        return fallback_prompts

# API Endpoints
@prompt_router.post("/generate", response_model=PromptGenerationResponse)
async def generate_intelligent_prompts(
    request: PromptGenerationRequest,
    current_user: AuthUser = Depends(get_current_user_with_org),
    db = Depends(get_db)
):
    """
    Generate intelligent default prompts based on crawled content AND Gypsum persona data.
    
    This endpoint analyzes your organization's crawled content, combines it with Gypsum
    persona insights and messaging frameworks to generate highly targeted, personalized
    prompts that speak directly to your target audience.
    
    NEW: Funnel-aware prompt generation! Specify a funnel_stage to get prompts optimized for:
    - TOFU (Top of Funnel): Awareness-stage content, educational and broad
    - MOFU (Middle of Funnel): Consideration-stage content, solution-focused
    - BOFU (Bottom of Funnel): Decision-stage content, product-specific and ROI-focused
    """
    try:
        # Get organization ID for multi-tenant isolation
        org_id = get_org_id_from_user(current_user)
        
        logger.info(f"Generating Gypsum-enhanced prompts for org {org_id}")
        
        # Initialize enhanced prompt generator (without Gypsum client for now)
        prompt_generator = GypsumEnhancedPromptGenerator(db, gypsum_client=None)
        
        # Generate enhanced prompts
        response = await prompt_generator.generate_prompts(org_id, request)
        
        logger.info(f"Generated {len(response.prompts)} Gypsum-enhanced prompts for org {org_id}")
        
        return response
        
    except Exception as e:
        logger.error(f"Failed to generate Gypsum-enhanced prompts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate enhanced prompts: {str(e)}"
        )

@prompt_router.get("/sample", response_model=PromptGenerationResponse)
async def get_sample_prompts(
    business_type: Optional[str] = None,
    persona_role: Optional[str] = None,
    funnel_stage: Optional[FunnelStage] = None,
    current_user: AuthUser = Depends(get_current_user_with_org)
):
    """
    Get sample prompts showing Gypsum persona integration capabilities.
    
    Optionally specify a funnel_stage to see how prompts are tailored for different stages:
    - tofu: Awareness-stage educational content
    - mofu: Consideration-stage solution-focused content  
    - bofu: Decision-stage implementation and ROI content
    """
    try:
        # Create sample content analysis
        sample_content = {
            'primary_value_propositions': ['Streamline code signing workflows', 'Ensure security compliance'],
            'key_features': ['Certificate management', 'CI/CD integration', 'Automated signing'],
            'problems_addressed': ['Manual signing processes', 'Security vulnerabilities', 'Compliance challenges'],
            'competitive_advantages': ['Enterprise-grade security', 'Seamless integration', 'Audit trail'],
            'industry_positioning': {'primary_industry': 'Software Development'},
            'emotional_triggers': ['security confidence', 'development efficiency'],
            'messaging_themes': ['security-first development', 'automated compliance']
        }
        
        # Create sample persona
        sample_persona = {
            'role': persona_role or 'DevOps Engineer',
            'industry': 'Software Development',
            'pain_points': ['Manual certificate management', 'Compliance overhead', 'Security vulnerabilities'],
            'goals': ['Automate workflows', 'Ensure security', 'Reduce manual work'],
            'company_size': 'Enterprise'
        }
        
        # Generate sample prompts
        prompt_generator = GypsumEnhancedPromptGenerator(None)
        
        sample_request = PromptGenerationRequest(
            max_prompts=1, 
            persona_id="sample_persona",
            funnel_stage=funnel_stage
        )
        
        # Create enhanced prompts using sample data with funnel awareness
        enhanced_prompts = prompt_generator._create_template_prompts(
            {'messaging': sample_content, 'positioning': {'target_market': 'Software Development Teams'}},
            sample_persona,
            funnel_stage,
            1
        )
        
        return PromptGenerationResponse(
            prompts=enhanced_prompts,
            content_summary={
                'business_type': sample_content['industry_positioning']['primary_industry'],
                'value_propositions': sample_content['primary_value_propositions'],
                'key_features': sample_content['key_features'],
                'problems_addressed': sample_content['problems_addressed'],
                'competitive_advantages': sample_content['competitive_advantages']
            },
            persona_context={
                'persona_id': 'sample_persona',
                'role': sample_persona['role'],
                'industry': sample_persona['industry'],
                'pain_points': sample_persona['pain_points'],
                'goals': sample_persona['goals'],
                'company_size': sample_persona['company_size']
            },
            messaging_insights={
                'framework_included': True,
                'messaging_elements': {
                    'value_propositions': sample_content['primary_value_propositions'],
                    'emotional_triggers': sample_content['emotional_triggers'],
                    'messaging_themes': sample_content['messaging_themes']
                },
                'confidence_score': 0.8
            },
            metadata={
                'generated_at': datetime.now().isoformat(),
                'analysis_successful': True,
                'persona_integrated': True,
                'prompt_count': len(enhanced_prompts),
                'sample_data': True
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to generate sample enhanced prompts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate sample enhanced prompts: {str(e)}"
        )

@prompt_router.get("/health")
async def prompt_generation_health():
    """Health check for enhanced prompt generation service"""
    return {
        "status": "healthy",
        "service": "gypsum_enhanced_prompt_generation",
        "timestamp": datetime.now().isoformat(),
        "features": [
            "voiceforge_content_analysis",
            "gypsum_persona_integration",
            "messaging_framework_support",
            "business_type_detection", 
            "persona_targeted_prompts",
            "funnel_stage_awareness",
            "tofu_mofu_bofu_prompts",
            "confidence_scoring",
            "multi_platform_support",
            "content_driven_ai_integration"
        ]
    }
