#!/bin/bash

# VoiceForge UI Text Updates Verification Script
echo "🔤 VoiceForge UI Text Updates Verification"
echo "=========================================="
echo ""

# Check ModernDashboard for updated text
echo "1️⃣ Checking ModernDashboard text updates..."
if grep -q "Pages Analyzed" "frontend/src/components/ModernDashboard.jsx"; then
    echo "✅ 'Pages Analyzed' found in ModernDashboard"
else
    echo "❌ 'Pages Analyzed' not found in ModernDashboard"
fi

if grep -q "Analyze Web Content" "frontend/src/components/ModernDashboard.jsx"; then
    echo "✅ 'Analyze Web Content' button text found in ModernDashboard"
else
    echo "❌ 'Analyze Web Content' button text not found in ModernDashboard"
fi

echo ""

# Check Dashboard for updated text
echo "2️⃣ Checking Dashboard text updates..."
if grep -q "Analyze Web Content" "frontend/src/pages/Dashboard.jsx"; then
    echo "✅ 'Analyze Web Content' button text found in Dashboard"
else
    echo "❌ 'Analyze Web Content' button text not found in Dashboard"
fi

echo ""

# Check AppSidebar for updated text
echo "3️⃣ Checking AppSidebar text updates..."
if grep -q "Content Analysis" "frontend/src/components/AppSidebar.jsx"; then
    echo "✅ 'Content Analysis' section found in AppSidebar"
else
    echo "❌ 'Content Analysis' section not found in AppSidebar"
fi

if grep -q "Recent Analysis" "frontend/src/components/AppSidebar.jsx"; then
    echo "✅ 'Recent Analysis' found in AppSidebar"
else
    echo "❌ 'Recent Analysis' not found in AppSidebar"
fi

if grep -q "New Analysis" "frontend/src/components/AppSidebar.jsx"; then
    echo "✅ 'New Analysis' found in AppSidebar"
else
    echo "❌ 'New Analysis' not found in AppSidebar"
fi

echo ""

# Check for old terminology (should not exist)
echo "4️⃣ Checking for old terminology removal..."
if ! grep -q "Pages Crawled" "frontend/src/components/ModernDashboard.jsx"; then
    echo "✅ 'Pages Crawled' successfully removed from ModernDashboard"
else
    echo "❌ 'Pages Crawled' still found in ModernDashboard"
fi

if ! grep -q "New Crawl" "frontend/src/pages/Dashboard.jsx" && ! grep -q "New Crawl" "frontend/src/components/ModernDashboard.jsx"; then
    echo "✅ 'New Crawl' button text successfully updated"
else
    echo "❌ 'New Crawl' button text still found"
fi

echo ""

# Summary
echo "📋 Summary of Text Updates:"
echo "• 'Pages Crawled' → 'Pages Analyzed' (more user-friendly)"
echo "• 'New Crawl' → 'Analyze Web Content' (clearer action)"
echo "• 'Recent Crawls' → 'Recent Analysis' (consistent terminology)"
echo "• 'Crawling' → 'Content Analysis' (professional section naming)"
echo ""
echo "🎯 Result: More professional, user-friendly interface language!"
