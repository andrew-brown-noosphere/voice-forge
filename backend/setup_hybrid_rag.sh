#!/bin/bash
"""
Quick setup script for Hybrid RAG implementation.
This script automates the setup process for the enhanced RAG system.
"""

set -e  # Exit on any error

echo "🚀 VoiceForge Hybrid RAG Setup"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the backend directory
if [ ! -f "requirements.txt" ]; then
    print_error "Please run this script from the backend directory"
    exit 1
fi

echo "Step 1: Checking Python dependencies..."
if command -v python3 &> /dev/null; then
    print_status "Python 3 found"
else
    print_error "Python 3 is required but not found"
    exit 1
fi

echo "Step 2: Installing/checking required packages..."
pip install -q sentence-transformers>=2.2.2
pip install -q nltk>=3.8.1
pip install -q numpy>=1.24.2
print_status "Dependencies checked/installed"

echo "Step 3: Downloading NLTK data..."
python -c "
import nltk
import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    print('NLTK data downloaded successfully')
except Exception as e:
    print(f'NLTK download warning: {e}')
"
print_status "NLTK data setup complete"

echo "Step 4: Applying database migration..."
if python apply_fts_migration.py; then
    print_status "Database migration applied successfully"
else
    print_warning "Database migration failed - you may need to run it manually"
fi

echo "Step 5: Running test suite..."
echo "This will test the hybrid RAG implementation..."
if python test_hybrid_rag.py; then
    print_status "All tests passed! 🎉"
else
    print_warning "Some tests failed - check the output above"
fi

echo ""
echo "🎯 Setup Complete!"
echo "=================="
echo ""
echo "The Hybrid RAG system is now ready. You can:"
echo ""
echo "1. Test the API endpoints:"
echo "   curl -X GET 'http://localhost:8000/api/rag/strategies'"
echo ""
echo "2. Run a search:"
echo "   curl -X POST 'http://localhost:8000/api/rag/search' \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"query\": \"test\", \"strategy\": \"hybrid\"}'"
echo ""
echo "3. Check the documentation:"
echo "   cat HYBRID_RAG_README.md"
echo ""
echo "4. Run tests anytime:"
echo "   python test_hybrid_rag.py"
echo ""
print_status "Happy searching! 🔍"
