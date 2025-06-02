#!/bin/bash

echo "🔍 VoiceForge Environment Checker"
echo "================================"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📍 Current directory: $SCRIPT_DIR"
echo

# Check virtual environments
echo "🐍 Checking Virtual Environments:"
if [ -d "venv-py311" ]; then
    echo "   ✅ venv-py311 exists"
    echo "   📦 Packages in venv-py311:"
    venv-py311/bin/pip list | grep -E "(playwright|sqlalchemy|celery|redis|fastapi)" | head -10
else
    echo "   ❌ venv-py311 not found"
fi

if [ -d "venv" ]; then
    echo "   ✅ venv exists"
else
    echo "   ❌ venv not found"
fi

echo

# Check which virtual environment is active
echo "🔧 Current Environment:"
echo "   VIRTUAL_ENV: ${VIRTUAL_ENV:-Not set}"
echo "   Python executable: $(which python)"
echo "   Python version: $(python --version)"
echo "   Pip location: $(which pip)"

echo

# Test activating venv-py311
echo "🧪 Testing venv-py311 activation:"
if [ -d "venv-py311" ]; then
    source venv-py311/bin/activate
    echo "   ✅ Activated venv-py311"
    echo "   Python: $(which python)"
    echo "   Python version: $(python --version)"
    
    echo "   🔍 Checking key packages:"
    python -c "
import sys
packages = ['playwright', 'sqlalchemy', 'celery', 'redis', 'fastapi']
for pkg in packages:
    try:
        __import__(pkg)
        print(f'   ✅ {pkg}')
    except ImportError:
        print(f'   ❌ {pkg}')
"
else
    echo "   ❌ venv-py311 not found"
fi

echo

# Check if packages are in the right place
echo "📦 Package Installation Check:"
if [ -d "venv-py311" ]; then
    echo "   Checking venv-py311/lib/python3.11/site-packages/:"
    ls venv-py311/lib/python3.11/site-packages/ | grep -E "(playwright|sqlalchemy|celery|redis|fastapi)" | head -10
fi

echo

# Environment variables
echo "🔧 Environment Variables:"
echo "   PYTHONPATH: ${PYTHONPATH:-Not set}"
echo "   REDIS_URL: ${REDIS_URL:-Not set}"
echo "   DATABASE_URL: ${DATABASE_URL:-Not set}"

echo

# Recommendations
echo "💡 Quick Fixes to Try:"
echo "   1. Activate venv-py311: source venv-py311/bin/activate"
echo "   2. Check packages: pip list | grep playwright"
echo "   3. Reinstall if needed: pip install playwright sqlalchemy celery"
echo "   4. Run debug script: python debug_env.py"
