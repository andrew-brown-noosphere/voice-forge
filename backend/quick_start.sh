#!/bin/bash

# Quick Backend Startup (Minimal Version)
echo "🚀 Starting VoiceForge Backend..."

cd /Users/andrewbrown/Sites/noosphere/github/voice-forge/backend

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv-py311/bin/activate

# Set Python path
export PYTHONPATH=/Users/andrewbrown/Sites/noosphere/github/voice-forge/backend

# Load environment variables
echo "🔧 Loading environment variables..."
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Start the server
echo "🌐 Starting uvicorn server on port 8000..."
echo "📝 Watch for startup messages and errors below:"
echo "================================================================"

python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
