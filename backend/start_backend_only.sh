#!/bin/bash
# Quick start script for just the FastAPI backend

echo "🌐 Starting VoiceForge FastAPI Backend..."
echo "📍 Running from: $(pwd)"
echo "🔧 Using correct module path: api.main:app"

python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

echo "🚀 Backend should be running at http://localhost:8000"
