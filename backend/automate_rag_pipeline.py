#!/usr/bin/env python3
"""
VoiceForge RAG Pipeline Automation Script
Complete automation for optimizing your VoiceForge RAG system
"""

import os
import sys
import time
import subprocess
import json
import argparse
from datetime import datetime

# ANSI color codes for better output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_banner():
    """Print the VoiceForge banner."""
    banner = f"""
{Colors.HEADER}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║                    VoiceForge RAG Pipeline                   ║
║              Content Processing Optimization                 ║
╚══════════════════════════════════════════════════════════════╝
{Colors.ENDC}
"""
    print(banner)

def print_step(step_num, title, description=""):
    """Print a step header."""
    print(f"\n{Colors.OKBLUE}{Colors.BOLD}📋 Step {step_num}: {title}{Colors.ENDC}")
    if description:
        print(f"   {description}")

def print_success(message):
    """Print a success message."""
    print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")

def print_warning(message):
    """Print a warning message."""
    print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")

def print_error(message):
    """Print an error message."""
    print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")

def print_info(message):
    """Print an info message."""
    print(f"{Colors.OKCYAN}ℹ️  {message}{Colors.ENDC}")

def run_command(command, description="", capture_output=False):
    """
    Run a shell command with error handling.
    
    Args:
        command: Command to run (list or string)
        description: Description of what the command does
        capture_output: Whether to capture and return output
        
    Returns:
        (success, output) tuple
    """
    if description:
        print(f"   Running: {description}")
    
    try:
        if isinstance(command, str):
            command = command.split()
        
        if capture_output:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            return True, result.stdout
        else:
            result = subprocess.run(command, check=True)
            return True, ""
            
    except subprocess.CalledProcessError as e:
        error_msg = f"Command failed: {' '.join(command)}"
        if capture_output and e.stderr:
            error_msg += f"\nError: {e.stderr}"
        print_error(error_msg)
        return False, ""
    except Exception as e:
        print_error(f"Unexpected error running command: {e}")
        return False, ""

def check_dependencies():
    """Check if required dependencies are installed."""
    print_step(1, "Checking Dependencies", "Verifying required packages are installed")
    
    dependencies_ok = True
    
    # Check Python packages
    required_packages = [
        ('sentence_transformers', 'sentence-transformers'),
        ('sklearn', 'scikit-learn'),
        ('numpy', 'numpy'),
        ('sqlalchemy', 'SQLAlchemy'),
    ]
    
    for package, pip_name in required_packages:
        try:
            __import__(package)
            print_success(f"{pip_name} is installed")
        except ImportError:
            print_warning(f"{pip_name} is not installed")
            print_info(f"Install with: pip install {pip_name}")
            dependencies_ok = False
    
    return dependencies_ok

def get_organization_id():
    """Get organization ID from user or environment."""
    # Check environment variable first
    org_id = os.environ.get('VOICEFORGE_ORG_ID')
    
    if org_id:
        print_info(f"Using organization ID from environment: {org_id}")
        return org_id
    
    # Prompt user
    print_info("Organization ID is required for multi-tenant operation")
    org_id = input("Enter your organization ID: ").strip()
    
    if not org_id:
        print_error("Organization ID is required")
        return None
    
    return org_id

def run_optimization_pipeline(org_id, options=None):
    """
    Run the main optimization pipeline.
    
    Args:
        org_id: Organization ID
        options: Additional options dictionary
        
    Returns:
        Success status
    """
    options = options or {}
    
    print_step(2, "Running Content Processing Pipeline", "Optimizing content chunking and embeddings")
    
    # Build command
    command = [
        sys.executable, 
        "optimized_processing_pipeline.py",
        "--org-id", org_id
    ]
    
    # Add optional parameters
    if options.get('chunk_size'):
        command.extend(["--chunk-size", str(options['chunk_size'])])
    
    if options.get('batch_size'):
        command.extend(["--batch-size", str(options['batch_size'])])
    
    if options.get('max_content'):
        command.extend(["--max-content", str(options['max_content'])])
    
    # Run the optimization
    success, output = run_command(command, "Content processing optimization", capture_output=True)
    
    if success:
        print_success("Content processing completed successfully")
        
        # Try to parse the JSON output for summary
        try:
            lines = output.strip().split('\n')
            json_start = -1
            for i, line in enumerate(lines):
                if line.strip() == "FINAL RESULTS (JSON):":
                    json_start = i + 1
                    break
            
            if json_start >= 0:
                json_text = '\n'.join(lines[json_start:])
                results = json.loads(json_text)
                
                print_info("Pipeline Results:")
                print(f"   • Success: {results.get('success', 'Unknown')}")
                print(f"   • Ready for RAG: {results.get('ready_for_rag', 'Unknown')}")
                
                improvements = results.get('improvements', {})
                print(f"   • Content processed: +{improvements.get('content_processed', 0)}")
                print(f"   • Chunks created: +{improvements.get('chunks_created', 0)}")
                print(f"   • Embeddings generated: +{improvements.get('embeddings_generated', 0)}")
                
                performance = results.get('performance', {})
                if performance.get('total_time'):
                    print(f"   • Total time: {performance['total_time']:.2f} seconds")
                
        except (json.JSONDecodeError, IndexError):
            print_info("Could not parse detailed results, but pipeline completed")
        
        return True
    else:
        print_error("Content processing failed")
        return False

