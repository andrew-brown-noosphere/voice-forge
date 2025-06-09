#!/bin/bash
# Stop VoiceForge services

echo "🛑 Stopping VoiceForge services..."

# Stop Celery workers
if [ -f /tmp/celery.pid ]; then
    kill -TERM $(cat /tmp/celery.pid) 2>/dev/null
    rm /tmp/celery.pid
fi
pkill -f "celery.*worker" 2>/dev/null

# Stop any uvicorn processes
pkill -f "uvicorn.*api.main" 2>/dev/null

echo "✅ All services stopped"
