#!/bin/bash

# Quick Redis Check and Start Script

echo "🔴 Redis Setup for VoiceForge"
echo "============================"

# Check if Redis is installed
if ! command -v redis-server &> /dev/null; then
    echo "❌ Redis is not installed"
    echo
    echo "📋 Installation options:"
    echo "   macOS:   brew install redis"
    echo "   Ubuntu:  sudo apt install redis-server"
    echo "   Docker:  docker run -d -p 6379:6379 --name redis redis:alpine"
    echo
    exit 1
fi

# Check if Redis is already running
if redis-cli ping &> /dev/null; then
    echo "✅ Redis is already running"
    echo "📊 Redis info:"
    redis-cli info server | grep redis_version
    echo "🌐 Connection: localhost:6379"
else
    echo "🚀 Starting Redis server..."
    
    # Try different methods to start Redis
    if command -v brew &> /dev/null && brew services list | grep redis &> /dev/null; then
        # macOS with Homebrew
        echo "📦 Using Homebrew to start Redis..."
        brew services start redis
    else
        # Manual start
        echo "🔧 Starting Redis manually..."
        redis-server --daemonize yes --port 6379
    fi
    
    # Wait and verify
    sleep 2
    if redis-cli ping &> /dev/null; then
        echo "✅ Redis started successfully"
        echo "🌐 Running on: localhost:6379"
    else
        echo "❌ Failed to start Redis"
        echo "🔧 Try running manually: redis-server"
        exit 1
    fi
fi

echo
echo "🧪 Testing Redis connection..."
echo "PING: $(redis-cli ping)"
echo "📊 Redis is ready for Celery!"
