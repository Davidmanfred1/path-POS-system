#!/usr/bin/env python3
"""
Pathway Pharmacy POS System - Startup Script

This script provides an easy way to start the Pathway POS system with various options.
"""

import argparse
import asyncio
import subprocess
import sys
import os
from pathlib import Path


def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import pydantic
        print("✓ All required dependencies are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Please install dependencies with:")
        print("  python setup.py                     (automatic setup)")
        print("  uv pip install -r requirements.txt  (recommended - faster)")
        print("  pip install -r requirements.txt     (traditional)")
        print("\nFor PostgreSQL support, also run:")
        print("  uv pip install -r requirements-postgresql.txt")
        return False


async def init_database():
    """Initialize the database with sample data."""
    print("Initializing database...")
    try:
        # Import and run the initialization script
        from scripts.init_sample_data import main as init_main
        await init_main()
        print("✓ Database initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        return False


def run_tests():
    """Run the test suite."""
    print("Running tests...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/", "-v", "--tb=short"
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        if result.returncode == 0:
            print("✓ All tests passed")
            return True
        else:
            print("✗ Some tests failed")
            return False
    except Exception as e:
        print(f"✗ Error running tests: {e}")
        return False


def start_server(host="127.0.0.1", port=8000, reload=True):
    """Start the FastAPI server."""
    print(f"Starting Pathway POS server on http://{host}:{port}")
    print("Press Ctrl+C to stop the server")
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--host", host,
            "--port", str(port),
            "--reload" if reload else "--no-reload"
        ])
    except KeyboardInterrupt:
        print("\nServer stopped")
    except Exception as e:
        print(f"✗ Error starting server: {e}")


def main():
    """Main function to handle command line arguments and run the appropriate action."""
    parser = argparse.ArgumentParser(
        description="Pathway Pharmacy POS System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # First time setup (install uv if needed)
  pip install uv
  uv pip install -r requirements.txt

  # Run the system
  python run.py                    # Start the server with default settings
  python run.py --init             # Initialize database and start server
  python run.py --test             # Run tests only
  python run.py --host 0.0.0.0     # Start server accessible from other machines
  python run.py --port 8080        # Start server on port 8080
        """
    )
    
    parser.add_argument(
        "--init", 
        action="store_true",
        help="Initialize database with sample data before starting"
    )
    
    parser.add_argument(
        "--test", 
        action="store_true",
        help="Run tests only (don't start server)"
    )
    
    parser.add_argument(
        "--host", 
        default="127.0.0.1",
        help="Host to bind the server to (default: 127.0.0.1)"
    )
    
    parser.add_argument(
        "--port", 
        type=int,
        default=8000,
        help="Port to bind the server to (default: 8000)"
    )
    
    parser.add_argument(
        "--no-reload", 
        action="store_true",
        help="Disable auto-reload in development mode"
    )
    
    args = parser.parse_args()
    
    # Print banner
    print("=" * 60)
    print("🏥 Pathway Pharmacy POS System")
    print("   Intelligent Pharmacy Management with Expiry Alerts")
    print("   💡 Tip: Use 'uv pip install -r requirements.txt' for faster setup")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Run tests if requested
    if args.test:
        success = run_tests()
        sys.exit(0 if success else 1)
    
    # Initialize database if requested
    if args.init:
        success = asyncio.run(init_database())
        if not success:
            sys.exit(1)
    
    # Start the server
    print("\n🚀 Starting Pathway POS System...")
    print(f"📱 Web Interface: http://{args.host}:{args.port}")
    print(f"📚 API Documentation: http://{args.host}:{args.port}/docs")
    print(f"🔍 Expiry Dashboard: http://{args.host}:{args.port}#expiry")
    print("\n" + "=" * 60)
    
    start_server(
        host=args.host,
        port=args.port,
        reload=not args.no_reload
    )


if __name__ == "__main__":
    main()