def test_rag_system(org_id):
    """Test the RAG system with sample queries."""
    print_step(3, "Testing RAG System", "Running sample queries to validate functionality")
    
    test_queries = [
        "What are your main services?",
        "How can I get support?",
        "What makes your company different?"
    ]
    
    try:
        # Import here to avoid issues if not available
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from database.session import get_db_session
        from database.db import Database
        from processor.rag_service import RAGService
        
        # Initialize services
        session = get_db_session()
        if hasattr(session, '__next__'):
            session = next(session)
        
        db = Database(session)
        rag_service = RAGService(db)
        
        success_count = 0
        
        for i, query in enumerate(test_queries, 1):
            print_info(f"Testing query {i}: '{query}'")
            
            try:
                # Test chunk retrieval
                chunks = rag_service.search_chunks(
                    query=query,
                    top_k=3,
                    org_id=org_id
                )
                
                if chunks:
                    print_success(f"Found {len(chunks)} relevant chunks")
                    
                    # Test content generation
                    response = rag_service.generate_content(
                        query=query,
                        platform="general",
                        tone="professional",
                        top_k=3,
                        org_id=org_id
                    )
                    
                    if hasattr(response, 'text') and response.text:
                        print_success(f"Generated response ({len(response.text)} characters)")
                        print(f"   Preview: {response.text[:100]}...")
                        success_count += 1
                    else:
                        print_warning("No response text generated")
                else:
                    print_warning("No relevant chunks found")
                    
            except Exception as e:
                print_error(f"Query test failed: {e}")
        
        session.close()
        
        if success_count > 0:
            print_success(f"RAG system is working! {success_count}/{len(test_queries)} queries successful")
            return True
        else:
            print_warning("RAG system needs attention - no successful queries")
            return False
            
    except Exception as e:
        print_error(f"RAG testing failed: {e}")
        return False

def generate_usage_examples(org_id):
    """Generate usage examples for the user."""
    print_step(4, "Usage Examples", "Generating code examples for using your RAG system")
    
    examples = f"""
# Example 1: Basic RAG Query
from database.session import get_db_session
from database.db import Database
from processor.rag_service import RAGService

session = next(get_db_session())
db = Database(session)
rag_service = RAGService(db)

# Search for relevant content
chunks = rag_service.search_chunks(
    query="your question here",
    top_k=5,
    org_id="{org_id}"
)

# Generate response
response = rag_service.generate_content(
    query="your question here",
    platform="general",  # or "twitter", "email", "blog"
    tone="professional",  # or "casual", "enthusiastic"
    org_id="{org_id}"
)

print(response.text)

# Example 2: Platform-specific generation
twitter_response = rag_service.generate_content(
    query="What makes your product unique?",
    platform="twitter",
    tone="enthusiastic",
    org_id="{org_id}"
)

email_response = rag_service.generate_content(
    query="How can I integrate your API?",
    platform="email",
    tone="professional",
    org_id="{org_id}"
)

# Example 3: Filtered search
specific_chunks = rag_service.search_chunks(
    query="API documentation",
    domain="your-domain.com",  # Filter by specific domain
    content_type="documentation",  # Filter by content type
    top_k=10,
    org_id="{org_id}"
)
"""
    
    # Write examples to file
    try:
        with open("rag_usage_examples.py", "w") as f:
            f.write(examples)
        print_success("Usage examples saved to 'rag_usage_examples.py'")
    except Exception as e:
        print_warning(f"Could not save examples file: {e}")
    
    print_info("Basic usage pattern:")
    print("   1. Search for relevant chunks")
    print("   2. Generate content using those chunks")
    print("   3. Customize by platform and tone")

