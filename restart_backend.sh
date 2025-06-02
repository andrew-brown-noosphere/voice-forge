#!/bin/bash

# VoiceForge Backend Quick Restart Script
echo "🚀 VoiceForge Backend Quick Restart"
echo "==================================="

# Navigate to backend directory
cd "$(dirname "$0")/backend" || {
    echo "❌ Could not find backend directory"
    exit 1
}

# Check if virtual environment exists
if [ ! -d "venv-py311" ]; then
    echo "❌ Virtual environment not found at venv-py311"
    echo "🔧 Create it with: python3.11 -m venv venv-py311"
    exit 1
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv-py311/bin/activate

# Check if required packages are installed
echo "📦 Checking dependencies..."
if ! python -c "import uvicorn, fastapi, psycopg2" 2>/dev/null; then
    echo "⚠️ Some dependencies missing, installing..."
    pip install -r requirements.txt
fi

# Kill any existing backend processes
echo "🛑 Stopping existing backend processes..."
pkill -f "uvicorn.*main:app" || true
sleep 2

# Start the backend
echo "🚀 Starting VoiceForge backend..."
echo "   URL: http://localhost:8000"
echo "   Press Ctrl+C to stop"
echo ""

python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
