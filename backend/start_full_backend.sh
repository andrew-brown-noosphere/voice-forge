#!/bin/bash
"""
Complete VoiceForge Backend Startup
Starts both the API server and Celery workers
"""

echo "🚀 VOICEFORGE COMPLETE BACKEND STARTUP"
echo "======================================"

# Navigate to backend directory
cd /Users/andrewbrown/Sites/noosphere/github/voice-forge/backend

# Activate virtual environment
echo "📦 Activating virtual environment..."
if [ -d "venv-py311" ]; then
    source venv-py311/bin/activate
else
    echo "❌ Virtual environment not found at venv-py311"
    exit 1
fi

# Set Python path
export PYTHONPATH=/Users/andrewbrown/Sites/noosphere/github/voice-forge/backend

# Load environment variables
echo "🔧 Loading environment variables..."
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check if Redis is running
echo "🔍 Checking Redis..."
if ! redis-cli ping > /dev/null 2>&1; then
    echo "⚠️  Redis not running. Starting Redis..."
    brew services start redis
    sleep 2
    
    # Check again
    if ! redis-cli ping > /dev/null 2>&1; then
        echo "❌ Failed to start Redis. Please run: brew install redis && brew services start redis"
        exit 1
    fi
fi
echo "✅ Redis is running"

# Test Celery app import
echo "🔍 Testing Celery configuration..."
python -c "
try:
    from celery_app import celery_app
    print('✅ Celery app imported successfully')
    registered_tasks = [t for t in celery_app.tasks.keys() if 'crawl' in t]
    print(f'✅ Found {len(registered_tasks)} crawl tasks')
except Exception as e:
    print(f'❌ Celery setup failed: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Celery setup failed. Exiting."
    exit 1
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down VoiceForge Backend..."
    echo "Stopping all background processes..."
    jobs -p | xargs kill 2>/dev/null
    exit 0
}

# Set trap to cleanup on Ctrl+C
trap cleanup SIGINT SIGTERM

echo ""
echo "🌐 Starting FastAPI server..."
echo "🔄 Starting Celery workers..."
echo ""
echo "📋 Services starting:"
echo "   • API Server: http://localhost:8000"
echo "   • Celery Workers: 2 workers (crawl, process, rag queues)"
echo "   • Redis: Background task queue"
echo ""
echo "Press Ctrl+C to stop all services"
echo "======================================"

# Start Celery worker in background
celery -A celery_app worker --loglevel=info --concurrency=2 --queues=crawl,process,rag &
CELERY_PID=$!

# Wait a moment for worker to start
sleep 3

# Start FastAPI server in foreground
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000 &
API_PID=$!

# Wait for both processes
wait $API_PID $CELERY_PID
