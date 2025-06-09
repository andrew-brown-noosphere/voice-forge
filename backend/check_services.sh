#!/bin/bash
# Check status of all VoiceForge services

echo "📊 VoiceForge Services Status"
echo "=============================="

# Check Redis
echo "📡 Redis Status:"
if pgrep redis-server > /dev/null; then
    echo "  ✅ Redis is running"
else
    echo "  ❌ Redis is not running"
fi

# Check Celery workers
echo "⚙️ Celery Workers:"
celery -A celery_app status 2>/dev/null || echo "  ❌ No Celery workers running"

# Check backend server
echo "🌐 Backend Server:"
if lsof -i:8000 > /dev/null; then
    echo "  ✅ Backend server running on port 8000"
else
    echo "  ❌ Backend server not running on port 8000"
fi

# Show active signal sources (if any)
echo "🎯 Active Signal Sources:"
python -c "
try:
    from database.session import get_db_session
    from database.models import SignalSource
    db = get_db_session()
    sources = db.query(SignalSource).filter(SignalSource.is_active == True).all()
    if sources:
        for source in sources:
            print(f'  📍 {source.platform}: {source.source_name} ({source.crawl_frequency})')
    else:
        print('  📝 No active signal sources configured')
    db.close()
except Exception as e:
    print(f'  ❌ Could not check signal sources: {e}')
"
