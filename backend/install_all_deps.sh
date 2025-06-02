#!/bin/bash

echo "📦 Installing ALL VoiceForge Dependencies (Python 3.11)"
echo "===================================================="

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Prioritize venv-py311 since that's what the user is using
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

# Show Python version
echo "🐍 Python version: $(python --version)"
echo "📍 Virtual env: $VIRTUAL_ENV"

echo
echo "🔍 Checking requirements.txt..."
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found"
    exit 1
fi

echo "✅ Found requirements.txt"
echo
echo "📦 Installing all dependencies..."
echo "⏳ This may take a few minutes (especially PyTorch and Transformers)..."

# Upgrade pip first
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ All dependencies installed successfully"
else
    echo "❌ Some dependencies failed to install"
    echo "💡 You may need to install system dependencies first"
fi

echo
echo "🎭 Installing Playwright browsers..."
playwright install

echo
echo "🧪 Testing key imports..."

# Test critical imports
python -c "
import sys
print(f'Python version: {sys.version}')
print(f'Virtual env: {sys.prefix}')
print()

test_imports = [
    ('playwright', 'Playwright'),
    ('celery', 'Celery'),
    ('redis', 'Redis'),
    ('fastapi', 'FastAPI'), 
    ('sqlalchemy', 'SQLAlchemy'),
    ('psycopg2', 'PostgreSQL driver'),
    ('transformers', 'Transformers'),
    ('sentence_transformers', 'Sentence Transformers'),
    ('torch', 'PyTorch'),
    ('sklearn', 'Scikit-learn'),
    ('spacy', 'spaCy'),
    ('nltk', 'NLTK'),
]

failed = []
for module, name in test_imports:
    try:
        __import__(module)
        print(f'✅ {name}')
    except ImportError as e:
        print(f'❌ {name}: {e}')
        failed.append(name)

if failed:
    print(f'\\n⚠️  Failed imports: {len(failed)} out of {len(test_imports)}')
    print('💡 Some packages may need system dependencies or take time to install')
else:
    print('\\n🎉 All critical packages imported successfully!')
"

echo
echo "🔧 Testing Celery app configuration..."
python -c "
try:
    from celery_app import celery_app
    print('✅ Celery app configuration valid')
    print(f'   Broker: {celery_app.conf.broker_url}')
    print(f'   Backend: {celery_app.conf.result_backend}')
except Exception as e:
    print(f'❌ Celery app configuration error: {e}')
"

echo
echo "🧪 Testing specific VoiceForge imports..."
python -c "
try:
    from database.session import get_db_session
    print('✅ Database session import OK')
except Exception as e:
    print(f'❌ Database session import failed: {e}')

try:
    from api.models import CrawlConfig
    print('✅ API models import OK')
except Exception as e:
    print(f'❌ API models import failed: {e}')
"

echo
echo "✅ Installation complete!"
echo
echo "📋 Next steps:"
echo "1. Make sure Redis is running: ./start_redis.sh"
echo "2. Start Celery worker: ./start_worker.sh"
echo "3. Start API server: uvicorn api.main:app --reload"
echo "4. Test everything: python test_celery.py"
echo
echo "💡 Using venv-py311 (Python 3.11) environment"
