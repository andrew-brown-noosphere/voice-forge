#!/bin/bash

# VoiceForge Quick Environment Setup
# Ensures the correct Python environment has all dependencies

echo "🔧 VoiceForge Environment Setup"
echo "==============================="

# Navigate to backend
cd /Users/andrewbrown/Sites/noosphere/github/voice-forge/backend

# Check for Python 3.11 virtual environment
if [ -d "venv-py311" ]; then
    echo "✅ Found Python 3.11 virtual environment"
    echo "🐍 Activating venv-py311..."
    source venv-py311/bin/activate
elif [ -d "venv" ]; then
    echo "✅ Found Python virtual environment"
    echo "🐍 Activating venv..."
    source venv/bin/activate
else
    echo "❌ No virtual environment found!"
    echo "💡 Creating Python 3.11 virtual environment..."
    python3.11 -m venv venv-py311
    source venv-py311/bin/activate
fi

# Show current Python version
echo "📍 Current Python: $(which python)"
echo "📍 Python version: $(python --version)"

# Install/upgrade required packages
echo ""
echo "📦 Installing required packages..."
pip install --upgrade pip

# Core dependencies
echo "   Installing FastAPI and Uvicorn..."
pip install fastapi uvicorn

# Check if requirements.txt exists and install
if [ -f "requirements.txt" ]; then
    echo "   Installing from requirements.txt..."
    pip install -r requirements.txt
else
    echo "   ⚠️  requirements.txt not found, installing core packages..."
    pip install sqlalchemy psycopg2-binary python-multipart
fi

# Verify uvicorn installation
echo ""
echo "🧪 Testing uvicorn installation..."
if python -m uvicorn --version > /dev/null 2>&1; then
    echo "✅ Uvicorn installed successfully: $(python -m uvicorn --version)"
else
    echo "❌ Uvicorn installation failed"
    echo "🔧 Trying alternative installation..."
    pip install uvicorn[standard]
fi

# Test FastAPI import
echo ""
echo "🧪 Testing FastAPI import..."
python -c "import fastapi; print(f'✅ FastAPI {fastapi.__version__} imported successfully')" 2>/dev/null || {
    echo "❌ FastAPI import failed"
    pip install fastapi
}

# Test database connectivity
echo ""
echo "🧪 Testing database components..."
python -c "from database.session import get_db_session; print('✅ Database session OK')" 2>/dev/null || {
    echo "⚠️  Database session test failed (may need database setup)"
}

echo ""
echo "🎉 Environment setup complete!"
echo ""
echo "🚀 Next steps:"
echo "   1. Start the application: ./start_voiceforge.sh"
echo "   2. Or manually start backend: python -m uvicorn api.main:app --reload"
echo ""
echo "💡 If you have issues, try:"
echo "   source venv-py311/bin/activate"
echo "   python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000"
