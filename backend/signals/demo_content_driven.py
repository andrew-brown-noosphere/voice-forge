"""
Content-Driven Signal Discovery Integration Example

This example shows how the new content-driven approach works across all platforms:
1. Analyzes VoiceForge vectorized content
2. Uses Gypsum personas for targeting
3. Generates intelligent searches across Reddit, LinkedIn, GitHub, Twitter
"""

import asyncio
import json
from signals.content_driven_ai import ContentDrivenSignalAI

# Example usage of the content-driven signal intelligence
async def demo_content_driven_signals():
    \"\"\"Demonstrate the content-driven signal discovery approach\"\"\"
    
    # Initialize the content-driven AI service
    content_ai = ContentDrivenSignalAI(
        voiceforge_db=None,  # Your VoiceForge database connection
        gypsum_client=None   # Your Gypsum client
    )
    
    # Configuration
    org_id = "demo-org-123"
    persona_id = "tech-founder-001"
    platforms = ['reddit', 'linkedin', 'github', 'twitter']
    
    print("🚀 Starting Content-Driven Signal Discovery Demo...")
    print(f"   Organization: {org_id}")
    print(f"   Target Persona: {persona_id}")
    print(f"   Platforms: {', '.join(platforms)}")
    print()
    
    try:
        # Generate comprehensive content-driven strategy
        strategy = await content_ai.generate_content_driven_searches(
            org_id=org_id,
            selected_persona_id=persona_id,
            platforms=platforms,
            options={
                'max_queries_per_platform': 8,
                'analysis_depth': 'comprehensive',
                'include_competitive_analysis': True
            }
        )
        
        print("✅ Content-Driven Strategy Generated Successfully!")
        print()
        
        # Display content analysis insights
        content_analysis = strategy['content_analysis']
        print("📄 VoiceForge Content Analysis:")
        print(f"   Primary Value Props: {content_analysis.get('primary_value_propositions', [])}")
        print(f"   Key Features: {content_analysis.get('key_features', [])}")
        print(f"   Problems Addressed: {content_analysis.get('problems_addressed', [])}")
        print(f"   Industry: {content_analysis.get('industry_positioning', {}).get('primary_industry', 'Unknown')}")
        print()
        
        # Display persona insights
        persona = strategy['selected_persona']
        print("👤 Target Persona:")
        print(f"   Role: {persona.get('role', 'Unknown')}")
        print(f"   Industry: {persona.get('industry', 'Unknown')}")
        print(f"   Pain Points: {persona.get('pain_points', [])}")
        print(f"   Goals: {persona.get('goals', [])}")
        print()
        
        # Display platform-specific strategies
        print("🎯 Platform-Specific Strategies:")
        for platform, platform_strategy in strategy['platform_strategies'].items():
            print(f"\\n   {platform.upper()}:")
            
            if platform == 'reddit':
                sources = platform_strategy.get('recommended_sources', [])
                print(f"     Subreddits: {[s['name'] for s in sources[:5]]}")
            elif platform == 'linkedin':
                sources = platform_strategy.get('recommended_sources', {})
                print(f"     Hashtags: {sources.get('hashtags', [])[:5]}")
                print(f"     Companies: {sources.get('companies', [])[:3]}")
            elif platform == 'github':
                sources = platform_strategy.get('recommended_sources', {})
                print(f"     Repositories: {sources.get('repositories', [])[:3]}")
            elif platform == 'twitter':
                sources = platform_strategy.get('recommended_sources', {})
                print(f"     Hashtags: {sources.get('hashtags', [])[:5]}")
            
            queries = platform_strategy.get('search_queries', [])
            print(f"     Sample Queries:")
            for query in queries[:3]:
                print(f"       - {query.get('query', '')} ({query.get('type', '')})")
        
        # Display execution plan
        print("\\n📋 Execution Plan:")
        execution_plan = strategy['execution_plan']
        print(f"   Total Platforms: {execution_plan['total_platforms']}")
        print(f"   Total Queries: {execution_plan['total_queries']}")
        print(f"   Estimated Signals/Day: {execution_plan['estimated_signals_per_day']}")
        print(f"   Scan Frequency: {execution_plan['recommended_schedule']['scan_frequency']}")
        
        phases = execution_plan.get('execution_phases', [])
        print(f"   Execution Phases:")
        for phase in phases:
            print(f"     {phase['phase']} ({phase['priority']} priority) - {phase['estimated_duration']}")
        
        return strategy
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


# Example API integration
async def demo_api_integration():
    \"\"\"Demonstrate API endpoint integration\"\"\"
    
    print("\\n🔌 API Integration Examples:")
    print()
    
    # Example 1: Generate full strategy
    print("1. Generate Content-Driven Strategy:")
    print("   POST /api/signals/content-driven/strategy")
    api_request_1 = {
        "persona_id": "tech-founder-001",
        "platforms": ["reddit", "linkedin"],
        "options": {
            "analysis_depth": "comprehensive",
            "max_queries_per_platform": 10
        }
    }
    print(f"   Request: {json.dumps(api_request_1, indent=2)}")
    print()
    
    # Example 2: Preview platform strategy
    print("2. Preview Platform Strategy:")
    print("   GET /api/signals/content-driven/preview/reddit?persona_id=tech-founder-001")
    print()
    
    # Example 3: Validate requirements
    print("3. Validate Strategy Requirements:")
    print("   POST /api/signals/content-driven/validate")
    api_request_3 = {
        "persona_id": "tech-founder-001",
        "platforms": ["reddit", "linkedin", "github", "twitter"]
    }
    print(f"   Request: {json.dumps(api_request_3, indent=2)}")
    print()
    
    # Example 4: Get content analysis
    print("4. Get VoiceForge Content Analysis:")
    print("   GET /api/signals/content-driven/analysis")
    print()
    
    # Example 5: Platform capabilities
    print("5. Get Platform Capabilities:")
    print("   GET /api/signals/content-driven/capabilities")


