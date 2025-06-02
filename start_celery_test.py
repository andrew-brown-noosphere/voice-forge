#!/usr/bin/env python3
"""
Test Celery setup and start worker
"""

import os
import sys
import subprocess

# Set up Python path
backend_dir = "/Users/andrewbrown/Sites/noosphere/github/voice-forge/backend"
sys.path.insert(0, backend_dir)
os.chdir(backend_dir)

def test_celery_import():
    """Test if we can import the Celery app"""
    print("🔍 TESTING CELERY IMPORT")
    print("=" * 40)
    
    try:
        from celery_app import celery_app
        print("✅ Celery app imported successfully")
        print(f"   App name: {celery_app.main}")
        print(f"   Broker: {celery_app.conf.broker_url}")
        print(f"   Backend: {celery_app.conf.result_backend}")
        
        # Check registered tasks
        tasks = list(celery_app.tasks.keys())
        crawl_tasks = [t for t in tasks if 'crawl' in t]
        
        print(f"   Total tasks: {len(tasks)}")
        print(f"   Crawl tasks: {len(crawl_tasks)}")
        
        for task in crawl_tasks:
            print(f"     📋 {task}")
            
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_redis():
    """Check Redis connection"""
    print("\n🔍 TESTING REDIS")
    print("=" * 40)
    
    try:
        result = subprocess.run(["redis-cli", "ping"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and "PONG" in result.stdout:
            print("✅ Redis is running")
            return True
        else:
            print("❌ Redis not responding")
            print("   Starting Redis...")
            subprocess.run(["brew", "services", "start", "redis"])
            return False
    except Exception as e:
        print(f"❌ Redis check failed: {e}")
        return False

def start_worker():
    """Start Celery worker"""
    print("\n🚀 STARTING CELERY WORKER")
    print("=" * 40)
    print("Press Ctrl+C to stop")
    print("")
    
    try:
        # Set environment variables
        env = os.environ.copy()
        env['PYTHONPATH'] = backend_dir
        
        subprocess.run([
            "celery", "-A", "celery_app", "worker", 
            "--loglevel=info",
            "--concurrency=2",
            "--queues=crawl,process,rag"
        ], env=env)
        
    except KeyboardInterrupt:
        print("\n✅ Worker stopped")
    except Exception as e:
        print(f"❌ Worker failed: {e}")

if __name__ == "__main__":
    print("🔧 CELERY SETUP AND TEST")
    print("=" * 50)
    
    # Test Redis
    redis_ok = check_redis()
    
    # Test Celery import
    celery_ok = test_celery_import()
    
    if celery_ok and redis_ok:
        print("\n" + "=" * 50)
        print("✅ ALL CHECKS PASSED")
        print("=" * 50)
        
        try:
            response = input("\nStart Celery worker? (y/n): ").lower()
            if response == 'y':
                start_worker()
        except KeyboardInterrupt:
            print("\nExiting...")
    else:
        print("\n" + "=" * 50)
        print("❌ SETUP ISSUES FOUND")
        print("=" * 50)
        
        if not redis_ok:
            print("• Fix Redis: brew services start redis")
        if not celery_ok:
            print("• Check Python path and dependencies")
