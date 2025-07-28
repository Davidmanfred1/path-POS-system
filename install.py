#!/usr/bin/env python3
"""
Pathway Pharmacy POS System - Robust Installation Script

This script tries multiple installation approaches to handle build issues.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command_safe(command, description):
    """Run a command safely and return success status."""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed")
        if e.stderr:
            print(f"   Error: {e.stderr.strip()}")
        return False
    except Exception as e:
        print(f"✗ {description} failed: {e}")
        return False


def try_installation_methods():
    """Try different installation methods until one works."""
    
    methods = [
        {
            "name": "uv with minimal requirements",
            "commands": [
                "pip install uv",
                "uv pip install -r requirements-minimal.txt"
            ]
        },
        {
            "name": "pip with minimal requirements", 
            "commands": [
                "pip install -r requirements-minimal.txt"
            ]
        },
        {
            "name": "pip with individual core packages",
            "commands": [
                "pip install fastapi uvicorn sqlalchemy aiosqlite pydantic python-dotenv"
            ]
        },
        {
            "name": "pip with pre-compiled wheels only",
            "commands": [
                "pip install --only-binary=all fastapi uvicorn sqlalchemy aiosqlite pydantic python-dotenv"
            ]
        }
    ]
    
    for method in methods:
        print(f"\n🔄 Trying: {method['name']}")
        success = True
        
        for command in method['commands']:
            if not run_command_safe(command, f"Running: {command}"):
                success = False
                break
        
        if success:
            print(f"✅ Success with: {method['name']}")
            return True
        else:
            print(f"❌ Failed with: {method['name']}")
    
    return False


def verify_installation():
    """Verify that core dependencies are installed."""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import aiosqlite
        import pydantic
        print("✅ Core dependencies verified successfully")
        return True
    except ImportError as e:
        print(f"❌ Verification failed: {e}")
        return False


def main():
    """Main installation function."""
    print("=" * 60)
    print("🏥 Pathway Pharmacy POS - Robust Installation")
    print("   Trying multiple methods to ensure successful setup")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} is compatible")
    
    # Try installation methods
    if try_installation_methods():
        print("\n🔍 Verifying installation...")
        if verify_installation():
            print("\n" + "=" * 60)
            print("🎉 Installation completed successfully!")
            print("\n📋 Next steps:")
            print("   python run.py --init    # Initialize with sample data")
            print("   python run.py           # Start the server")
            print("\n🌐 Access points:")
            print("   • POS Interface: http://localhost:8000")
            print("   • API Docs: http://localhost:8000/docs")
            print("=" * 60)
        else:
            print("\n❌ Installation verification failed")
            print("Please check the error messages above and try manual installation")
            sys.exit(1)
    else:
        print("\n❌ All installation methods failed")
        print("\n🛠️  Manual installation options:")
        print("1. Try: pip install --upgrade pip setuptools wheel")
        print("2. Try: pip install -r requirements-minimal.txt")
        print("3. Install individual packages:")
        print("   pip install fastapi uvicorn sqlalchemy aiosqlite pydantic")
        print("\n📚 For more help, see the troubleshooting section in README.md")
        sys.exit(1)


if __name__ == "__main__":
    main()
