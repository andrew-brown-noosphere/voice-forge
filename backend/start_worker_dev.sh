#!/bin/bash

# Simple script to start a single Celery worker for development

echo "🚀 Starting VoiceForge Celery Worker (Development Mode)"

# Check if Redis is running
if ! redis-cli ping > /dev/null 2>&1; then
    echo "❌ Redis is not running. Starting with Docker..."
    docker-compose up -d redis
    sleep 3
fi

echo "✅ Redis is ready"

# Set environment variables
export CELERY_BROKER_URL="redis://localhost:6379/0"
export CELERY_RESULT_BACKEND="redis://localhost:6379/0"

# Start single worker that handles all queues
echo "🔄 Starting Celery worker for all queues..."
celery -A celery_app worker --loglevel=info --concurrency=4 --hostname=dev-worker@%h