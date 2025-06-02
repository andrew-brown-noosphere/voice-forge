#!/bin/bash

# Celery Installation and Worker Starter with dependency checks

echo "👷 VoiceForge Celery Worker Setup & Start"
echo "========================================"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Find and activate virtual environment (prioritize venv-py311)
if [ -d "venv-py311" ]; then
    source venv-py311/bin/activate
    echo "✅ Activated venv-py311 (Python 3.11)"
elif [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Activated venv"
else
    echo "❌ No virtual environment found"
    echo "💡 Create one with: python3.11 -m venv venv-py311"
    exit 1
fi

# Check if celery is installed
echo "🔍 Checking Celery installation..."
if ! command -v celery &> /dev/null; then
    echo "❌ Celery not found, installing required packages..."
    echo "📦 Installing: celery, redis, flower..."
    
    pip install celery redis flower
    
    if [ $? -eq 0 ]; then
        echo "✅ Packages installed successfully"
    else
        echo "❌ Failed to install packages"
        echo "💡 Try manually: pip install celery redis flower"
        exit 1
    fi
else
    echo "✅ Celery is installed"
fi

# Check Redis connection
echo "🔍 Checking Redis connection..."
python -c "
import redis
try:
    r = redis.Redis(host='localhost', port=6379, db=0)
    response = r.ping()
    print('✅ Redis connection successful')
except Exception as e:
    print(f'❌ Redis connection failed: {e}')
    print('💡 Start Redis with: redis-server')
    exit(1)
"

if [ $? -ne 0 ]; then
    exit 1
fi

# Test Celery app import
echo "🔍 Testing Celery app configuration..."
python -c "
try:
    from celery_app import celery_app
    print('✅ Celery app configuration valid')
except Exception as e:
    print(f'❌ Celery app configuration error: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

echo
echo "🚀 Starting Celery worker..."
echo "📋 Queues: crawl, process, rag"
echo "🔧 Concurrency: 4 processes"
echo "📊 Log level: info"
echo "📄 Log file: logs/celery_worker.log"
echo
echo "💡 Press Ctrl+C to stop the worker"
echo

# Start worker with detailed configuration
exec celery -A celery_app worker \
    --loglevel=info \
    --queues=crawl,process,rag \
    --concurrency=4 \
    --logfile=logs/celery_worker.log \
    --time-limit=3600 \
    --soft-time-limit=3000 \
    --max-tasks-per-child=1000
