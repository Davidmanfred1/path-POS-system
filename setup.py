#!/usr/bin/env python3
"""
Pathway Pharmacy POS System - Setup Script

This script automatically sets up the Pathway POS system using uv for fast dependency installation.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(f"   Command: {command}")
        print(f"   Error: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("✗ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} is compatible")
    return True


def install_uv():
    """Install uv if not already installed."""
    try:
        subprocess.run(["uv", "--version"], check=True, capture_output=True)
        print("✓ uv is already installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("📦 Installing uv...")
        return run_command("pip install uv", "uv installation")


def install_dependencies():
    """Install project dependencies using uv with fallback options."""

    print("\n📦 Installation Options:")
    print("   1. Full installation (recommended)")
    print("   2. Minimal installation (if having build issues)")
    print("   3. Core only (fastest, basic features)")

    while True:
        choice = input("\nChoose installation type (1/2/3) [1]: ").strip()
        if choice in ['', '1']:
            requirements_file = "requirements.txt"
            install_type = "full installation"
            break
        elif choice == '2':
            requirements_file = "requirements-minimal.txt"
            install_type = "minimal installation"
            break
        elif choice == '3':
            requirements_file = "requirements-minimal.txt"
            install_type = "core installation"
            break
        else:
            print("Please enter 1, 2, or 3")

    if not Path(requirements_file).exists():
        print(f"✗ {requirements_file} not found")
        return False

    # Install main dependencies
    success = run_command(f"uv pip install -r {requirements_file}", install_type)

    if not success:
        print(f"\n💡 Trying fallback to pip for {install_type}...")
        success = run_command(f"pip install -r {requirements_file}", f"fallback {install_type}")

    if success and choice in ['', '1']:
        # Ask about optional features for full installation
        print("\n📋 Optional Features:")

        # PostgreSQL support
        pg_choice = input("Install PostgreSQL support? (y/N): ").strip().lower()
        if pg_choice in ['y', 'yes']:
            print("📦 Installing PostgreSQL dependencies...")
            pg_success = run_command("uv pip install -r requirements-postgresql.txt", "PostgreSQL dependencies")
            if not pg_success:
                run_command("pip install -r requirements-postgresql.txt", "PostgreSQL dependencies (fallback)")

        # Optional features
        opt_choice = input("Install optional features (PDF, Excel, Barcode)? (y/N): ").strip().lower()
        if opt_choice in ['y', 'yes']:
            print("📦 Installing optional dependencies...")
            opt_success = run_command("uv pip install -r requirements-optional.txt", "optional dependencies")
            if not opt_success:
                print("⚠️  Some optional features failed to install")
                print("   You can install them later with:")
                print("   uv pip install -r requirements-optional.txt")

        # Development tools
        dev_choice = input("Install development tools? (y/N): ").strip().lower()
        if dev_choice in ['y', 'yes']:
            print("📦 Installing development dependencies...")
            run_command("uv pip install -r requirements-dev.txt", "development dependencies")

    return success


def setup_environment():
    """Set up environment file if it doesn't exist."""
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_file.exists():
        print("✓ .env file already exists")
        return True
    
    if not env_example.exists():
        print("✗ .env.example not found")
        return False
    
    try:
        env_file.write_text(env_example.read_text())
        print("✓ Created .env file from .env.example")
        print("   You can customize settings in .env if needed")
        return True
    except Exception as e:
        print(f"✗ Failed to create .env file: {e}")
        return False


def main():
    """Main setup function."""
    print("=" * 60)
    print("🏥 Pathway Pharmacy POS System - Setup")
    print("   Fast setup using uv for dependency management")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install uv
    if not install_uv():
        print("\n💡 Alternative: You can install dependencies with regular pip:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n💡 Trying fallback to pip...")
        if not run_command("pip install -r requirements.txt", "fallback dependency installation"):
            print("\n⚠️  Dependency installation failed. Common solutions:")
            print("   1. Make sure you have Python 3.8+ installed")
            print("   2. Try running: python -m pip install --upgrade pip")
            print("   3. For PostgreSQL issues, see requirements-postgresql.txt")
            sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        print("⚠️  Warning: Could not set up .env file")
        print("   You may need to create it manually from .env.example")
    
    print("\n" + "=" * 60)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("   1. Initialize database: python run.py --init")
    print("   2. Or start immediately: python run.py")
    print("\n🌐 Access points:")
    print("   • POS Interface: http://localhost:8000")
    print("   • API Docs: http://localhost:8000/docs")
    print("   • Expiry Dashboard: http://localhost:8000#expiry")
    print("\n🔑 Default credentials:")
    print("   • Admin: admin/admin123")
    print("   • Pharmacist: pharmacist/pharma123")
    print("   • Cashier: cashier/cashier123")
    print("=" * 60)


if __name__ == "__main__":
    main()
