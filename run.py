#!/usr/bin/env python3
"""
Production Monitoring System - Universal Run Script
Runs on Windows, macOS, and Linux
"""

import os
import sys
import subprocess
import platform

def print_header():
    """Print application header"""
    print("\n" + "="*60)
    print("  PRODUCTION MONITORING SYSTEM - QUICK START")
    print("  Textile Spinning Production Management")
    print("="*60 + "\n")

def check_python():
    """Check if Python is installed"""
    print("[OK] Python detected!")
    print(f"   Version: {platform.python_version()}\n")

def create_virtualenv():
    """Create virtual environment if it doesn't exist"""
    venv_dir = "venv"
    
    if not os.path.exists(venv_dir):
        print("[*] Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", venv_dir])
        print("[OK] Virtual environment created!\n")
    else:
        print("[OK] Virtual environment already exists!\n")

def get_venv_python():
    """Get path to virtual environment Python"""
    if platform.system() == "Windows":
        return os.path.join("venv", "Scripts", "python.exe")
    else:
        return os.path.join("venv", "bin", "python")

def install_dependencies():
    """Install required dependencies"""
    print("[*] Installing dependencies...")
    venv_python = get_venv_python()
    
    if not os.path.exists(venv_python):
        print("[!] Virtual environment Python not found!")
        sys.exit(1)
    
    subprocess.run([venv_python, "-m", "pip", "install", "-q", "-r", "requirements.txt"])
    print("[OK] Dependencies installed!\n")

def start_application():
    """Start the Flask application"""
    print(">> Starting Production Monitoring System...\n")
    print("="*60)
    print("  [OK] Server is running!")
    print()
    print("  Open your browser and go to:")
    print("     http://localhost:5000/")
    print()
    print("  Login Credentials:")
    print("     Username: admin")
    print("     Password: admin123")
    print()
    print("  Tips:")
    print("     - Press Ctrl+C to stop the server")
    print("     - If port 5000 is busy, edit app.py and change port")
    print("     - Check browser console (F12) for debug info")
    print()
    print("="*60 + "\n")
    
    venv_python = get_venv_python()
    try:
        subprocess.run([venv_python, "app.py"])
    except KeyboardInterrupt:
        print("\n\nServer stopped by user. Goodbye!")
        sys.exit(0)

def main():
    """Main execution"""
    try:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        print_header()
        check_python()
        create_virtualenv()
        install_dependencies()
        start_application()
        
    except Exception as e:
        print(f"\n[!] Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