def print_final_summary(success, org_id):
    """Print final summary and next steps."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}🎉 VoiceForge RAG Pipeline Complete!{Colors.ENDC}")
    
    if success:
        print_success("Your RAG system is optimized and ready to use!")
        
        print(f"\n{Colors.OKBLUE}{Colors.BOLD}Next Steps:{Colors.ENDC}")
        print("1. 🚀 Start using the RAG system in your application")
        print("2. 🔍 Test with different query types and platforms")
        print("3. 📊 Monitor performance and adjust parameters as needed")
        print("4. 🔄 Re-run optimization after adding new content")
        
        print(f"\n{Colors.OKBLUE}{Colors.BOLD}Quick Test:{Colors.ENDC}")
        print(f"python -c \"")
        print(f"from database.session import get_db_session")
        print(f"from database.db import Database")
        print(f"from processor.rag_service import RAGService")
        print(f"session = next(get_db_session())")
        print(f"db = Database(session)")
        print(f"rag = RAGService(db)")
        print(f"print(rag.search_chunks('your query', org_id='{org_id}'))\"")
        
        print(f"\n{Colors.OKBLUE}{Colors.BOLD}Automation:{Colors.ENDC}")
        print(f"# Set environment variable to skip prompts")
        print(f"export VOICEFORGE_ORG_ID='{org_id}'")
        print(f"# Run optimization anytime")
        print(f"python automate_rag_pipeline.py --auto")
        
    else:
        print_warning("Pipeline completed with issues")
        
        print(f"\n{Colors.WARNING}{Colors.BOLD}Troubleshooting:{Colors.ENDC}")
        print("1. ❓ Check that you have crawled content in your database")
        print("2. ❓ Verify all required Python packages are installed")
        print("3. ❓ Ensure your database connection is working")
        print("4. ❓ Check logs for specific error messages")
        
        print(f"\n{Colors.INFO}Get help:")
        print("- Check the error messages above")
        print("- Run with --debug for more detailed output")
        print("- Verify your organization ID is correct")

def main():
    """Main automation function."""
    parser = argparse.ArgumentParser(description='VoiceForge RAG Pipeline Automation')
    parser.add_argument('--org-id', help='Organization ID (or set VOICEFORGE_ORG_ID env var)')
    parser.add_argument('--auto', action='store_true', help='Run automatically without prompts')
    parser.add_argument('--chunk-size', type=int, default=400, help='Chunk size for processing')
    parser.add_argument('--batch-size', type=int, default=32, help='Batch size for embeddings')
    parser.add_argument('--max-content', type=int, help='Maximum content items to process')
    parser.add_argument('--skip-deps', action='store_true', help='Skip dependency checking')
    parser.add_argument('--skip-test', action='store_true', help='Skip RAG system testing')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    start_time = time.time()
    
    # Get organization ID
    org_id = args.org_id or get_organization_id()
    if not org_id:
        print_error("Cannot proceed without organization ID")
        sys.exit(1)
    
    overall_success = True
    
    # Step 1: Check dependencies (unless skipped)
    if not args.skip_deps:
        if not check_dependencies():
            if not args.auto:
                continue_anyway = input("\nContinue anyway? (y/N): ").strip().lower()
                if continue_anyway != 'y':
                    print_error("Please install missing dependencies and try again")
                    sys.exit(1)
            else:
                print_error("Missing dependencies in auto mode")
                sys.exit(1)
    
    # Step 2: Run optimization pipeline
    options = {
        'chunk_size': args.chunk_size,
        'batch_size': args.batch_size,
        'max_content': args.max_content
    }
    
    pipeline_success = run_optimization_pipeline(org_id, options)
    if not pipeline_success:
        overall_success = False
    
    # Step 3: Test RAG system (unless skipped)
    if not args.skip_test and pipeline_success:
        test_success = test_rag_system(org_id)
        if not test_success:
            overall_success = False
    
    # Step 4: Generate usage examples
    generate_usage_examples(org_id)
    
    # Final summary
    total_time = time.time() - start_time
    print(f"\n{Colors.OKCYAN}Total execution time: {total_time:.2f} seconds{Colors.ENDC}")
    
    print_final_summary(overall_success, org_id)
    
    # Exit with appropriate code
    sys.exit(0 if overall_success else 1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Operation cancelled by user{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
