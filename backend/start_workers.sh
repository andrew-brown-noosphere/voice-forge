#!/bin/bash

# VoiceForge Celery Worker Startup Script

echo "🚀 Starting VoiceForge Celery Workers"

# Check if Redis is running
echo "🔍 Checking Redis connection..."
if ! redis-cli ping > /dev/null 2>&1; then
    echo "❌ Redis is not running. Please start Redis first:"
    echo "   Option 1: docker-compose up -d redis"
    echo "   Option 2: brew services start redis (macOS)"
    echo "   Option 3: sudo systemctl start redis (Linux)"
    exit 1
fi

echo "✅ Redis is running"

# Set environment variables
export CELERY_BROKER_URL="redis://localhost:6379/0"
export CELERY_RESULT_BACKEND="redis://localhost:6379/0"

# Start workers in the background
echo "🔄 Starting Celery workers..."

# Worker for crawling tasks
echo "Starting crawl worker..."
celery -A celery_app worker --loglevel=info --queues=crawl --concurrency=2 --hostname=crawl-worker@%h &
CRAWL_PID=$!

# Worker for processing tasks  
echo "Starting process worker..."
celery -A celery_app worker --loglevel=info --queues=process --concurrency=3 --hostname=process-worker@%h &
PROCESS_PID=$!

# Worker for RAG tasks
echo "Starting RAG worker..."
celery -A celery_app worker --loglevel=info --queues=rag --concurrency=2 --hostname=rag-worker@%h &
RAG_PID=$!

# General worker for default queue
echo "Starting general worker..."
celery -A celery_app worker --loglevel=info --queues=celery --concurrency=2 --hostname=general-worker@%h &
GENERAL_PID=$!

echo ""
echo "✅ All Celery workers started!"
echo "📊 Monitor workers at: http://localhost:5555 (if Flower is running)"
echo ""
echo "Worker PIDs:"
echo "  Crawl worker: $CRAWL_PID"
echo "  Process worker: $PROCESS_PID" 
echo "  RAG worker: $RAG_PID"
echo "  General worker: $GENERAL_PID"
echo ""
echo "To stop workers: kill $CRAWL_PID $PROCESS_PID $RAG_PID $GENERAL_PID"
echo "Or use: pkill -f celery"

# Wait for all workers
wait