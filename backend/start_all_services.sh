#!/bin/bash
# Auto-start all VoiceForge services including Celery workers

echo "🚀 Starting VoiceForge Backend Services..."

# Start Redis (required for Celery)
echo "📡 Starting Redis..."
redis-server --daemonize yes

# Start Celery workers for different queues
echo "⚙️ Starting Celery workers..."

# Crawl queue worker
celery -A celery_app worker --loglevel=info --queues=crawl --detach --pidfile=/tmp/celery_crawl.pid --logfile=/tmp/celery_crawl.log

# Process queue worker  
celery -A celery_app worker --loglevel=info --queues=process --detach --pidfile=/tmp/celery_process.pid --logfile=/tmp/celery_process.log

# RAG queue worker
celery -A celery_app worker --loglevel=info --queues=rag --detach --pidfile=/tmp/celery_rag.pid --logfile=/tmp/celery_rag.log

# Signals queue worker (NEW)
celery -A celery_app worker --loglevel=info --queues=signals --detach --pidfile=/tmp/celery_signals.pid --logfile=/tmp/celery_signals.log

# Start the main backend server
echo "🌐 Starting FastAPI backend..."
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

echo "✅ All services started!"
echo "📊 Check worker status: celery -A celery_app status"
echo "🛑 Stop workers: ./stop_services.sh"
