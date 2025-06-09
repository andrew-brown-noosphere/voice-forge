#!/bin/bash
"""
Fixed Celery startup script for VoiceForge
"""

# Navigate to backend directory
cd /Users/andrewbrown/Sites/noosphere/github/voice-forge/backend

# Activate virtual environment if it exists
if [ -d "venv-py311" ]; then
    echo "🔄 Activating virtual environment..."
    source venv-py311/bin/activate
fi

# Set Python path to include current directory
export PYTHONPATH="/Users/andrewbrown/Sites/noosphere/github/voice-forge/backend:$PYTHONPATH"

# Check if Redis is running
echo "🔍 Checking Redis..."
if ! redis-cli ping > /dev/null 2>&1; then
    echo "⚠️  Redis not running. Starting Redis..."
    brew services start redis
    sleep 2
fi

# Test Celery app import
echo "🔍 Testing Celery app import..."
python -c "
try:
    from celery_app import celery_app
    print('✅ Celery app imported successfully')
    print(f'   Broker: {celery_app.conf.broker_url}')
    print(f'   Backend: {celery_app.conf.result_backend}')
    
    # Test task discovery
    registered_tasks = list(celery_app.tasks.keys())
    print(f'   Registered tasks: {len(registered_tasks)}')
    for task in registered_tasks:
        if 'crawl' in task:
            print(f'     📋 {task}')
            
except ImportError as e:
    print(f'❌ Import failed: {e}')
    exit(1)
except Exception as e:
    print(f'❌ Error: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🚀 Starting Celery worker..."
    echo "   Press Ctrl+C to stop"
    echo ""
    
    # Start worker with explicit app import
    celery -A celery_app worker --loglevel=info --concurrency=2 --queues=crawl,process,rag
else
    echo "❌ Celery setup failed. Check the error above."
    exit 1
fi
