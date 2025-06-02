#!/bin/bash

# VoiceForge Backend Startup with Diagnostics
# This script will check everything needed to start the backend successfully

echo "🚀 VoiceForge Backend Startup Diagnostics"
echo "=========================================="

# Change to backend directory
cd /Users/andrewbrown/Sites/noosphere/github/voice-forge/backend

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're in the right directory
echo -e "${BLUE}📁 Current directory:${NC} $(pwd)"

# 1. Check if virtual environment exists
echo -e "\n${BLUE}1️⃣ Checking Python Virtual Environment...${NC}"
if [ -d "venv-py311" ]; then
    echo -e "${GREEN}✅ Virtual environment found: venv-py311${NC}"
    
    # Check Python version in venv
    source venv-py311/bin/activate
    PYTHON_VERSION=$(python --version 2>&1)
    echo -e "${GREEN}✅ Python version: $PYTHON_VERSION${NC}"
    
    # Check if main dependencies are installed
    echo -e "\n${BLUE}2️⃣ Checking Key Dependencies...${NC}"
    
    # FastAPI
    if python -c "import fastapi" 2>/dev/null; then
        FASTAPI_VERSION=$(python -c "import fastapi; print(fastapi.__version__)" 2>/dev/null)
        echo -e "${GREEN}✅ FastAPI installed: $FASTAPI_VERSION${NC}"
    else
        echo -e "${RED}❌ FastAPI not installed${NC}"
    fi
    
    # Uvicorn
    if python -c "import uvicorn" 2>/dev/null; then
        echo -e "${GREEN}✅ Uvicorn installed${NC}"
    else
        echo -e "${RED}❌ Uvicorn not installed${NC}"
    fi
    
    # SQLAlchemy
    if python -c "import sqlalchemy" 2>/dev/null; then
        SQLALCHEMY_VERSION=$(python -c "import sqlalchemy; print(sqlalchemy.__version__)" 2>/dev/null)
        echo -e "${GREEN}✅ SQLAlchemy installed: $SQLALCHEMY_VERSION${NC}"
    else
        echo -e "${RED}❌ SQLAlchemy not installed${NC}"
    fi
    
    # PostgreSQL driver
    if python -c "import psycopg2" 2>/dev/null; then
        echo -e "${GREEN}✅ PostgreSQL driver (psycopg2) installed${NC}"
    else
        echo -e "${RED}❌ PostgreSQL driver (psycopg2) not installed${NC}"
    fi
    
    # OpenAI
    if python -c "import openai" 2>/dev/null; then
        echo -e "${GREEN}✅ OpenAI library installed${NC}"
    else
        echo -e "${RED}❌ OpenAI library not installed${NC}"
    fi
    
else
    echo -e "${RED}❌ Virtual environment 'venv-py311' not found${NC}"
    echo -e "${YELLOW}⚠️  Creating virtual environment...${NC}"
    python3.11 -m venv venv-py311
    source venv-py311/bin/activate
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# 3. Check environment variables
echo -e "\n${BLUE}3️⃣ Checking Environment Variables...${NC}"

if [ -f ".env" ]; then
    echo -e "${GREEN}✅ .env file found${NC}"
    
    # Check for OpenAI API key
    if grep -q "OPENAI_API_KEY=" .env && [ -n "$(grep OPENAI_API_KEY= .env | cut -d'=' -f2)" ]; then
        echo -e "${GREEN}✅ OpenAI API key configured${NC}"
    else
        echo -e "${RED}❌ OpenAI API key missing or empty${NC}"
    fi
    
    # Check for database URL
    if grep -q "DATABASE_URL=" .env && [ -n "$(grep DATABASE_URL= .env | cut -d'=' -f2)" ]; then
        echo -e "${GREEN}✅ Database URL configured${NC}"
    else
        echo -e "${RED}❌ Database URL missing or empty${NC}"
    fi
    
    # Check for Clerk keys
    if grep -q "CLERK_SECRET_KEY=" .env && [ -n "$(grep CLERK_SECRET_KEY= .env | cut -d'=' -f2)" ]; then
        echo -e "${GREEN}✅ Clerk secret key configured${NC}"
    else
        echo -e "${RED}❌ Clerk secret key missing or empty${NC}"
    fi
    
else
    echo -e "${RED}❌ .env file not found${NC}"
fi

# 4. Check database connection
echo -e "\n${BLUE}4️⃣ Checking Database Connection...${NC}"
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()

try:
    import psycopg2
    from urllib.parse import urlparse
    
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print('❌ DATABASE_URL not found in environment')
        exit(1)
    
    # Parse the database URL
    parsed = urlparse(db_url)
    
    # Try to connect
    conn = psycopg2.connect(
        host=parsed.hostname or 'localhost',
        port=parsed.port or 5432,
        database=parsed.path[1:] if parsed.path else 'voice_forge',
        user=parsed.username,
        password=parsed.password
    )
    
    # Test the connection
    cursor = conn.cursor()
    cursor.execute('SELECT version();')
    version = cursor.fetchone()
    print('✅ Database connection successful')
    print(f'✅ PostgreSQL version: {version[0].split(\",\")[0]}')
    
    # Check for pgvector extension
    cursor.execute(\"SELECT * FROM pg_extension WHERE extname = 'vector';\")
    if cursor.fetchone():
        print('✅ pgvector extension is installed')
    else:
        print('⚠️  pgvector extension not found - may need to install')
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f'❌ Database connection failed: {e}')
" 2>/dev/null || echo -e "${RED}❌ Database connection check failed${NC}"

# 5. Check port availability
echo -e "\n${BLUE}5️⃣ Checking Port Availability...${NC}"
if lsof -ti:8000 > /dev/null 2>&1; then
    echo -e "${RED}❌ Port 8000 is already in use${NC}"
    echo -e "${YELLOW}⚠️  Process using port 8000:${NC}"
    lsof -i:8000
    echo -e "${YELLOW}⚠️  You may need to kill this process or use a different port${NC}"
else
    echo -e "${GREEN}✅ Port 8000 is available${NC}"
fi

# 6. Install missing dependencies if needed
echo -e "\n${BLUE}6️⃣ Installing/Updating Dependencies...${NC}"
echo -e "${YELLOW}⚠️  This may take a few minutes...${NC}"

# Ensure we're in the virtual environment
source venv-py311/bin/activate

# Upgrade pip first
pip install --upgrade pip > /dev/null 2>&1

# Install requirements
if pip install -r requirements.txt > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Dependencies installed successfully${NC}"
else
    echo -e "${RED}❌ Failed to install some dependencies${NC}"
    echo -e "${YELLOW}⚠️  Trying to install critical dependencies individually...${NC}"
    
    # Install critical packages one by one
    pip install fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv PyJWT httpx > /dev/null 2>&1
fi

# 7. Final startup
echo -e "\n${BLUE}7️⃣ Starting Backend Server...${NC}"
echo -e "${GREEN}✅ All checks complete! Starting uvicorn...${NC}"
echo -e "${YELLOW}⚠️  Watch for any error messages below:${NC}"
echo "================================================================"

# Set the PYTHONPATH
export PYTHONPATH=/Users/andrewbrown/Sites/noosphere/github/voice-forge/backend

# Start the server with detailed error reporting
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug
