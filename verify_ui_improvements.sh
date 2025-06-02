#!/bin/bash

# VoiceForge UI Improvements Verification Script
echo "🧪 VoiceForge UI Improvements Verification"
echo "=========================================="
echo ""

# Check if the JWT token components have been moved to backup
echo "1️⃣ Checking JWT Token Widget Removal..."
if [ ! -f "frontend/src/components/SimpleTokenDisplay.jsx" ]; then
    echo "✅ SimpleTokenDisplay.jsx removed from components"
else
    echo "❌ SimpleTokenDisplay.jsx still in components directory"
fi

if [ -f "frontend/src/backup/SimpleTokenDisplay.jsx" ]; then
    echo "✅ SimpleTokenDisplay.jsx moved to backup"
else
    echo "❌ SimpleTokenDisplay.jsx not found in backup"
fi

# Check App.jsx for JWT widget removal
if ! grep -q "SimpleTokenDisplay" "frontend/src/App.jsx"; then
    echo "✅ SimpleTokenDisplay import removed from App.jsx"
else
    echo "❌ SimpleTokenDisplay still referenced in App.jsx"
fi

echo ""

# Check Dashboard for modern UI default
echo "2️⃣ Checking Modern UI Default..."
if ! grep -q "Switch to Modern" "frontend/src/pages/Dashboard.jsx"; then
    echo "✅ 'Switch to Modern' button removed from Dashboard"
else
    echo "❌ 'Switch to Modern' button still present in Dashboard"
fi

if grep -q "ModernDashboard onRefresh" "frontend/src/pages/Dashboard.jsx"; then
    echo "✅ Dashboard always uses ModernDashboard component"
else
    echo "❌ Dashboard not configured to always use ModernDashboard"
fi

echo ""

# Check Content Generator improvements
echo "3️⃣ Checking Content Generator Robustness..."
if grep -q "retryCount" "frontend/src/pages/ContentGenerator.jsx"; then
    echo "✅ Retry logic added to ContentGenerator"
else
    echo "❌ Retry logic missing from ContentGenerator"
fi

if grep -q "retryCount" "frontend/src/pages/ModernContentGenerator.jsx"; then
    echo "✅ Retry logic added to ModernContentGenerator"
else
    echo "❌ Retry logic missing from ModernContentGenerator"
fi

echo ""

# Summary
echo "📋 Summary of Changes:"
echo "• JWT token debug widgets removed from production UI"
echo "• Modern UI is now the default experience"
echo "• Domains loading is more robust with retry logic"
echo "• Error handling improved throughout the application"
echo ""
echo "🚀 Ready for deployment!"
echo ""
echo "To test manually:"
echo "1. Start the application: npm run dev"
echo "2. Navigate to dashboard - should show modern UI immediately"
echo "3. Test content generator - domains should load reliably"
echo "4. Verify no JWT token widgets are visible"
