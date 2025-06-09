#!/bin/bash
# Make service scripts executable
chmod +x start.sh
chmod +x stop.sh
echo "✅ Scripts are now executable"
echo ""
echo "🚀 Usage:"
echo "  ./start.sh  - Start VoiceForge (Redis + Celery + API)"
echo "  ./stop.sh   - Stop all services"
echo ""
