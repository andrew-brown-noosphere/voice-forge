#!/bin/bash

# VoiceForge Multi-tenant Backend Setup Script
echo "🚀 Setting up VoiceForge Multi-tenant Backend..."

# Navigate to backend directory
cd /Users/andrewbrown/Sites/noosphere/github/voice-forge/backend

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv-py311/bin/activate

# Install new dependencies
echo "🔧 Installing authentication dependencies..."
pip install PyJWT>=2.6.0
pip install httpx>=0.24.0
pip install cryptography>=3.4.8

# Check if .env file has required keys
echo "🔐 Checking environment configuration..."
if grep -q "CLERK_SECRET_KEY" .env; then
    echo "✅ CLERK_SECRET_KEY found in .env"
else
    echo "❌ CLERK_SECRET_KEY not found in .env"
    echo "Please add: CLERK_SECRET_KEY=sk_test_EICq39wG0LmMB8FSLU6uWtiFI9uW4CqLYeofVvYJ3v"
fi

if grep -q "CLERK_PUBLISHABLE_KEY" .env; then
    echo "✅ CLERK_PUBLISHABLE_KEY found in .env"
else
    echo "⚠️  CLERK_PUBLISHABLE_KEY not found in .env"
    echo "Adding CLERK_PUBLISHABLE_KEY..."
    echo "CLERK_PUBLISHABLE_KEY=pk_test_aGFyZHktZmxvdW5kZXItMC5jbGVyay5hY2NvdW50cy5kZXYk" >> .env
fi

echo ""
echo "🎯 Multi-tenant backend setup completed!"
echo ""
echo "📋 Summary of changes:"
echo "✅ Added PyJWT, httpx, cryptography to requirements.txt"
echo "✅ Created auth/clerk_auth.py with Clerk authentication middleware"
echo "✅ Updated database/models.py with org_id columns and indexes"
echo "✅ Updated api/main.py with multi-tenant authentication on all endpoints"
echo "✅ Added authentication test endpoints: /auth/me and /auth/health"
echo ""
echo "🔥 Ready to test! Start the backend with:"
echo "   cd /Users/andrewbrown/Sites/noosphere/github/voice-forge/backend"
echo "   source venv-py311/bin/activate"
echo "   python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "🧪 Test endpoints:"
echo "   GET  http://localhost:8000/ (public)"
echo "   GET  http://localhost:8000/auth/health (public)"
echo "   GET  http://localhost:8000/auth/me (requires auth)"
echo "   POST http://localhost:8000/crawl (requires auth + org)"
echo ""
echo "📚 All API endpoints now require organization-level authentication!"
