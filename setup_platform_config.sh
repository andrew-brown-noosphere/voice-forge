#!/bin/bash

# Voice Forge Platform Configuration Setup Script
# Run this script to set up the new platform configuration features

echo "🚀 Setting up Voice Forge Platform Configuration..."
echo ""

# Check if we're in the correct directory
if [ ! -f "backend/api/signals.py" ]; then
    echo "❌ Error: Please run this script from the voice-forge root directory"
    exit 1
fi

# 1. Database Migration
echo "📊 Running database migration..."
cd backend
if psql -d voice_forge -f database/migrations/add_platform_configurations.sql; then
    echo "✅ Database migration completed successfully!"
else
    echo "❌ Database migration failed. Please check your PostgreSQL connection."
    echo "   Make sure the voice_forge database exists and you have the right permissions."
    exit 1
fi

# 2. Test Backend Endpoints
echo ""
echo "🔧 Testing backend endpoints..."
if python test_platform_endpoints.py; then
    echo "✅ Backend endpoints are working!"
else
    echo "⚠️  Backend endpoint test had issues. Check the output above."
fi

# 3. Frontend Setup Check
echo ""
echo "🎨 Checking frontend setup..."
cd ../frontend

if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

echo ""
echo "🎉 Setup Complete!"
echo ""
echo "🔥 Your Voice Forge platform configuration is ready!"
echo ""
echo "Next steps:"
echo "1. Start the backend: cd backend && python main.py"
echo "2. Start the frontend: cd frontend && npm run dev"
echo "3. Navigate to: http://localhost:3000/settings/signals"
echo ""
echo "✨ Enjoy your beautiful new platform configuration interface!"