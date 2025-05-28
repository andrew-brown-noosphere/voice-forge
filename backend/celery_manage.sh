#!/bin/bash

# VoiceForge Celery Monitoring and Management Script

show_help() {
    echo "🔧 VoiceForge Celery Management"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  status     - Show worker status"
    echo "  start      - Start all workers"
    echo "  stop       - Stop all workers"
    echo "  restart    - Restart all workers"
    echo "  monitor    - Start Flower monitoring"
    echo "  health     - Run health check"
    echo "  purge      - Purge all queues"
    echo "  help       - Show this help"
}

check_redis() {
    if ! redis-cli ping > /dev/null 2>&1; then
        echo "❌ Redis is not running"
        return 1
    fi
    echo "✅ Redis is running"
    return 0
}

show_status() {
    echo "🔍 Checking Celery worker status..."
    
    if ! check_redis; then
        return 1
    fi
    
    # Check if workers are running
    WORKERS=$(ps aux | grep -v grep | grep "celery.*worker" | wc -l)
    echo "📊 Active workers: $WORKERS"
    
    # Show queue status
    echo ""
    echo "📋 Queue status:"
    celery -A celery_app inspect active 2>/dev/null || echo "No active tasks"
    
    echo ""
    echo "📈 Queue lengths:"
    redis-cli llen crawl 2>/dev/null && echo "  Crawl queue: $(redis-cli llen crawl)"
    redis-cli llen process 2>/dev/null && echo "  Process queue: $(redis-cli llen process)"
    redis-cli llen rag 2>/dev/null && echo "  RAG queue: $(redis-cli llen rag)"
}

start_workers() {
    echo "🚀 Starting Celery workers..."
    ./start_workers.sh
}

stop_workers() {
    echo "🛑 Stopping Celery workers..."
    pkill -f "celery.*worker"
    echo "✅ Workers stopped"
}

restart_workers() {
    echo "🔄 Restarting Celery workers..."
    stop_workers
    sleep 2
    start_workers
}

start_monitor() {
    echo "📊 Starting Flower monitoring..."
    
    if ! check_redis; then
        echo "Starting Redis first..."
        docker-compose up -d redis
        sleep 3
    fi
    
    echo "🌸 Flower will be available at: http://localhost:5555"
    celery -A celery_app flower --port=5555
}

run_health_check() {
    echo "🏥 Running Celery health check..."
    
    if ! check_redis; then
        return 1
    fi
    
    # Run health check task
    python3 -c "
from celery_app import celery_app
from crawler.tasks import health_check_task

print('Submitting health check task...')
result = health_check_task.delay()
print(f'Task ID: {result.id}')

try:
    # Wait for result with timeout
    health_result = result.get(timeout=30)
    print('✅ Health check passed:')
    print(f'   Status: {health_result[\"status\"]}')
    print(f'   Task ID: {health_result[\"task_id\"]}')
    print(f'   Timestamp: {health_result[\"timestamp\"]}')
except Exception as e:
    print(f'❌ Health check failed: {e}')
"
}

purge_queues() {
    echo "🧹 Purging all Celery queues..."
    
    read -p "Are you sure you want to purge all queues? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        celery -A celery_app purge -f
        echo "✅ All queues purged"
    else
        echo "❌ Purge cancelled"
    fi
}

# Main command handling
case "$1" in
    status)
        show_status
        ;;
    start)
        start_workers
        ;;
    stop)
        stop_workers
        ;;
    restart)
        restart_workers
        ;;
    monitor)
        start_monitor
        ;;
    health)
        run_health_check
        ;;
    purge)
        purge_queues
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "❓ Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac