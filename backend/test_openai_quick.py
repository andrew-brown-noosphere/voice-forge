#!/usr/bin/env python3
"""
Quick test to verify OpenAI API key and quota
"""
import os
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_openai_key():
    """Test OpenAI API key and quota"""
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ No OPENAI_API_KEY found in environment")
        return False
    
    print(f"🔑 Found API key: {api_key[:20]}...")
    
    try:
        client = AsyncOpenAI(api_key=api_key)
        
        # Test with a very simple, low-token request
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",  # Cheaper model
            messages=[
                {"role": "user", "content": "Say hello"}
            ],
            max_tokens=10,
            temperature=0
        )
        
        print("✅ OpenAI API is working!")
        print(f"Response: {response.choices[0].message.content}")
        print(f"Usage: {response.usage}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API test failed: {e}")
        
        # Check if it's a quota issue
        if "quota" in str(e).lower() or "429" in str(e):
            print("💳 This appears to be a quota/billing issue.")
            print("📋 Please check:")
            print("   1. Your OpenAI account has available credits")
            print("   2. Your API key is from the correct account")
            print("   3. Your usage limits haven't been exceeded")
            print("   4. Try waiting a few minutes and test again")
        
        return False

if __name__ == "__main__":
    asyncio.run(test_openai_key())
