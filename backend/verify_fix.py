#!/usr/bin/env python3
"""
Quick verification that the fix is properly installed.
"""

import os
import sys

def verify_fix():
    """Verify that all fix components are in place."""
    
    print("🔍 VERIFYING RAG SERVICE FIX")
    print("=" * 40)
    
    base_path = "/Users/andrewbrown/Sites/noosphere/github/voice-forge/backend"
    
    # Check files exist
    files_to_check = [
        "services/simplified_rag_service.py",
        "services/enhanced_rag_service.py", 
        "services/enhanced_rag_service_backup.py",
        "test_fixed_rag.py"
    ]
    
    all_good = True
    
    for file_path in files_to_check:
        full_path = os.path.join(base_path, file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING!")
            all_good = False
    
    if all_good:
        print(f"\n🎯 All fix components are in place!")
        print(f"\n📋 Next steps:")
        print(f"1. Run: python test_fixed_rag.py")
        print(f"2. Check that context retrieval works")
        print(f"3. Test your content generation")
        
        print(f"\n💡 What changed:")
        print(f"- enhanced_rag_service.py now uses simplified version")
        print(f"- Complex crawls table joins are bypassed")
        print(f"- Simple, reliable queries that actually work")
        
        return True
    else:
        print(f"\n❌ Some components are missing!")
        return False

if __name__ == "__main__":
    verify_fix()
