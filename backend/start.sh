#!/bin/bash
# VoiceForge - One Simple Startup Script

echo "🚀 Starting VoiceForge..."

# Check if we're in the right directory
if [ ! -f "celery_app.py" ]; then
    echo "❌ Please run this from the backend directory"
    exit 1
fi

# Start Redis if not running
if ! redis-cli ping > /dev/null 2>&1; then
    echo "📡 Starting Redis..."
    redis-server --daemonize yes
fi

# Function to cleanup on exit
cleanup() {
    echo "🛑 Stopping services..."
    pkill -f "celery.*worker" 2>/dev/null
    jobs -p | xargs kill 2>/dev/null
    exit 0
}
trap cleanup SIGINT SIGTERM

echo "⚙️ Starting Celery workers..."
# Start all Celery workers in background with MPS disabled
export PYTORCH_ENABLE_MPS_FALLBACK=1
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
export MPS_DISABLE=1
celery -A celery_app worker --loglevel=info --concurrency=1 --pool=solo --queues=crawl,process,rag,signals --detach --pidfile=/tmp/celery.pid --logfile=/tmp/celery.log

echo "🌐 Starting API server at http://localhost:8000"
echo "Press Ctrl+C to stop all services"
echo "=================================="

# Start FastAPI server (foreground)
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