# Example of signal discovery workflow
async def demo_signal_discovery_workflow():
    \"\"\"Demonstrate complete signal discovery workflow\"\"\"
    
    print("\\n🔄 Complete Signal Discovery Workflow:")
    print()
    
    workflow_steps = [
        {
            "step": 1,
            "title": "Content Analysis",
            "description": "Analyze VoiceForge vectorized content to understand product positioning",
            "endpoint": "GET /api/signals/content-driven/analysis",
            "output": "Product understanding, value props, problems addressed"
        },
        {
            "step": 2,
            "title": "Persona Selection",
            "description": "Select target persona from Gypsum",
            "endpoint": "GET /api/gypsum/personas",
            "output": "Target audience characteristics, pain points, goals"
        },
        {
            "step": 3,
            "title": "Strategy Generation",
            "description": "Generate intelligent search strategy across platforms",
            "endpoint": "POST /api/signals/content-driven/strategy",
            "output": "Platform-specific queries, sources, targeting criteria"
        },
        {
            "step": 4,
            "title": "Signal Discovery",
            "description": "Execute searches across Reddit, LinkedIn, GitHub, Twitter",
            "endpoint": "POST /api/signals/discover",
            "output": "Relevant signals, discussions, engagement opportunities"
        },
        {
            "step": 5,
            "title": "Content Generation",
            "description": "Generate contextual responses using VoiceForge RAG",
            "endpoint": "POST /api/signals/generate-response",
            "output": "Personalized responses for each signal"
        },
        {
            "step": 6,
            "title": "Optimization",
            "description": "AI-powered optimization based on performance",
            "endpoint": "POST /api/signals/sources/{source_id}/optimize",
            "output": "Improved keywords, sources, targeting"
        }
    ]
    
    for step in workflow_steps:
        print(f"Step {step['step']}: {step['title']}")
        print(f"   Description: {step['description']}")
        print(f"   Endpoint: {step['endpoint']}")
        print(f"   Output: {step['output']}")
        print()


# Platform-specific examples
def demo_platform_examples():
    \"\"\"Show platform-specific signal discovery examples\"\"\"
    
    print("\\n🌐 Platform-Specific Examples:")
    print()
    
    platforms = {
        "Reddit": {
            "sources": ["r/startups", "r/SaaS", "r/entrepreneur"],
            "queries": [
                "API integration problems",
                "workflow automation tools",
                "business process optimization"
            ],
            "signal_types": ["question", "complaint", "feature_request"],
            "engagement": "Helpful expert responses in comments"
        },
        "LinkedIn": {
            "sources": ["#TechLeadership", "#StartupLife", "#ProductManagement"],
            "queries": [
                "Digital transformation challenges",
                "Productivity tools for teams",
                "API management solutions"
            ],
            "signal_types": ["professional_challenge", "industry_trend"],
            "engagement": "Thought leadership posts and professional insights"
        },
        "GitHub": {
            "sources": ["microsoft/vscode", "facebook/react", "nodejs/node"],
            "queries": [
                "API integration issues",
                "Workflow automation scripts",
                "Development tool requests"
            ],
            "signal_types": ["technical_issue", "feature_request"],
            "engagement": "Technical solutions and code contributions"
        },
        "Twitter": {
            "sources": ["#DevOps", "#TechStartup", "#APIFirst"],
            "queries": [
                "API integration pain points",
                "Developer productivity hacks",
                "Automation tool recommendations"
            ],
            "signal_types": ["realtime_problem", "trend_monitoring"],
            "engagement": "Quick helpful responses and resource sharing"
        }
    }
    
    for platform, details in platforms.items():
        print(f"{platform}:")
        print(f"   Sources: {', '.join(details['sources'])}")
        print(f"   Example Queries:")
        for query in details['queries']:
            print(f"     - {query}")
        print(f"   Signal Types: {', '.join(details['signal_types'])}")
        print(f"   Engagement Style: {details['engagement']}")
        print()


if __name__ == "__main__":
    \"\"\"Run the complete demo\"\"\"
    
    async def run_demo():
        print("=" * 80)
        print("CONTENT-DRIVEN SIGNAL DISCOVERY DEMO")
        print("=" * 80)
        
        # Run the main demo
        strategy = await demo_content_driven_signals()
        
        # Show API integration examples
        await demo_api_integration()
        
        # Show workflow
        await demo_signal_discovery_workflow()
        
        # Show platform examples
        demo_platform_examples()
        
        print("=" * 80)
        print("Demo completed! 🎉")
        print("\\nNext steps:")
        print("1. Configure VoiceForge content analysis")
        print("2. Set up Gypsum personas")
        print("3. Test Reddit signal discovery")
        print("4. Implement LinkedIn, GitHub, Twitter integrations")
        print("5. Set up automated optimization")
        print("=" * 80)
    
    # Run the demo
    asyncio.run(run_demo())
