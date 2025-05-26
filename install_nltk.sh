#!/bin/bash

# Fix NLTK Dependencies for VoiceForge
# This script installs NLTK and downloads required resources

echo "🔧 Installing NLTK Dependencies for VoiceForge"
echo "=============================================="

# Navigate to backend and activate environment
cd /Users/andrewbrown/Sites/noosphere/github/voice-forge/backend

# Activate the correct virtual environment
if [ -d "venv-py311" ]; then
    echo "🐍 Activating Python 3.11 virtual environment..."
    source venv-py311/bin/activate
elif [ -d "venv" ]; then
    echo "🐍 Activating Python virtual environment..."
    source venv/bin/activate
else
    echo "❌ No virtual environment found!"
    exit 1
fi

echo "📍 Using Python: $(which python)"
echo "📍 Python version: $(python --version)"

# Install NLTK
echo ""
echo "📦 Installing NLTK..."
pip install nltk

# Download required NLTK resources
echo ""
echo "📥 Downloading NLTK resources..."
python -c "
import nltk
import ssl

# Handle SSL issues if they occur
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

print('Downloading punkt...')
nltk.download('punkt', quiet=False)

print('Downloading punkt_tab...')
nltk.download('punkt_tab', quiet=False)

print('Downloading stopwords (useful for text processing)...')
nltk.download('stopwords', quiet=False)

print('✅ NLTK resources downloaded successfully!')
"

# Test NLTK installation
echo ""
echo "🧪 Testing NLTK installation..."
python -c "
import nltk
from nltk.tokenize import sent_tokenize

# Test sentence tokenization
test_text = 'This is a test sentence. This is another sentence! And here is a third one?'
sentences = sent_tokenize(test_text)
print(f'✅ NLTK working! Split into {len(sentences)} sentences:')
for i, sentence in enumerate(sentences, 1):
    print(f'   {i}. {sentence}')
"

echo ""
echo "🎉 NLTK installation complete!"
echo ""
echo "🚀 Now you can run the content processing:"
echo "   python process_crawled_content_fixed.py"
