#!/usr/bin/env python3
"""
Check backend logs and Celery status
"""

import subprocess
import sys
import os

def check_celery_workers():
    """Check if Celery workers are running"""
    print("🔍 CHECKING CELERY WORKERS")
    print("=" * 40)
    
    try:
        os.chdir("/Users/andrewbrown/Sites/noosphere/github/voice-forge/backend")
        
        # Check worker status
        result = subprocess.run(
            ["celery", "-A", "celery_app", "status"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ Celery workers are running:")
            print(result.stdout)
        else:
            print("❌ No Celery workers found")
            print("Error:", result.stderr)
            print("\nTo start workers:")
            print("cd /Users/andrewbrown/Sites/noosphere/github/voice-forge/backend")
            print("celery -A celery_app worker --loglevel=info")
            
    except FileNotFoundError:
        print("❌ Celery command not found")
        print("Install with: pip install celery")
    except subprocess.TimeoutExpired:
        print("❌ Celery status check timed out")
    except Exception as e:
        print(f"❌ Error checking Celery: {e}")

def check_redis():
    """Check if Redis is running"""
    print("\n🔍 CHECKING REDIS")
    print("=" * 40)
    
    try:
        result = subprocess.run(
            ["redis-cli", "ping"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and "PONG" in result.stdout:
            print("✅ Redis is running")
        else:
            print("❌ Redis not responding")
            print("Start with: brew services start redis")
            
    except FileNotFoundError:
        print("❌ Redis not installed")
        print("Install with: brew install redis")
    except Exception as e:
        print(f"❌ Error checking Redis: {e}")

def check_processes():
    """Check for running processes"""
    print("\n🔍 CHECKING PROCESSES")
    print("=" * 40)
    
    # Check for Python processes that might be workers
    try:
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True
        )
        
        celery_processes = [line for line in result.stdout.split('\n') if 'celery' in line.lower()]
        
        if celery_processes:
            print("✅ Found Celery processes:")
            for proc in celery_processes:
                print(f"   {proc}")
        else:
            print("❌ No Celery processes found")
            
    except Exception as e:
        print(f"❌ Error checking processes: {e}")

def start_worker():
    """Offer to start a Celery worker"""
    print("\n🚀 STARTING CELERY WORKER")
    print("=" * 40)
    
    try:
        os.chdir("/Users/andrewbrown/Sites/noosphere/github/voice-forge/backend")
        
        print("Starting Celery worker...")
        print("Press Ctrl+C to stop")
        
        # Start worker in foreground so we can see output
        subprocess.run([
            "celery", "-A", "celery_app", "worker", 
            "--loglevel=info",
            "--concurrency=1"
        ])
        
    except KeyboardInterrupt:
        print("\n✅ Worker stopped")
    except Exception as e:
        print(f"❌ Error starting worker: {e}")

if __name__ == "__main__":
    check_redis()
    check_celery_workers()
    check_processes()
    
    print("\n" + "=" * 60)
    print("🎯 DIAGNOSIS COMPLETE")
    print("=" * 60)
    
    # Ask if user wants to start a worker
    try:
        response = input("\nDo you want to start a Celery worker now? (y/n): ").lower()
        if response == 'y':
            start_worker()
    except KeyboardInterrupt:
        print("\nExiting...")
