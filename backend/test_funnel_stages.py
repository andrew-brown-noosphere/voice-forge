#!/usr/bin/env python3
"""
Test script for funnel stage functionality in prompt generation
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.prompt_generation import GypsumEnhancedPromptGenerator
from api.models import FunnelStage

async def test_funnel_stages():
    """Test funnel stage prompt generation"""
    
    # Initialize the prompt generator
    generator = GypsumEnhancedPromptGenerator(db=None)
    
    # Sample data
    sample_gypsum_data = {
        'messaging': {
            'headline_message': 'Build APIs 10x faster with enterprise-grade schema management',
            'elevator_pitch': 'Buf is the platform that makes Protobuf and gRPC accessible to any team while preventing API-related bugs and accelerating API development',
            'key_differentiators': [
                'Enterprise-grade schema management',
                'Prevents breaking changes',
                'Accelerates API development'
            ]
        },
        'positioning': {
            'target_market': 'Software development teams building and maintaining APIs'
        }
    }
    
    sample_persona = {
        'role': 'DevOps Engineer',
        'industry': 'Software Development',
        'pain_points': ['Manual certificate management', 'Compliance overhead', 'Security vulnerabilities'],
        'goals': ['Automate workflows', 'Ensure security', 'Reduce manual work'],
        'company_size': 'Enterprise'
    }
    
    print("🚀 Testing Funnel Stage Prompt Generation\n")
    
    # Test each funnel stage
    for stage in [FunnelStage.TOFU, FunnelStage.MOFU, FunnelStage.BOFU]:
        print(f"📍 Testing {stage.value.upper()} Stage:")
        print("=" * 50)
        
        try:
            prompts = generator._create_template_prompts(
                sample_gypsum_data,
                sample_persona,
                stage,
                3
            )
            
            for i, prompt in enumerate(prompts, 1):
                print(f"\n{i}. **{prompt.title}**")
                print(f"   Funnel Stage: {prompt.funnel_stage.value.upper()}")
                print(f"   Category: {prompt.category}")
                print(f"   Confidence: {prompt.confidence}")
                print(f"   Platform: {prompt.platform.value}")
                print(f"   Tone: {prompt.tone.value}")
                print(f"   Prompt Preview: {prompt.prompt[:150]}...")
                print(f"   Reasoning: {prompt.reasoning}")
            
        except Exception as e:
            print(f"❌ Error testing {stage.value.upper()}: {e}")
        
        print("\n" + "=" * 50)
        print()
    
    # Test funnel stage guidance
    print("📖 Testing Funnel Stage Guidance:\n")
    
    for stage in [FunnelStage.TOFU, FunnelStage.MOFU, FunnelStage.BOFU]:
        guidance = generator._get_funnel_stage_guidance(stage)
        print(f"**{stage.value.upper()} Guidance:**")
        print(guidance[:200] + "..." if len(guidance) > 200 else guidance)
        print()
    
    print("✅ Funnel stage testing complete!")

if __name__ == "__main__":
    asyncio.run(test_funnel_stages())
