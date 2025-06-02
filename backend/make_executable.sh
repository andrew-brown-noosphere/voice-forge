#!/bin/bash

# Make all Celery scripts executable

echo "🔧 Making Celery scripts executable..."
echo "===================================="

chmod +x start_redis.sh
chmod +x start_worker.sh  
chmod +x setup_celery.sh
chmod +x celery_quickstart.sh
chmod +x test_celery.py

echo "✅ Scripts are now executable:"
echo "   ./start_redis.sh"
echo "   ./start_worker.sh"
echo "   ./setup_celery.sh"
echo "   ./celery_quickstart.sh"
echo "   python test_celery.py"
echo
echo "🎯 Quick test: python test_celery.py"
