# VoiceForge: Website Crawling and Content Processing System

VoiceForge is a standalone service that analyzes company websites to create bespoke language models that can generate content in the company's unique voice and positioning. This service will eventually be integrated with a Reddit Scanner application via API.

## Project Structure

The project is divided into two main components:

### Backend (Python)
- Website crawler infrastructure
- Content extraction & processing
- Content database design & implementation
- Initial relevance scoring system

### Frontend (React)
- Admin dashboard for monitoring crawl progress
- Configuration interface for crawl parameters
- Content search and browsing capabilities

## Installation & Setup

### Backend
1. Navigate to the backend directory
```bash
cd backend
```

2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Install Playwright browsers
```bash
playwright install
```

5. Set up the database
```bash
alembic upgrade head
```

6. Start the backend server
```bash
uvicorn api.main:app --reload
```

### Frontend
1. Navigate to the frontend directory
```bash
cd frontend
```

2. Install dependencies
```bash
npm install
```

3. Start the development server
```bash
npm run dev
```

## Features

- Website crawling with respect for robots.txt and rate limiting
- Support for JavaScript-rendered content
- Intelligent content extraction from various website layouts
- Content categorization and metadata extraction
- PostgreSQL database with vector similarity capabilities
- RESTful API with OpenAPI/Swagger documentation
- Admin dashboard for monitoring and configuration
- Initial relevance scoring system

## Technical Architecture

- **Backend**: Python with FastAPI
- **Frontend**: React with TypeScript
- **Database**: PostgreSQL with pgvector extension
- **Deployment**: Docker containerization
- **Web Scraping**: Playwright for JavaScript rendering
- **Text Processing**: SpaCy, NLTK, and Transformers for NLP

## Development Status

This project is currently in Phase I, focusing on creating a solid foundation for website crawling, content extraction, and storage.