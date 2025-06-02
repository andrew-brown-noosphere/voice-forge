#!/bin/bash

echo "📦 Installing Celery Dependencies for VoiceForge"
echo "=============================================="

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

echo
echo "🔍 Checking current installations..."

# Check what's already installed
python -c "
import sys
packages = ['celery', 'redis', 'flower']
missing = []

for package in packages:
    try:
        __import__(package)
        print(f'✅ {package} is installed')
    except ImportError:
        print(f'❌ {package} is missing')
        missing.append(package)

if missing:
    print(f'\\n📦 Need to install: {', '.join(missing)}')
else:
    print('\\n🎉 All packages are already installed!')
"

echo
echo "📦 Installing/Updating Celery packages..."

# Install specific versions that work well together
pip install celery==5.3.0 redis==4.5.0 flower==1.2.0

echo
echo "🧪 Testing installations..."

# Test each package
python -c "
import celery
print(f'✅ Celery version: {celery.__version__}')
"

python -c "
import redis
print(f'✅ Redis client version: {redis.__version__}')
"

python -c "
try:
    import flower
    print('✅ Flower is installed')
except ImportError:
    print('❌ Flower installation failed')
"

echo
echo "🔧 Testing Celery app import..."
python -c "
try:
    from celery_app import celery_app
    print('✅ Celery app imports successfully')
    print(f'   Broker: {celery_app.conf.broker_url}')
    print(f'   Backend: {celery_app.conf.result_backend}')
except Exception as e:
    print(f'❌ Celery app import failed: {e}')
"

echo
echo "✅ Installation complete!"
echo
echo "📋 Next steps:"
echo "1. Start Redis: ./start_redis.sh"
echo "2. Start worker: ./start_worker.sh"
echo "3. Test setup: python test_celery.py"
