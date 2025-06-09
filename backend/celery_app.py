"""
Celery configuration for VoiceForge distributed task processing.

This module sets up Celery with Redis as the message broker for handling
long-running tasks like web crawling and content processing.
"""
import os
from celery import Celery
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "voiceforge",
    broker=REDIS_URL,
    backend=None,  # Disable result backend to avoid serialization issues
    include=[
        "crawler.tasks",      # Crawling tasks
        "processor.tasks",    # Content processing tasks
        "processor.rag_tasks", # RAG processing tasks
        "signals.tasks"       # Signal automation tasks
    ]
)

# Celery configuration - No result backend to avoid all serialization issues
celery_app.conf.update(
    # Task serialization
    task_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    
    # Task execution
    task_always_eager=False,
    
    # Worker configuration
    worker_prefetch_multiplier=1,
    
    # Disable all result-related features
    task_ignore_result=True,
    result_backend=None,
)

# Task retry configuration - DISABLED for testing to avoid serialization issues
# RETRY_KWARGS = {
#     "autoretry_for": (Exception,),
#     "retry_kwargs": {"max_retries": 3, "countdown": 60},
#     "retry_backoff": True,
#     "retry_jitter": False,
# }

# Import tasks to register them
try:
    from crawler import tasks as crawler_tasks
    print("✅ Crawler tasks imported successfully")
except ImportError as e:
    print(f"⚠️  Warning: Could not import crawler tasks: {e}")
    print("💡 Run: pip install -r requirements.txt")

try:
    from processor import tasks as processor_tasks  
    print("✅ Processor tasks imported successfully")
except ImportError as e:
    print(f"⚠️  Warning: Could not import processor tasks: {e}")
    
try:
    from processor import rag_tasks
    print("✅ RAG tasks imported successfully")
except ImportError as e:
    print(f"⚠️  Warning: Could not import RAG tasks: {e}")

try:
    from signals import tasks as signal_tasks
    print("✅ Signal tasks imported successfully")
except ImportError as e:
    print(f"⚠️  Warning: Could not import signal tasks: {e}")

if __name__ == "__main__":
    celery_app.start()