@echo off
REM Production Monitoring System - Quick Start Script for Windows
REM ============================================================

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║   PRODUCTION MONITORING SYSTEM - QUICK START              ║
echo ║   Textile Spinning Production Management                  ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo ✅ Python detected!
python --version
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    echo ✅ Virtual environment created!
) else (
    echo ✅ Virtual environment already exists!
)

echo.
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo 📥 Installing dependencies...
pip install -q -r requirements.txt
echo ✅ Dependencies installed!

echo.
echo 🚀 Starting Production Monitoring System...
echo.
echo ════════════════════════════════════════════════════════════
echo  ✅ Server is running!
echo.
echo  🌐 Open your browser and go to:
echo     http://localhost:5000/
echo.
echo  📝 Login Credentials:
echo     Username: admin
echo     Password: admin123
echo.
echo  💡 Tips:
echo     - Press Ctrl+C to stop the server
echo     - If port 5000 is busy, edit app.py and change port
echo     - Check browser console (F12) for debug info
echo.
echo ════════════════════════════════════════════════════════════
echo.

python app.py

pause
