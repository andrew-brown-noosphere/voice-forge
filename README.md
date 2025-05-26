# VoiceForge

VoiceForge is a website crawling and content processing system designed to analyze company websites to create bespoke language models that can generate content in a company's unique voice and positioning.

## Overview

VoiceForge analyzes company websites to extract and process content, which can then be used with Retrieval-Augmented Generation (RAG) to generate content matching the company's voice and brand. The system is built with a Python backend and React frontend.

This project is structured as a full-stack application with the following components:

### Backend Features
- **Website Crawler Infrastructure**: A robust crawler that can recursively scan websites, respecting robots.txt and implementing rate limiting
- **Content Extraction & Processing**: Intelligent extraction of meaningful content from websites
- **Content Database**: Efficient storage of crawled website content
- **Vector Embedding & Similarity Search**: Advanced semantic search capabilities using embeddings
- **Retrieval-Augmented Generation (RAG)**: Generate brand-aligned content using retrieved context
- **Multi-Platform Content Templates**: Pre-configured templates for different social platforms and tones

### Frontend Features
- **Admin Dashboard**: Monitor and manage crawl jobs
- **Content Search**: Search and view extracted content
- **Content Generation**: Generate brand-aligned content for different platforms
- **Template Management**: Create and edit marketing templates
- **Configuration Interface**: Customize crawler settings

## Tech Stack

### Backend
- **Language**: Python
- **Framework**: FastAPI
- **Database**: PostgreSQL with pgvector extension
- **Web Scraping**: Playwright for JavaScript rendering
- **NLP**: SpaCy, scikit-learn, sentence-transformers
- **RAG**: Custom implementation with embedding retrieval and templating
- **Container**: Docker

### Frontend
- **Framework**: React
- **UI Library**: Material UI
- **State Management**: React Hooks
- **Routing**: React Router
- **API Client**: Axios
- **Build Tool**: Vite

## Installation & Setup

### Prerequisites
- Docker and Docker Compose
- Node.js 16+ (for local development)
- Python 3.9+ (for local development)

### Using Docker Compose (Recommended)
1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/voice-forge.git
   cd voice-forge
   ```

2. Start the services
   ```bash
   docker-compose up -d
   ```

3. Access the application
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Manual Setup

#### Backend
1. Navigate to the backend directory
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment
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
   playwright install chromium
   ```

5. Set up PostgreSQL with pgvector extension
   - Create a database named "voiceforge"
   - Create a user "postgres" with password "postgres" (or modify .env file)
   - Install pgvector extension in the database

6. Run migrations
   ```bash
   alembic upgrade head
   ```

7. Create initial marketing templates
   ```bash
   python scripts/create_templates.py
   ```

8. Start the API server
   ```bash
   uvicorn api.main:app --reload
   ```

#### Frontend
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

## Usage

1. Access the application at http://localhost:3000
2. Go to the "New Crawl" page and enter a domain URL to start crawling
3. Monitor the crawl progress on the dashboard
4. Once content is extracted, use the Content Search page to explore and analyze the content
5. Process content for RAG using the API or scripts
6. Generate brand-aligned content using the RAG system with different templates and tones

## RAG System

The VoiceForge RAG system provides the following capabilities:

1. **Content Chunking**: Split content into semantic chunks for more precise retrieval
2. **Vector Embedding**: Generate embeddings for content using state-of-the-art models
3. **Semantic Search**: Retrieve the most relevant content chunks based on query similarity
4. **Template-based Generation**: Generate content using retrieved context and platform-specific templates
5. **Multi-platform Support**: Generate content for different platforms (Twitter, LinkedIn, Email, Instagram, etc.)
6. **Tone Customization**: Choose from various tones (professional, casual, enthusiastic, etc.)

### RAG API Endpoints

- **POST /rag/chunks/search**: Search for relevant content chunks
- **GET /rag/content/{content_id}/chunks**: Get all chunks for a specific content piece
- **POST /rag/process/{content_id}**: Process content for RAG
- **POST /rag/generate**: Generate content using RAG
- **POST /templates**: Create a new marketing template
- **GET /templates/{template_id}**: Get a specific template by ID
- **POST /templates/search**: Search for templates with filters

## Project Structure

```
voice-forge/
├── backend/                     # Python backend application
│   ├── api/                     # API endpoints and models
│   ├── crawler/                 # Website crawler implementation
│   ├── processor/               # Content processing and analysis
│   │   ├── chunker.py           # Content chunking for RAG
│   │   ├── rag.py               # RAG system implementation
│   │   └── rag_service.py       # RAG service layer
│   ├── database/                # Database models and access
│   ├── scripts/                 # Utility scripts
│   ├── requirements.txt         # Python dependencies
│   └── Dockerfile               # Backend Docker configuration
├── frontend/                    # React frontend application
│   ├── public/                  # Static assets
│   ├── src/                     # React source code
│   │   ├── components/          # Reusable UI components
│   │   ├── pages/               # Application pages
│   │   └── services/            # API services
│   ├── package.json             # Frontend dependencies
│   └── Dockerfile               # Frontend Docker configuration
├── docker-compose.yml           # Docker Compose configuration
└── README.md                    # Project documentation
```

## Future Development
- Advanced scoring and ranking for retrieved content
- Integration with commercial language models for enhanced generation
- Multi-lingual support for content processing and generation
- A/B testing of different content versions
- Content performance analytics and reporting

## License
This project is proprietary and not licensed for public use.

## Acknowledgements
This project was built using various open-source libraries and frameworks. We thank the community for their contributions.
