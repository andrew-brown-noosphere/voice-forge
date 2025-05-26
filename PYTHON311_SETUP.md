# VoiceForge Setup with Python 3.11

This guide will help you set up VoiceForge with Python 3.11 to ensure optimal performance with neural embeddings.

## Prerequisites

Before beginning, make sure you have:

1. Python 3.11 installed
2. A Pinecone account and API key
3. PostgreSQL installed and running

## Step 1: Install Python 3.11

### macOS
```bash
brew install python@3.11
```

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev
```

### Windows
Download the installer from [python.org](https://www.python.org/downloads/release/python-3110/) and run it.

## Step 2: Create and Activate a Virtual Environment

```bash
# Navigate to the project directory
cd /Users/andrewbrown/Sites/noosphere/github/voice-forge

# Create a virtual environment
python3.11 -m venv venv-py311

# Activate the virtual environment
# On macOS/Linux:
source venv-py311/bin/activate
# On Windows:
# venv-py311\Scripts\activate
```

## Step 3: Configure Environment Variables

Edit the `.env` file in the `backend` directory:

```
# Replace these with your actual credentials
PINECONE_API_KEY=your_actual_api_key_here
PINECONE_ENVIRONMENT=gcp-starter  # Change if needed
PINECONE_INDEX_NAME=voiceforge-rag
```

## Step 4: Run the Setup Script

```bash
cd backend
python scripts/setup.py
```

This script will:
- Check that you're using Python 3.11
- Install all dependencies
- Run database migrations
- Test the Pinecone connection
- Create sample marketing templates

## Step 5: Start the Backend Server

```bash
# Make sure you're in the backend directory
cd backend
uvicorn api.main:app --reload
```

## Step 6: Start the Frontend Server

In a new terminal:

```bash
cd frontend
npm install  # First time only
npm run dev
```

## Step 7: Use the System

1. Open your browser and go to: `http://localhost:3000`
2. Create a new crawl to extract content from a website
3. Process the extracted content for RAG
4. Generate brand-aligned content using the RAG system

## Testing Pinecone Integration

To verify that Pinecone is working correctly:

```bash
cd backend
python scripts/test_pinecone.py
```

## Troubleshooting

### Python Version Issues

If you see errors related to PyTorch or sentence-transformers, make sure you're using Python 3.11:

```bash
python --version
```

### Pinecone Connection Issues

- Verify your API key and environment in the `.env` file
- Check that your Pinecone account is active
- Ensure you're using the correct environment name

### Database Errors

- Make sure PostgreSQL is running
- Check the `DATABASE_URL` in the `.env` file
- Run migrations manually: `alembic upgrade head`

### Import Errors

- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check that you're in the virtual environment: `which python` should point to your venv

## Next Steps

After getting the basic RAG system working with Pinecone, you can:

1. Add LLM integration for more sophisticated content generation
2. Customize templates for different platforms and tones
3. Implement user authentication and multi-tenancy
4. Add analytics to track content performance
