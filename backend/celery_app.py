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
    backend=REDIS_URL,
    include=[
        "crawler.tasks",      # Crawling tasks
        "processor.tasks",    # Content processing tasks
        "processor.rag_tasks" # RAG processing tasks
    ]
)

# Celery configuration
celery_app.conf.update(
    # Task serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task routing
    task_routes={
        "crawler.tasks.*": {"queue": "crawl"},
        "processor.tasks.*": {"queue": "process"},
        "processor.rag_tasks.*": {"queue": "rag"}
    },
    
    # Result expiration
    result_expires=3600,  # 1 hour
    
    # Task execution
    task_always_eager=False,  # Set to True for synchronous testing
    task_eager_propagates=True,
    
    # Worker configuration
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
    
    # Security
    worker_hijack_root_logger=False,
    worker_log_color=False,
)

# Task retry configuration
RETRY_KWARGS = {
    "autoretry_for": (Exception,),
    "retry_kwargs": {"max_retries": 3, "countdown": 60},
    "retry_backoff": True,
    "retry_jitter": False,
}

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

if __name__ == "__main__":
    celery_app.start()