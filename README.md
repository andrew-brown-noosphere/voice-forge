# VoiceForge

VoiceForge is a website crawling and content processing system designed to analyze company websites to create bespoke language models that can generate content in a company's unique voice and positioning.

## Overview

VoiceForge analyzes company websites to extract and process content, which can then be used to train language models that generate content matching the company's voice and brand. The system is built with a Python backend and React frontend.

This project is structured as a full-stack application with the following components:

### Backend Features
- **Website Crawler Infrastructure**: A robust crawler that can recursively scan websites, respecting robots.txt and implementing rate limiting
- **Content Extraction & Processing**: Intelligent extraction of meaningful content from websites
- **Content Database**: Efficient storage of crawled website content
- **Relevance Scoring System**: Text analysis to identify key topics and terms

### Frontend Features
- **Admin Dashboard**: Monitor and manage crawl jobs
- **Content Search**: Search and view extracted content
- **Configuration Interface**: Customize crawler settings

## Tech Stack

### Backend
- **Language**: Python
- **Framework**: FastAPI
- **Database**: PostgreSQL with pgvector extension
- **Web Scraping**: Playwright for JavaScript rendering
- **NLP**: SpaCy, scikit-learn, sentence-transformers
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

7. Start the API server
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

## Project Structure

```
voice-forge/
├── backend/                     # Python backend application
│   ├── api/                     # API endpoints and models
│   ├── crawler/                 # Website crawler implementation
│   ├── processor/               # Content processing and analysis
│   ├── database/                # Database models and access
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
- Integration with language models for content generation
- Advanced analytics and reporting
- Extensible plugin system for custom content processors
- Integration with content management systems

## License
This project is proprietary and not licensed for public use.

## Acknowledgements
This project was built using various open-source libraries and frameworks. We thank the community for their contributions.
