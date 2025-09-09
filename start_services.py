#!/usr/bin/env python3
"""
Startup script to run both the Python ML service and Next.js app
"""
import subprocess
import time
import os
import sys
from pathlib import Path

def start_ml_service():
    """Start the Python ML service"""
    print("🚀 Starting Python ML service...")
    
    # Change to ml_service directory
    ml_service_dir = Path(__file__).parent / "ml_service"
    os.chdir(ml_service_dir)
    
    # Install requirements if needed
    print("📦 Installing Python dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    
    # Start the FastAPI service
    print("🔧 Starting ML service on http://localhost:8000")
    subprocess.run([sys.executable, "-m", "uvicorn", "prediction_service:app", "--host", "0.0.0.0", "--port", "8000", "--reload"])

def start_nextjs_app():
    """Start the Next.js app"""
    print("🚀 Starting Next.js app...")
    
    # Change back to project root
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Install Node.js dependencies if needed
    print("📦 Installing Node.js dependencies...")
    subprocess.run(["npm", "install"], check=True)
    
    # Start the Next.js app
    print("🔧 Starting Next.js app on http://localhost:3000")
    subprocess.run(["npm", "run", "dev"], check=True)

if __name__ == "__main__":
    print("🎯 NBA Betting Analytics - Starting Services")
    print("=" * 50)
    
    try:
        # Start ML service in background
        ml_process = subprocess.Popen([
            sys.executable, __file__, "--ml-service"
        ])
        
        # Wait a moment for ML service to start
        time.sleep(5)
        
        # Start Next.js app
        start_nextjs_app()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
        ml_process.terminate()
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting services: {e}")
        sys.exit(1)
