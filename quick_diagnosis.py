#!/usr/bin/env python3
"""
Quick diagnosis for recently broken VoiceForge content generation.
"""

import requests
import json
import psycopg2
import os
from datetime import datetime

def quick_diagnosis():
    """Quick diagnosis of what broke in the last hour."""
    
    print("🚨 VoiceForge Quick Diagnosis - Recently Broken")
    print("=" * 50)
    print(f"Time: {datetime.now().isoformat()}")
    print("")
    
    # Get token
    token = input("🔑 Paste your JWT token: ").strip()
    if not token:
        print("❌ No token provided")
        return
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print("🔍 Testing what broke...")
    
    # 1. Test basic auth
    print("\n1️⃣ Testing authentication...")
    try:
        auth_response = requests.get('http://localhost:8000/auth/me', headers=headers, timeout=5)
        if auth_response.status_code == 200:
            print("✅ Authentication working")
        else:
            print(f"❌ Auth broken: {auth_response.status_code}")
            print(f"   Response: {auth_response.text}")
            return
    except Exception as e:
        print(f"❌ Can't reach backend: {e}")
        print("🔧 Is the backend running on port 8000?")
        return
    
    # 2. Test database connection
    print("\n2️⃣ Testing database connection...")
    try:
        db_params = {
            'host': 'localhost',
            'port': '5432', 
            'database': 'voiceforge',
            'user': 'postgres',
            'password': 'postgres'
        }
        
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        cursor.fetchone()
        print("✅ Database connection working")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("🔧 Check if PostgreSQL is running")
        return
    
    # 3. Test vector extension specifically
    print("\n3️⃣ Testing vector extension...")
    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        
        # Check if extension exists
        cursor.execute("SELECT 1 FROM pg_extension WHERE extname = 'vector';")
        if cursor.fetchone():
            print("✅ Vector extension installed")
            
            # Test vector operation
            cursor.execute("SELECT '[1,2,3]'::vector <-> '[1,2,4]'::vector;")
            result = cursor.fetchone()
            print(f"✅ Vector operations working (distance: {result[0]})")
        else:
            print("❌ Vector extension missing!")
            print("🔧 This might be the issue - extension was removed or DB was reset")
            
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ Vector test failed: {e}")
        print("🔧 This is likely the problem!")
    
    # 4. Test RAG endpoint directly
    print("\n4️⃣ Testing RAG endpoint...")
    test_payload = {
        "query": "test query",
        "platform": "twitter", 
        "tone": "professional",
        "top_k": 3
    }
    
    try:
        response = requests.post(
            'http://localhost:8000/rag/generate',
            headers=headers,
            json=test_payload,
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ RAG endpoint working")
            data = response.json()
            if 'text' in data:
                print(f"   Generated: {data['text'][:50]}...")
            else:
                print("⚠️ No text in response")
        else:
            print(f"❌ RAG endpoint failed")
            print(f"   Error: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ RAG test failed: {e}")
    
    # 5. Quick fixes to try
    print("\n🔧 QUICK FIXES TO TRY:")
    print("1. Restart backend server (Ctrl+C and restart)")
    print("2. If vector extension missing: Connect to DB and run 'CREATE EXTENSION vector;'")
    print("3. Check if any recent changes to database or backend code")
    print("4. Try a different browser/incognito mode")

def quick_vector_fix():
    """Quick fix for vector extension."""
    print("\n🔧 Quick Vector Extension Fix")
    print("=" * 30)
    
    try:
        db_params = {
            'host': 'localhost',
            'port': '5432',
            'database': 'voiceforge', 
            'user': 'postgres',
            'password': 'postgres'
        }
        
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        
        # Try to create extension
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        conn.commit()
        print("✅ Vector extension created/verified")
        
        # Test it
        cursor.execute("SELECT '[1,2,3]'::vector <-> '[1,2,4]'::vector;")
        result = cursor.fetchone()
        print(f"✅ Vector operations working (distance: {result[0]})")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Vector extension fixed! Restart your backend now.")
        
    except Exception as e:
        print(f"❌ Could not fix vector extension: {e}")
        print("🔧 Try manually:")
        print("   psql -d voiceforge -c 'CREATE EXTENSION IF NOT EXISTS vector;'")

if __name__ == "__main__":
    quick_diagnosis()
    
    fix_vectors = input("\n🔧 Try quick vector fix? (y/n): ").strip().lower()
    if fix_vectors == 'y':
        quick_vector_fix()
