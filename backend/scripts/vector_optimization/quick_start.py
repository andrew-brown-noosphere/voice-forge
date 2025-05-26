#!/usr/bin/env python3
"""
VoiceForge Vector Database Quick Start

This script guides you through optimizing your vector database setup
with an interactive menu system.
"""

import os
import sys
import subprocess
from typing import Optional

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

def run_script(script_path: str, description: str) -> bool:
    """Run a Python script and return success status."""
    print(f"\n🚀 {description}")
    print("-" * 50)
    
    try:
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=False, 
                              text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running {script_path}: {str(e)}")
        return False

def show_menu():
    """Display the main menu."""
    print("\n" + "=" * 60)
    print("🚀 VoiceForge Vector Database Optimization")
    print("=" * 60)
    print()
    print("Choose an option:")
    print()
    print("1. 🔍 Run Diagnostic (Check current status)")
    print("2. 🐘 Optimize PostgreSQL + pgvector (Local/Development)")
    print("3. 🌲 Optimize Pinecone (Cloud/Production)")
    print("4. 🧠 Generate Missing Embeddings")
    print("5. ✅ Test OpenAI Connection")
    print("6. 📊 Check Embedding Status Only")
    print("7. 📖 View Optimization Guide")
    print("0. ❌ Exit")
    print()

def main():
    """Main interactive menu."""
    
    # Check if we're in the right directory
    if not os.path.exists('scripts/vector_optimization'):
        print("❌ Please run this script from the backend directory")
        print("   cd /path/to/voice-forge/backend")
        return
    
    while True:
        show_menu()
        
        try:
            choice = input("Enter your choice (0-7): ").strip()
            
            if choice == "0":
                print("\n👋 Goodbye!")
                break
                
            elif choice == "1":
                # Run diagnostic
                success = run_script(
                    "scripts/vector_optimization/vector_db_diagnostic.py",
                    "Running Vector Database Diagnostic"
                )
                if success:
                    print("\n✅ Diagnostic complete! Check the output above for recommendations.")
                
            elif choice == "2":
                # PostgreSQL optimization
                print("\n🐘 PostgreSQL + pgvector Optimization")
                print("This will:")
                print("   • Install pgvector extension")
                print("   • Create optimized indexes")
                print("   • Update database schema")
                print("   • Test performance")
                
                confirm = input("\nProceed? (y/N): ").strip().lower()
                if confirm == 'y':
                    success = run_script(
                        "scripts/vector_optimization/postgresql_optimization.py",
                        "Optimizing PostgreSQL + pgvector"
                    )
                    if success:
                        print("\n✅ PostgreSQL optimization complete!")
                        print("   Next: Generate embeddings (option 4)")
                
            elif choice == "3":
                # Pinecone optimization
                print("\n🌲 Pinecone Cloud Optimization")
                print("This will:")
                print("   • Create Pinecone index")
                print("   • Migrate existing embeddings")
                print("   • Test cloud performance")
                print("   • Update configuration")
                
                # Check for API key
                api_key = os.environ.get('PINECONE_API_KEY')
                if not api_key:
                    print("\n⚠️  PINECONE_API_KEY not found in environment")
                    print("   1. Get API key from: https://app.pinecone.io/")
                    print("   2. Add to .env file: PINECONE_API_KEY=your-key-here")
                    print("   3. Restart this script")
                    input("\nPress Enter to continue...")
                    continue
                
                confirm = input("\nProceed? (y/N): ").strip().lower()
                if confirm == 'y':
                    success = run_script(
                        "scripts/vector_optimization/pinecone_optimization.py",
                        "Optimizing Pinecone Cloud Database"
                    )
                    if success:
                        print("\n✅ Pinecone optimization complete!")
                        print("   Your vectors are now in the cloud!")
                
            elif choice == "4":
                # Generate embeddings
                print("\n🧠 Generate Missing Embeddings")
                print("This will process content and chunks that don't have embeddings yet.")
                
                # Check embedding status first
                try:
                    run_script(
                        "scripts/vector_optimization/generate_embeddings.py --check-only",
                        "Checking Current Embedding Status"
                    )
                except:
                    pass
                
                confirm = input("\nGenerate missing embeddings? (y/N): ").strip().lower()
                if confirm == 'y':
                    success = run_script(
                        "scripts/vector_optimization/generate_embeddings.py",
                        "Generating Missing Embeddings"
                    )
                    if success:
                        print("\n✅ Embedding generation complete!")
                
            elif choice == "5":
                # Test OpenAI
                success = run_script(
                    "scripts/test_openai.py",
                    "Testing OpenAI Connection and API"
                )
                if success:
                    print("\n✅ OpenAI connection working!")
                else:
                    print("\n❌ OpenAI test failed. Check your API key in .env")
                
            elif choice == "6":
                # Check embedding status only
                run_script(
                    "scripts/vector_optimization/generate_embeddings.py",
                    "Checking Embedding Status"
                )
                
            elif choice == "7":
                # View guide
                guide_path = "scripts/vector_optimization/OPTIMIZATION_GUIDE.md"
                if os.path.exists(guide_path):
                    print("\n📖 Opening Optimization Guide...")
                    if sys.platform == "darwin":  # macOS
                        subprocess.run(["open", guide_path])
                    elif sys.platform == "linux":
                        subprocess.run(["xdg-open", guide_path])
                    elif sys.platform == "win32":
                        subprocess.run(["start", guide_path], shell=True)
                    else:
                        print(f"Guide location: {os.path.abspath(guide_path)}")
                else:
                    print("❌ Optimization guide not found")
                
            else:
                print("❌ Invalid choice. Please enter 0-7.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except EOFError:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
