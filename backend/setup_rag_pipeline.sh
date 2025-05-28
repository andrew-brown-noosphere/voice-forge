#!/bin/bash
# VoiceForge RAG Pipeline Quick Setup Script

echo "🚀 VoiceForge RAG Pipeline Quick Setup"
echo "======================================"

# Make scripts executable
chmod +x optimized_processing_pipeline.py
chmod +x automate_rag_pipeline.py

echo "✅ Scripts are now executable"

# Check if organization ID is set
if [ -z "$VOICEFORGE_ORG_ID" ]; then
    echo ""
    echo "⚠️  Organization ID not set"
    echo "Set it with: export VOICEFORGE_ORG_ID='your-org-id-here'"
    echo ""
    echo "Or run: python automate_rag_pipeline.py --org-id your-org-id-here"
else
    echo "✅ Organization ID is set: $VOICEFORGE_ORG_ID"
    echo ""
    echo "🚀 Ready to run optimization:"
    echo "   python automate_rag_pipeline.py --auto"
fi

echo ""
echo "📖 See RAG_OPTIMIZATION_README.md for detailed instructions"
