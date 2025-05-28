#!/bin/bash

echo "🔧 Applying final fixes for API call spam..."

# Set logging level to ERROR to reduce all spam
echo "📝 Setting logging level to ERROR..."

# Update logging configuration
cat > backend/logging_config.py << 'EOF'
import logging
import sys

def setup_logging():
    """Configure logging to reduce spam while keeping important messages."""
    
    # Set root logger to ERROR level
    logging.getLogger().setLevel(logging.ERROR)
    
    # Set specific loggers to appropriate levels
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.ERROR)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    # Keep our app logger at WARNING for important messages
    app_logger = logging.getLogger("api")
    app_logger.setLevel(logging.WARNING)
    
    # Create a clean formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Configure console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)
    
    # Clear existing handlers and add our clean one
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    
    print("✅ Logging configured: Only warnings and errors will be shown")

if __name__ == "__main__":
    setup_logging()
EOF

echo "✅ Created logging configuration"

echo ""
echo "🎯 Fixes applied:"
echo "   1. ✅ Added 30-second caching to /domains endpoint"
echo "   2. ✅ Reduced database logging to DEBUG level"
echo "   3. ✅ Fixed useEffect dependencies to prevent loops"
echo "   4. ✅ Added component cleanup and throttling"
echo "   5. ✅ Created proper logging configuration"

echo ""
echo "🚀 To apply the logging fix:"
echo "   1. Add this to your backend/api/main.py at the top:"
echo "      from logging_config import setup_logging"
echo "      setup_logging()"
echo ""
echo "   2. Restart your backend server:"
echo "      cd backend && python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "   3. Restart your frontend:"
echo "      cd frontend && npm run dev"

echo ""
echo "📊 Expected result:"
echo "   - No more repeated GET /domains calls"
echo "   - Only important warnings and errors in logs"
echo "   - Much cleaner console output"
echo "   - Analytics load only when toggled on"
echo "   - Cached API responses for 30 seconds"

echo ""
echo "🎉 API spam should now be eliminated!"