#!/bin/bash

echo "🔍 VoiceForge Backend Diagnostic"
echo "================================"

# Check if we're in the right directory
echo "📂 Current directory: $(pwd)"
echo "📂 Backend directory exists: $([ -d "/Users/andrewbrown/Sites/noosphere/github/voice-forge/backend" ] && echo "✅ YES" || echo "❌ NO")"

# Check virtual environment
echo ""
echo "🐍 Python Environment:"
if [ -d "/Users/andrewbrown/Sites/noosphere/github/voice-forge/backend/venv-py311" ]; then
    echo "   ✅ venv-py311 directory exists"
    source /Users/andrewbrown/Sites/noosphere/github/voice-forge/backend/venv-py311/bin/activate
    echo "   🐍 Python version: $(python --version)"
    echo "   📦 Pip location: $(which pip)"
else
    echo "   ❌ venv-py311 directory not found"
fi

# Check if port 8000 is in use
echo ""
echo "🔌 Port Status:"
if lsof -i :8000 > /dev/null 2>&1; then
    echo "   ⚠️  Port 8000 is already in use:"
    lsof -i :8000
else
    echo "   ✅ Port 8000 is available"
fi

# Check dependencies
echo ""
echo "📦 Key Dependencies:"
cd /Users/andrewbrown/Sites/noosphere/github/voice-forge/backend
source venv-py311/bin/activate 2>/dev/null
echo "   FastAPI: $(pip show fastapi 2>/dev/null | grep Version || echo "❌ Not installed")"
echo "   Uvicorn: $(pip show uvicorn 2>/dev/null | grep Version || echo "❌ Not installed")"

# Check if main.py exists
echo ""
echo "📄 Main Files:"
echo "   api/main.py exists: $([ -f "/Users/andrewbrown/Sites/noosphere/github/voice-forge/backend/api/main.py" ] && echo "✅ YES" || echo "❌ NO")"
echo "   .env exists: $([ -f "/Users/andrewbrown/Sites/noosphere/github/voice-forge/backend/.env" ] && echo "✅ YES" || echo "❌ NO")"

echo ""
echo "🚀 Recommended Next Steps:"
echo "   1. cd /Users/andrewbrown/Sites/noosphere/github/voice-forge/backend"
echo "   2. source venv-py311/bin/activate"
echo "   3. pip install uvicorn fastapi"
echo "   4. python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000"
