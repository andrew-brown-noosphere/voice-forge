#!/usr/bin/env python3
"""
Test Environment Loading
Quick test to verify .env file is being loaded correctly
"""

import os
import sys

# Load environment variables from .env file
def load_env_file():
    """Load environment variables from .env file"""
    backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(backend_path, '.env')
    
    print(f"🔍 Looking for .env file at: {env_path}")
    
    if os.path.exists(env_path):
        print(f"✅ Found .env file")
        
        # Read and show file contents (without sensitive values)
        with open(env_path, 'r') as f:
            lines = f.readlines()
            print(f"📄 .env file has {len(lines)} lines")
            
            for i, line in enumerate(lines):
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Set environment variable
                    os.environ[key] = value
                    
                    # Show key (mask value for security)
                    if 'KEY' in key or 'PASSWORD' in key:
                        masked_value = value[:4] + '*' * (len(value) - 8) + value[-4:] if len(value) > 8 else '*' * len(value)
                        print(f"   Line {i+1}: {key} = {masked_value}")
                    else:
                        print(f"   Line {i+1}: {key} = {value}")
                elif line.startswith('#'):
                    print(f"   Line {i+1}: (comment)")
                elif not line:
                    print(f"   Line {i+1}: (empty)")
                else:
                    print(f"   Line {i+1}: {line[:30]}... (unrecognized format)")
        
        return True
    else:
        print(f"❌ .env file not found")
        return False

def test_environment():
    """Test environment variables after loading"""
    print(f"\n🧪 Testing Environment Variables:")
    
    important_vars = ['OPENAI_API_KEY', 'DATABASE_URL', 'VECTOR_DB_PROVIDER', 'PYTHONPATH']
    
    for var in important_vars:
        value = os.environ.get(var)
        if value:
            if 'KEY' in var or 'PASSWORD' in var:
                masked = value[:4] + '*' * 10 + value[-4:] if len(value) > 8 else '*' * len(value)
                print(f"   ✅ {var}: {masked}")
            else:
                print(f"   ✅ {var}: {value}")
        else:
            print(f"   ❌ {var}: NOT SET")

def main():
    print("🔧 Environment Loading Test")
    print("=" * 40)
    
    # Load .env file
    success = load_env_file()
    
    if success:
        test_environment()
        print(f"\n🎯 Environment loading: ✅ SUCCESS")
    else:
        print(f"\n❌ Environment loading: FAILED")
        print(f"Please check that your .env file exists and is properly formatted.")

if __name__ == "__main__":
    main()
