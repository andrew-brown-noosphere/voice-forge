#!/bin/bash

# Quick manual fix for VoiceForge vector extension
echo "🔧 VoiceForge Vector Extension Quick Fix"
echo "========================================"

echo "Connecting to voice_forge database..."

# Try to fix the vector extension manually
psql -d voice_forge << EOF
-- Drop and recreate vector extension
DROP EXTENSION IF EXISTS vector CASCADE;
CREATE EXTENSION IF NOT EXISTS vector;

-- Test vector operations
SELECT '[1,2,3]'::vector <-> '[1,2,4]'::vector as test_distance;

-- Check content_chunks table
SELECT COUNT(*) as total_chunks FROM content_chunks;
SELECT COUNT(*) as chunks_with_embeddings FROM content_chunks WHERE embedding IS NOT NULL;

\q
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Vector extension fixed successfully!"
    echo "🚀 Now restart your backend:"
    echo "   cd backend"
    echo "   source venv-py311/bin/activate"
    echo "   python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000"
else
    echo ""
    echo "❌ Manual fix failed"
    echo "🔧 Try the Python script instead:"
    echo "   python3 emergency_vector_fix.py"
fi
