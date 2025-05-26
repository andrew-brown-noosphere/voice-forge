# VoiceForge RAG Setup Guide

This guide will help you set up VoiceForge with Pinecone for powerful Retrieval-Augmented Generation (RAG).

## Prerequisites

Before beginning, make sure you have:

1. A Pinecone account and API key
2. PostgreSQL installed and running
3. Python 3.9+ installed

## Step 1: Configure Environment Variables

Edit the `.env` file in the `backend` directory:

```
# Replace these with your actual credentials
PINECONE_API_KEY=your_actual_api_key_here
PINECONE_ENVIRONMENT=gcp-starter  # Change if needed
PINECONE_INDEX_NAME=voiceforge-rag
```

## Step 2: Run the Setup Script

```bash
cd backend
python scripts/setup.py
```

This script will:
- Install all dependencies
- Run database migrations
- Test the Pinecone connection
- Create sample marketing templates

## Step 3: Start the Backend Server

```bash
cd backend
uvicorn api.main:app --reload
```

## Step 4: Start the Frontend Server

```bash
cd frontend
npm install
npm run dev
```

## Step 5: Use the System

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

## System Workflow

1. **Crawl Websites**: Extract content from company websites
2. **Process Content**: Split content into chunks and generate embeddings
3. **Store in Pinecone**: Save chunks and embeddings in the vector database
4. **Generate Content**: Create brand-aligned content using RAG

## Troubleshooting

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
- Check that you're running Python 3.9+

## Next Steps

After getting the basic RAG system working with Pinecone, you can:

1. Add LLM integration for more sophisticated content generation
2. Customize templates for different platforms and tones
3. Implement user authentication and multi-tenancy
4. Add analytics to track content performance

## Support

If you encounter any issues, please check the logs in the backend and frontend consoles for error messages.
