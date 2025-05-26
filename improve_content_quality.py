#!/usr/bin/env python3
"""
Content Quality Improvements for VoiceForge
Additional options to enhance AI-generated content quality
"""

import os
import sys

# Load environment
def load_env_file():
    backend_path = '/Users/andrewbrown/Sites/noosphere/github/voice-forge/backend'
    env_path = os.path.join(backend_path, '.env')
    
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env_file()

def show_improvement_options():
    """Show different ways to improve content quality"""
    print("🎯 Content Quality Improvement Options")
    print("=" * 40)
    
    print("\n1️⃣ **IMMEDIATE IMPROVEMENTS** (Already implemented):")
    print("   ✅ Better prompting with copywriter persona")
    print("   ✅ Upgraded to GPT-4o-mini (better quality)")
    print("   ✅ Higher creativity settings (temperature=0.8)")
    print("   ✅ Reduced repetition (frequency_penalty)")
    print("   ✅ Focus on benefits over features")
    
    print("\n2️⃣ **NEXT LEVEL UPGRADES**:")
    print("   🔹 GPT-4 (premium model) - $0.03/1k tokens vs $0.0005")
    print("   🔹 Custom writing examples for each platform")
    print("   🔹 A/B testing different prompts")
    print("   🔹 Brand voice training")
    print("   🔹 Content post-processing")
    
    print("\n3️⃣ **BRAND VOICE CUSTOMIZATION**:")
    print("   🔹 Add company style guide to prompts")
    print("   🔹 Include example content that matches your brand")
    print("   🔹 Define specific tone characteristics")
    print("   🔹 Industry-specific terminology")
    
    print("\n4️⃣ **PLATFORM-SPECIFIC OPTIMIZATION**:")
    print("   🔹 Twitter: Hook + value + CTA + hashtags")
    print("   🔹 LinkedIn: Insight + story + professional CTA")
    print("   🔹 Blog: Strong headline + structure + SEO")
    print("   🔹 Email: Subject line + personalization + urgency")

def test_improved_generation():
    """Test the improved content generation"""
    print("\n🧪 Testing Improved Content Generation")
    print("=" * 38)
    
    # Add backend to path
    backend_path = '/Users/andrewbrown/Sites/noosphere/github/voice-forge/backend'
    sys.path.append(backend_path)
    
    try:
        from database.session import get_db_session
        from database.db import Database
        from processor.rag import RAGSystem
        
        session = get_db_session()
        db = Database(session)
        rag_system = RAGSystem(db)
        
        # Test different queries and platforms
        test_cases = [
            {
                "query": "create a tweet about secure code signing",
                "platform": "twitter",
                "tone": "professional"
            },
            {
                "query": "write a LinkedIn post about automated security",
                "platform": "linkedin", 
                "tone": "enthusiastic"
            },
            {
                "query": "create an email about software development security",
                "platform": "email",
                "tone": "friendly"
            }
        ]
        
        for i, test in enumerate(test_cases, 1):
            print(f"\n📝 Test {i}: {test['platform'].title()} - {test['tone'].title()}")
            print(f"   Query: {test['query']}")
            
            response = rag_system.process_and_generate(
                query=test['query'],
                platform=test['platform'],
                tone=test['tone']
            )
            
            print(f"   Generated ({len(response['text'])} chars):")
            print(f"   {response['text'][:200]}...")
            
            # Show model used
            metadata = response.get('metadata', {})
            model = metadata.get('model_used', 'unknown')
            print(f"   Model: {model}")
        
        session.close()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

def upgrade_to_gpt4():
    """Show how to upgrade to GPT-4 for even better quality"""
    print("\n🚀 Upgrade to GPT-4 (Premium Quality)")
    print("=" * 35)
    
    print("💰 Cost Comparison:")
    print("   GPT-4o-mini: $0.0005/1k tokens (~$0.002 per generation)")
    print("   GPT-4:       $0.03/1k tokens   (~$0.05 per generation)")
    print("   GPT-4o:      $0.005/1k tokens  (~$0.01 per generation)")
    
    print("\n📈 Quality Improvement:")
    print("   ✅ More sophisticated language")
    print("   ✅ Better understanding of nuance")
    print("   ✅ More creative and engaging content")
    print("   ✅ Better adherence to complex instructions")
    
    print("\n🔧 To upgrade to GPT-4:")
    print("   Edit: backend/processor/ai_content_generator.py")
    print("   Change: model=\"gpt-4o-mini\"")
    print("   To:     model=\"gpt-4o\" or model=\"gpt-4\"")

def main():
    print("🎨 VoiceForge Content Quality Upgrade")
    print("=" * 37)
    
    show_improvement_options()
    
    print("\n" + "="*50)
    print("🔄 RESTART YOUR BACKEND to use the improvements:")
    print("   cd backend")
    print("   source venv-py311/bin/activate") 
    print("   python -m uvicorn api.main:app --reload")
    print("="*50)
    
    test_improved_generation()
    upgrade_to_gpt4()
    
    print("\n🎯 Next Steps:")
    print("   1. Restart backend to load improvements")
    print("   2. Test different platforms and tones")
    print("   3. Consider upgrading to GPT-4 for premium quality")
    print("   4. Customize brand voice for your specific needs")

if __name__ == "__main__":
    main()
