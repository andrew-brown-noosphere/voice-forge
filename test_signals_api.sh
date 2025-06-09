#!/bin/bash

echo "🧪 Testing the new abstracted signals API..."
echo ""

# Test health endpoint
echo "1. Testing signals health endpoint..."
curl -s http://localhost:8000/signals/health | jq '.' || echo "Health endpoint failed"

echo ""
echo "2. Testing supported platforms endpoint..."
curl -s http://localhost:8000/signals/platforms/supported | jq '.' || echo "Platforms endpoint failed"

echo ""
echo "3. Testing backwards compatibility - Reddit signals health..."
curl -s http://localhost:8000/reddit-signals/health | jq '.' || echo "Reddit signals health failed"

echo ""
echo "✅ API tests complete!"
echo ""
echo "🚀 Next steps:"
echo "1. Start the backend: cd backend && python -m uvicorn api.main:app --reload"
echo "2. Start the frontend: cd frontend && npm run dev"
echo "3. Navigate to http://localhost:5173/signals to see the new interface!"
