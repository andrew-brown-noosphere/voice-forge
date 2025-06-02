#!/usr/bin/env python3
"""
Debug script to check Python environment and imports
"""

import sys
import os
from pathlib import Path

print("🔍 VoiceForge Environment Debug")
print("=" * 40)
print()

# 1. Python environment info
print("🐍 Python Environment:")
print(f"   Python version: {sys.version}")
print(f"   Python executable: {sys.executable}")
print(f"   Virtual env: {os.getenv('VIRTUAL_ENV', 'Not set')}")
print(f"   Current working directory: {os.getcwd()}")
print()

# 2. Python path
print("📂 Python Path:")
for i, path in enumerate(sys.path):
    print(f"   {i}: {path}")
print()

# 3. Check if we're in the right directory
backend_dir = Path(__file__).parent
print(f"📍 Backend directory: {backend_dir}")
print(f"   requirements.txt exists: {(backend_dir / 'requirements.txt').exists()}")
print(f"   celery_app.py exists: {(backend_dir / 'celery_app.py').exists()}")
print(f"   venv-py311 exists: {(backend_dir / 'venv-py311').exists()}")
print()

# 4. Test imports one by one
print("📦 Testing Package Imports:")
test_packages = [
    'playwright',
    'sqlalchemy', 
    'celery',
    'redis',
    'fastapi',
    'psycopg2',
    'transformers',
    'sentence_transformers',
    'torch',
    'sklearn',
    'spacy',
    'nltk'
]

installed = []
missing = []

for package in test_packages:
    try:
        module = __import__(package)
        version = getattr(module, '__version__', 'unknown')
        print(f"   ✅ {package} (v{version})")
        installed.append(package)
    except ImportError as e:
        print(f"   ❌ {package}: {e}")
        missing.append(package)

print()
print(f"📊 Summary: {len(installed)} installed, {len(missing)} missing")

if missing:
    print()
    print("💡 Missing packages:")
    for pkg in missing:
        print(f"   - {pkg}")

print()

# 5. Check virtual environment packages
print("🔍 Checking pip packages in current environment:")
try:
    import subprocess
    result = subprocess.run([sys.executable, '-m', 'pip', 'list'], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        lines = result.stdout.split('\n')
        relevant_packages = [line for line in lines if any(pkg in line.lower() for pkg in ['playwright', 'sqlalchemy', 'celery', 'redis', 'fastapi'])]
        if relevant_packages:
            print("   Key packages found:")
            for line in relevant_packages:
                print(f"   {line}")
        else:
            print("   ❌ No key packages found in pip list")
    else:
        print(f"   ❌ Failed to run pip list: {result.stderr}")
except Exception as e:
    print(f"   ❌ Error checking pip packages: {e}")

print()

# 6. Try importing VoiceForge modules
print("🏠 Testing VoiceForge Module Imports:")
try:
    from celery_app import celery_app
    print("   ✅ celery_app imported")
except Exception as e:
    print(f"   ❌ celery_app import failed: {e}")

try:
    from database.session import get_db_session
    print("   ✅ database.session imported")
except Exception as e:
    print(f"   ❌ database.session import failed: {e}")

try:
    from api.models import CrawlConfig
    print("   ✅ api.models imported")
except Exception as e:
    print(f"   ❌ api.models import failed: {e}")

try:
    from crawler.engine import PlaywrightCrawler
    print("   ✅ crawler.engine imported")
except Exception as e:
    print(f"   ❌ crawler.engine import failed: {e}")

print()

# 7. Environment variables
print("🔧 Environment Variables:")
env_vars = ['REDIS_URL', 'DATABASE_URL', 'PYTHONPATH', 'VIRTUAL_ENV']
for var in env_vars:
    value = os.getenv(var)
    if value:
        print(f"   {var}: {value}")
    else:
        print(f"   {var}: Not set")

print()
print("🎯 Recommendations:")
print("   1. Make sure you're in the correct virtual environment")
print("   2. Check if packages are installed: pip list | grep playwright")
print("   3. Try reinstalling: pip install playwright sqlalchemy")
print("   4. Check PYTHONPATH includes the backend directory")
