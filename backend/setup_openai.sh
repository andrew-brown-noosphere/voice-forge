#!/bin/bash

# VoiceForge OpenAI Setup Script
# This script helps you set up your OpenAI API key for the VoiceForge AI content generation

echo "🚀 VoiceForge OpenAI API Setup"
echo "================================"
echo ""

# Check if OpenAI API key is already set
if [ -n "$OPENAI_API_KEY" ]; then
    echo "✅ OpenAI API key is already set in environment variables"
    echo "   Key preview: ${OPENAI_API_KEY:0:10}..."
    echo ""
else
    echo "❌ OpenAI API key not found in environment variables"
    echo ""
fi

# Check for .env file
ENV_FILE=".env"
if [ -f "$ENV_FILE" ]; then
    if grep -q "OPENAI_API_KEY" "$ENV_FILE"; then
        echo "✅ OpenAI API key found in .env file"
        echo ""
    else
        echo "❌ OpenAI API key not found in .env file"
        echo ""
    fi
else
    echo "❌ .env file not found"
    echo ""
fi

echo "📋 Setup Options:"
echo "=================="
echo ""
echo "1. Set API key in environment variable (recommended for production)"
echo "2. Set API key in .env file (good for development)"
echo "3. Test existing API key"
echo "4. View setup instructions"
echo ""

read -p "Choose an option (1-4): " choice

case $choice in
    1)
        echo ""
        echo "Setting up environment variable..."
        echo ""
        echo "Add this line to your shell profile (~/.bashrc, ~/.zshrc, etc.):"
        echo ""
        echo "export OPENAI_API_KEY=\"sk-your-actual-api-key-here\""
        echo ""
        echo "Or run this command for the current session:"
        echo ""
        read -p "Enter your OpenAI API key: " api_key
        if [ -n "$api_key" ]; then
            export OPENAI_API_KEY="$api_key"
            echo "export OPENAI_API_KEY=\"$api_key\"" >> ~/.bashrc
            echo "✅ API key set for current session and added to ~/.bashrc"
            echo "   Restart your terminal or run 'source ~/.bashrc' to persist"
        else
            echo "❌ No API key provided"
        fi
        ;;
    2)
        echo ""
        echo "Setting up .env file..."
        echo ""
        read -p "Enter your OpenAI API key: " api_key
        if [ -n "$api_key" ]; then
            if [ -f "$ENV_FILE" ]; then
                # Update existing .env file
                if grep -q "OPENAI_API_KEY" "$ENV_FILE"; then
                    # Replace existing key
                    sed -i.bak "s/OPENAI_API_KEY=.*/OPENAI_API_KEY=$api_key/" "$ENV_FILE"
                    echo "✅ Updated existing OPENAI_API_KEY in .env file"
                else
                    # Add new key
                    echo "OPENAI_API_KEY=$api_key" >> "$ENV_FILE"
                    echo "✅ Added OPENAI_API_KEY to existing .env file"
                fi
            else
                # Create new .env file
                echo "OPENAI_API_KEY=$api_key" > "$ENV_FILE"
                echo "✅ Created .env file with OPENAI_API_KEY"
            fi
        else
            echo "❌ No API key provided"
        fi
        ;;
    3)
        echo ""
        echo "Testing OpenAI API connection..."
        echo ""
        cd "$(dirname "$0")"
        python scripts/test_openai.py
        ;;
    4)
        echo ""
        echo "📖 Setup Instructions:"
        echo "====================="
        echo ""
        echo "1. Get your OpenAI API key:"
        echo "   • Go to https://platform.openai.com/"
        echo "   • Sign up or log in"
        echo "   • Navigate to API Keys"
        echo "   • Create a new secret key"
        echo "   • Copy the key (starts with 'sk-')"
        echo ""
        echo "2. Set the API key using one of these methods:"
        echo ""
        echo "   Method A: Environment Variable (Recommended)"
        echo "   export OPENAI_API_KEY=\"sk-your-actual-key-here\""
        echo ""
        echo "   Method B: .env File (Development)"
        echo "   echo \"OPENAI_API_KEY=sk-your-actual-key-here\" >> .env"
        echo ""
        echo "3. Test your setup:"
        echo "   python scripts/test_openai.py"
        echo ""
        echo "4. Restart your VoiceForge backend server"
        echo ""
        ;;
    *)
        echo "❌ Invalid choice"
        ;;
esac

echo ""
echo "🔗 Next Steps:"
echo "=============="
echo ""
echo "1. Make sure your API key is set (test with option 3)"
echo "2. Restart your VoiceForge backend server"
echo "3. Try generating content - it should now use real AI!"
echo ""
echo "💡 Troubleshooting:"
echo "   • If you get 'No AI providers configured', check your API key"
echo "   • Make sure you have OpenAI credits in your account"
echo "   • Check the backend logs for detailed error messages"
echo ""
echo "✨ Your VoiceForge AI content generation should now be working!"
