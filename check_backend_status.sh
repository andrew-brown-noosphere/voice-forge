#!/bin/bash

echo "🔍 VoiceForge Backend Status Check"
echo "=================================="

# Check if backend process is running
echo "1️⃣ Checking if backend process is running..."
BACKEND_PID=$(pgrep -f "uvicorn.*main:app")

if [ ! -z "$BACKEND_PID" ]; then
    echo "✅ Backend process found (PID: $BACKEND_PID)"
    echo "   Process details:"
    ps aux | grep "$BACKEND_PID" | grep -v grep
else
    echo "❌ No backend process found"
    echo "🔧 Backend is not running!"
fi

echo ""

# Check if port 8000 is in use
echo "2️⃣ Checking if port 8000 is in use..."
PORT_CHECK=$(lsof -ti:8000)

if [ ! -z "$PORT_CHECK" ]; then
    echo "✅ Something is listening on port 8000"
    echo "   Process using port 8000:"
    lsof -i:8000
else
    echo "❌ Nothing is listening on port 8000"
    echo "🔧 Backend is definitely not running!"
fi

echo ""

# Test if we can connect to localhost:8000
echo "3️⃣ Testing connection to localhost:8000..."
if curl -s --connect-timeout 3 http://localhost:8000 > /dev/null 2>&1; then
    echo "✅ Can connect to localhost:8000"
    echo "   Response:"
    curl -s http://localhost:8000
else
    echo "❌ Cannot connect to localhost:8000"
    echo "🔧 Backend is not accessible!"
fi

echo ""
echo "🚀 TO START THE BACKEND:"
echo "========================"
echo "cd /Users/andrewbrown/Sites/noosphere/github/voice-forge/backend"
echo "source venv-py311/bin/activate"
echo "python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "Then check for error messages in the terminal output!"
