# OpenAI API Setup Guide

## 1. Get Your OpenAI API Key

1. Go to [OpenAI's website](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to the API section
4. Create a new API key
5. Copy the key (it starts with `sk-`)

## 2. Set Up the API Key

### Option A: Environment Variable (Recommended)

**macOS/Linux:**
```bash
export OPENAI_API_KEY="sk-your-actual-api-key-here"
```

**Windows:**
```cmd
set OPENAI_API_KEY=sk-your-actual-api-key-here
```

### Option B: .env File (Development)

1. Edit the `.env` file in the backend directory:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

2. The .env file is already configured to be loaded automatically.

## 3. Test Your Setup

Run the test script to verify everything works:

```bash
cd /Users/andrewbrown/Sites/noosphere/github/voice-forge/backend
python scripts/test_openai.py
```

## 4. Usage in Code

The LLM service will automatically detect and use your API key:

```python
from processor.llm.llm_service import LLMService

# Initialize service
llm_service = LLMService()

# Generate content
response = llm_service.generate(
    prompt_type="rag_response",
    params={
        "query": "Your question here",
        "context": "Relevant context information"
    },
    provider="openai"
)

print(response['text'])
```

## 5. Integration with RAG

The enhanced RAG system can now use OpenAI for:
- Query reformulation (generating better search queries)
- Content generation (creating platform-specific content)
- Key point extraction
- Marketing analysis

## Security Notes

- Never commit your API key to version control
- The .env file is already in .gitignore
- Use environment variables in production
- Monitor your API usage on OpenAI's dashboard

## Troubleshooting

1. **"API key not found"** - Check that the environment variable is set correctly
2. **"Invalid API key"** - Verify the key is correct and hasn't been revoked
3. **"Rate limit exceeded"** - You've hit OpenAI's usage limits, wait or upgrade your plan
4. **"Import errors"** - Make sure all dependencies are installed: `pip install -r requirements.txt`
