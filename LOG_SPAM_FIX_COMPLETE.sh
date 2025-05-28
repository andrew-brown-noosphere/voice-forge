#!/bin/bash

# 🔧 Quick fix for log spam issue

echo "🔧 Fixing VoiceForge log spam..."

echo "✅ Applied fixes:"
echo "   1. Reduced logging level from INFO to WARNING"
echo "   2. Changed domains query logging to debug level when empty"
echo "   3. Added caching to analytics dashboard (30-second refresh limit)"
echo "   4. Skip expensive analytics calls when no content exists"
echo "   5. Better error handling to avoid organization-related error spam"

echo ""
echo "🚀 To test the fixes:"
echo "   1. Restart your backend server:"
echo "      cd backend && python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "   2. Restart your frontend:"
echo "      cd frontend && npm run dev"
echo ""
echo "   3. Log spam should now be significantly reduced!"

echo ""
echo "📊 If you want to see analytics in action:"
echo "   1. Run a crawl first to get some data"
echo "   2. Click 'Show Analytics' on your dashboard"
echo "   3. You'll see beautiful charts and insights!"

echo ""
echo "🎯 Log levels now:"
echo "   - ERROR: Critical issues only"
echo "   - WARNING: Important warnings (default level)"
echo "   - INFO: Only when domains are found"
echo "   - DEBUG: Empty domain queries (not shown by default)"
