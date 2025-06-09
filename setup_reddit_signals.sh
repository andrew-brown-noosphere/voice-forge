#!/bin/bash

# Reddit Signal Discovery Setup Script for VoiceForge
# This script sets up the Reddit signal discovery integration

echo "🚀 Setting up Reddit Signal Discovery for VoiceForge..."

# Check if we're in the correct directory
if [ ! -f "backend/api/main.py" ]; then
    echo "❌ Error: Please run this script from the voice-forge root directory"
    exit 1
fi

echo "📦 Installing required dependencies..."

# Install Reddit API dependencies
pip install praw pandas nltk scikit-learn

echo "🔧 Setting up environment variables..."

# Check if .env file exists in backend directory
if [ ! -f "backend/.env" ]; then
    echo "❌ Error: backend/.env file not found"
    echo "Please create backend/.env with your Reddit API credentials:"
    echo ""
    echo "REDDIT_CLIENT_ID=your_reddit_client_id"
    echo "REDDIT_CLIENT_SECRET=your_reddit_client_secret" 
    echo "REDDIT_USER_AGENT=VoiceForge Signal Discovery Bot v1.0"
    echo ""
    echo "Get your Reddit API credentials from: https://www.reddit.com/prefs/apps"
    exit 1
fi

# Check if Reddit credentials are in .env
if ! grep -q "REDDIT_CLIENT_ID" backend/.env; then
    echo "⚠️  Adding Reddit API credentials to .env..."
    echo "" >> backend/.env
    echo "# Reddit API Configuration" >> backend/.env
    echo "REDDIT_CLIENT_ID=your_reddit_client_id" >> backend/.env
    echo "REDDIT_CLIENT_SECRET=your_reddit_client_secret" >> backend/.env
    echo "REDDIT_USER_AGENT=VoiceForge Signal Discovery Bot v1.0" >> backend/.env
    echo ""
    echo "⚠️  Please update backend/.env with your actual Reddit API credentials"
    echo "Get them from: https://www.reddit.com/prefs/apps"
fi

echo "🗄️  Setting up database migrations..."

# Navigate to backend directory
cd backend

# Check if alembic is configured
if [ ! -f "alembic.ini" ]; then
    echo "⚠️  Alembic not configured. Please run database migrations manually."
else
    echo "Running database migrations for Reddit signals..."
    python -m alembic upgrade head 2>/dev/null || echo "⚠️  Please run migrations manually: python -m alembic upgrade head"
fi

echo "🧠 Downloading NLTK data..."
python -c "
import nltk
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True) 
    nltk.download('wordnet', quiet=True)
    print('✅ NLTK data downloaded successfully')
except Exception as e:
    print(f'⚠️  NLTK download failed: {e}')
"

echo ""
echo "✅ Reddit Signal Discovery setup complete!"
echo ""
echo "🔧 Next steps:"
echo "1. Update backend/.env with your Reddit API credentials"
echo "2. Run database migrations: cd backend && python -m alembic upgrade head"
echo "3. Start the backend server: cd backend && python -m uvicorn api.main:app --reload"
echo ""
echo "📡 New API endpoints available:"
echo "- POST /reddit-signals/discover - Discover Reddit signals"
echo "- POST /reddit-signals/generate-response - Generate AI responses"
echo "- GET /reddit-signals/signals - List discovered signals"
echo "- GET /reddit-signals/health - Health check"
echo ""
echo "🚀 Ready to discover Reddit signals and generate AI-powered responses!"
