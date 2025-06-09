#!/bin/bash

echo "🚀 Starting VoiceForge Frontend..."
echo "Navigate to VoiceForge frontend directory and start the dev server"

cd /Users/andrewbrown/Sites/noosphere/github/voice-forge/frontend

echo "📍 Current directory: $(pwd)"
echo "🔧 Installing dependencies if needed..."
npm install

echo "🎯 Starting VoiceForge Frontend..."
echo "This will start VoiceForge on port 3009"
echo ""
echo "Make sure Gypsum API is running on port 3001 first!"
echo ""
echo "Press Ctrl+C to stop the service"
echo ""

npm run dev
