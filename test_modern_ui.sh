#!/bin/bash

echo "🎨 VoiceForge Modern UI - Quick Test Script"
echo "=========================================="

# Check if modern pages exist
echo "📁 Checking Modern Page Files..."

if [ -f "/Users/andrewbrown/Sites/noosphere/github/voice-forge/frontend/src/pages/ModernNewCrawl.jsx" ]; then
    echo "✅ ModernNewCrawl.jsx exists"
else
    echo "❌ ModernNewCrawl.jsx missing"
fi

if [ -f "/Users/andrewbrown/Sites/noosphere/github/voice-forge/frontend/src/pages/ModernSettings.jsx" ]; then
    echo "✅ ModernSettings.jsx exists"
else
    echo "❌ ModernSettings.jsx missing"
fi

if [ -f "/Users/andrewbrown/Sites/noosphere/github/voice-forge/frontend/src/pages/ModernCrawlList.jsx" ]; then
    echo "✅ ModernCrawlList.jsx exists"
else
    echo "❌ ModernCrawlList.jsx missing"
fi

if [ -f "/Users/andrewbrown/Sites/noosphere/github/voice-forge/frontend/src/pages/ModernContentSearch.jsx" ]; then
    echo "✅ ModernContentSearch.jsx exists"
else
    echo "❌ ModernContentSearch.jsx missing"
fi

echo ""
echo "🔧 Checking Component Imports..."

# Check if App.jsx has the modern imports
if grep -q "ModernSettings" "/Users/andrewbrown/Sites/noosphere/github/voice-forge/frontend/src/App.jsx"; then
    echo "✅ ModernSettings imported in App.jsx"
else
    echo "❌ ModernSettings not imported in App.jsx"
fi

if grep -q "ModernCrawlList" "/Users/andrewbrown/Sites/noosphere/github/voice-forge/frontend/src/App.jsx"; then
    echo "✅ ModernCrawlList imported in App.jsx"
else
    echo "❌ ModernCrawlList not imported in App.jsx"
fi

echo ""
echo "🔧 Checking ModernNewCrawl Fix..."

# Check if GlassCard was replaced with ModernCard
if grep -q "GlassCard" "/Users/andrewbrown/Sites/noosphere/github/voice-forge/frontend/src/pages/ModernNewCrawl.jsx"; then
    echo "❌ ModernNewCrawl still has GlassCard references"
else
    echo "✅ ModernNewCrawl fixed - using ModernCard"
fi

echo ""
echo "🚀 Modern UI Test Complete!"
echo ""
echo "📍 To test the fixes:"
echo "   1. Start your app: ./start_voiceforge.sh"
echo "   2. Navigate to: http://localhost:3000/crawls/new"
echo "   3. Navigate to: http://localhost:3000/settings"
echo "   4. Navigate to: http://localhost:3000/crawls"
echo "   5. Navigate to: http://localhost:3000/content"
echo ""
echo "🎨 All pages should now display with modern UI!"
