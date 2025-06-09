#!/bin/bash
# Stop all VoiceForge services

echo "🛑 Stopping VoiceForge Backend Services..."

# Stop Celery workers
echo "⚙️ Stopping Celery workers..."
if [ -f /tmp/celery_crawl.pid ]; then
    kill -TERM $(cat /tmp/celery_crawl.pid)
    rm /tmp/celery_crawl.pid
    echo "  ✅ Crawl worker stopped"
fi

if [ -f /tmp/celery_process.pid ]; then
    kill -TERM $(cat /tmp/celery_process.pid)
    rm /tmp/celery_process.pid
    echo "  ✅ Process worker stopped"
fi

if [ -f /tmp/celery_rag.pid ]; then
    kill -TERM $(cat /tmp/celery_rag.pid)
    rm /tmp/celery_rag.pid
    echo "  ✅ RAG worker stopped"
fi

if [ -f /tmp/celery_signals.pid ]; then
    kill -TERM $(cat /tmp/celery_signals.pid)
    rm /tmp/celery_signals.pid
    echo "  ✅ Signals worker stopped"
fi

# Stop any remaining celery processes
pkill -f "celery.*worker"

echo "🛑 All services stopped!"
