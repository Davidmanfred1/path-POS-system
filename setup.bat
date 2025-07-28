@echo off
REM Pathway Pharmacy POS System - Windows Setup Script
REM This script sets up the system using uv for fast dependency installation

echo ============================================================
echo 🏥 Pathway Pharmacy POS System - Windows Setup
echo    Fast setup using uv for dependency management
echo ============================================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo ✓ Python is available

REM Install uv
echo 📦 Installing uv...
python -m pip install uv
if errorlevel 1 (
    echo ✗ Failed to install uv
    echo Falling back to regular pip...
    goto :pip_install
)

echo ✓ uv installed successfully

REM Install dependencies with uv
echo 📦 Installing dependencies with uv...
uv pip install -r requirements.txt
if errorlevel 1 (
    echo ✗ uv installation failed, trying pip...
    goto :pip_install
)

echo ✓ Dependencies installed with uv

echo.
echo 📋 Database Options:
echo    SQLite (default) - No additional setup required
echo    PostgreSQL - Requires additional dependencies
echo.
set /p pg_choice="Do you want PostgreSQL support? (y/N): "
if /i "%pg_choice%"=="y" (
    echo 📦 Installing PostgreSQL dependencies...
    uv pip install -r requirements-postgresql.txt
    if errorlevel 1 (
        echo ⚠️  PostgreSQL dependencies failed to install
        echo    You can install them later with:
        echo    uv pip install -r requirements-postgresql.txt
        echo    Or see requirements-postgresql.txt for troubleshooting
    )
) else (
    echo ✓ Using SQLite (default) - no additional dependencies needed
)

goto :setup_env

:pip_install
echo 📦 Installing dependencies with pip...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ✗ Failed to install dependencies
    echo.
    echo ⚠️  Common solutions:
    echo    1. Make sure you have Python 3.8+ installed
    echo    2. Try: python -m pip install --upgrade pip
    echo    3. For PostgreSQL issues, see requirements-postgresql.txt
    pause
    exit /b 1
)
echo ✓ Dependencies installed with pip

:setup_env
REM Setup environment file
if not exist .env (
    if exist .env.example (
        copy .env.example .env >nul
        echo ✓ Created .env file from .env.example
    ) else (
        echo ⚠️  Warning: .env.example not found
    )
) else (
    echo ✓ .env file already exists
)

echo.
echo ============================================================
echo 🎉 Setup completed successfully!
echo.
echo 📋 Next steps:
echo    1. Initialize database: python run.py --init
echo    2. Or start immediately: python run.py
echo.
echo 🌐 Access points:
echo    • POS Interface: http://localhost:8000
echo    • API Docs: http://localhost:8000/docs
echo    • Expiry Dashboard: http://localhost:8000#expiry
echo.
echo 🔑 Default credentials:
echo    • Admin: admin/admin123
echo    • Pharmacist: pharmacist/pharma123
echo    • Cashier: cashier/cashier123
echo ============================================================
echo.
pause
