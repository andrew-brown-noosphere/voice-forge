#!/bin/bash

# VoiceForge RAG Integration Startup Script
# This script helps you start both backend and frontend servers

echo "🚀 Starting VoiceForge RAG Application"
echo "====================================="

# Function to check if a port is in use
check_port() {
    lsof -i :$1 > /dev/null 2>&1
    return $?
}

# Function to start backend
start_backend() {
    echo "📊 Starting Backend Server..."
    cd /Users/andrewbrown/Sites/noosphere/github/voice-forge/backend
    
    # Check if virtual environment exists (prioritize venv-py311)
    if [ -d "venv-py311" ]; then
        echo "   🐍 Activating Python 3.11 virtual environment..."
        source venv-py311/bin/activate
    elif [ -d "venv" ]; then
        echo "   🐍 Activating Python virtual environment..."
        source venv/bin/activate
    else
        echo "   ⚠️  No virtual environment found. Using system Python."
    fi
    
    # Check if backend is already running
    if check_port 8000; then
        echo "   ⚠️  Backend already running on port 8000"
    else
        echo "   🔧 Installing/updating dependencies..."
        pip install -r requirements.txt
        
        # Make sure uvicorn is installed
        echo "   📦 Ensuring uvicorn is available..."
        pip install uvicorn
        
        echo "   🌐 Starting FastAPI server on http://localhost:8000"
        python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000 &
        
        # Wait for backend to start
        echo "   ⏳ Waiting for backend to start..."
        sleep 5
        if check_port 8000; then
            echo "   ✅ Backend started successfully!"
        else
            echo "   ❌ Backend failed to start"
            echo "   💡 Try manually: cd backend && source venv-py311/bin/activate && python -m uvicorn api.main:app --reload"
            return 1
        fi
    fi
}

# Function to start frontend
start_frontend() {
    echo "🎨 Starting Frontend Server..."
    cd /Users/andrewbrown/Sites/noosphere/github/voice-forge/frontend
    
    # Check if frontend is already running
    if check_port 5173; then
        echo "   ⚠️  Frontend already running on port 5173"
    else
        echo "   📦 Installing dependencies..."
        npm install
        
        echo "   🖥️  Starting Vite dev server on http://localhost:5173"
        npm run dev &
        
        # Wait for frontend to start
        echo "   ⏳ Waiting for frontend to start..."
        sleep 7
        if check_port 5173; then
            echo "   ✅ Frontend started successfully!"
        else
            echo "   ❌ Frontend failed to start"
            echo "   💡 Try manually: cd frontend && npm run dev"
            return 1
        fi
    fi
}

# Function to test RAG system
test_rag() {
    echo "🧪 Testing RAG System..."
    cd /Users/andrewbrown/Sites/noosphere/github/voice-forge/backend
    
    # Activate the correct environment
    if [ -d "venv-py311" ]; then
        source venv-py311/bin/activate
    elif [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    # Check system status
    if [ -f "scripts/quick_status.py" ]; then
        python scripts/quick_status.py
    else
        echo "   ⚠️  quick_status.py not found, skipping status check"
    fi
    
    echo ""
    echo "🔗 Application URLs:"
    echo "   Backend API: http://localhost:8000"
    echo "   Frontend App: http://localhost:5173"
    echo "   API Docs: http://localhost:8000/docs"
}

# Main execution
main() {
    # Check if we're in the right directory
    if [ ! -d "/Users/andrewbrown/Sites/noosphere/github/voice-forge/backend" ]; then
        echo "❌ VoiceForge directory not found. Please check the path."
        exit 1
    fi
    
    # Start backend
    start_backend
    if [ $? -ne 0 ]; then
        echo "❌ Failed to start backend"
        echo ""
        echo "🔧 Manual Backend Startup:"
        echo "   cd /Users/andrewbrown/Sites/noosphere/github/voice-forge/backend"
        echo "   source venv-py311/bin/activate"
        echo "   pip install uvicorn"
        echo "   python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000"
        exit 1
    fi
    
    # Start frontend
    start_frontend
    if [ $? -ne 0 ]; then
        echo "❌ Failed to start frontend"
        echo ""
        echo "🔧 Manual Frontend Startup:"
        echo "   cd /Users/andrewbrown/Sites/noosphere/github/voice-forge/frontend"
        echo "   npm install"
        echo "   npm run dev"
        exit 1
    fi
    
    # Test RAG system
    test_rag
    
    echo ""
    echo "🎉 VoiceForge RAG Application is now running!"
    echo ""
    echo "📋 Next Steps:"
    echo "   1. Open http://localhost:5173 in your browser"
    echo "   2. Navigate to 'Content Generator' in the sidebar"
    echo "   3. Enter a query and test content generation"
    echo ""
    echo "🛑 To stop the application:"
    echo "   Press Ctrl+C or run: pkill -f 'uvicorn\\|vite'"
}

# Handle Ctrl+C gracefully
trap 'echo ""; echo "🛑 Shutting down VoiceForge..."; pkill -f "uvicorn\\|vite"; exit 0' INT

# Run main function
main

# Keep script running to maintain servers
echo "⏳ Servers are running. Press Ctrl+C to stop."
wait
