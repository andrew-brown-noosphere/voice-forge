# Manual Celery Setup for VoiceForge

If the scripts don't work, here are the manual commands:

## 1. Install Redis

**macOS:**
```bash
brew install redis
brew services start redis
```

**Ubuntu:**
```bash
sudo apt install redis-server
sudo systemctl start redis-server
```

**Docker:**
```bash
docker run -d -p 6379:6379 --name redis redis:alpine
```

## 2. Test Redis
```bash
redis-cli ping
# Should return: PONG
```

## 3. Install Python packages
```bash
cd /Users/andrewbrown/Sites/noosphere/github/voice-forge/backend
source venv/bin/activate  # or venv-py311/bin/activate
pip install celery redis flower
```

## 4. Test Celery configuration
```bash
python test_celery.py
```

## 5. Start Celery worker
```bash
celery -A celery_app worker --loglevel=info --queues=crawl,process,rag
```

## 6. Start API server (in another terminal)
```bash
uvicorn api.main:app --reload
```

## 7. Optional: Start Flower monitoring
```bash
celery -A celery_app flower --port=5555
# Visit: http://localhost:5555
```

## Troubleshooting

**Redis not found:**
```bash
# Check if installed
which redis-server
redis-server --version
```

**Connection refused:**
```bash
# Check Redis status
ps aux | grep redis
redis-cli info
```

**Import errors:**
```bash
# Check Python path
python -c "import sys; print(sys.path)"
python -c "from celery_app import celery_app; print('OK')"
```

**Worker not starting:**
```bash
# Debug mode
celery -A celery_app worker --loglevel=debug
```
