# VoiceForge Backend - Simple Startup

## Quick Start

```bash
# One-time setup
bash make_executable.sh

# Start everything
./start.sh

# Stop everything  
./stop.sh
```

## What `start.sh` does:
- ✅ Starts Redis (if not running)
- ✅ Starts Celery workers for all queues (crawl, process, rag, signals)
- ✅ Starts FastAPI server at http://localhost:8000
- ✅ Handles graceful shutdown with Ctrl+C

## Services Included:
- **FastAPI Server**: Main API at http://localhost:8000
- **Redis**: Task queue for background jobs
- **Celery Workers**: 
  - `crawl` queue: Website crawling
  - `process` queue: Content processing  
  - `rag` queue: RAG operations
  - `signals` queue: **Signal automation** (NEW)

## Access Your App:
- **API**: http://localhost:8000
- **Frontend**: http://localhost:3000 (run separately)
- **Signal Settings**: Settings → "Manage Signal Sources & Automation"

That's it! One command to start everything. 🚀
