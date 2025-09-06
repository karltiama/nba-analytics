#!/usr/bin/env python3
"""
Setup script for NBA data import
Installs required Python dependencies
"""
import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("🔄 Installing Python dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def create_data_directory():
    """Create data directory if it doesn't exist"""
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"✅ Created data directory: {data_dir}")
    else:
        print(f"📁 Data directory already exists: {data_dir}")

def main():
    """Main setup function"""
    print("🚀 Setting up NBA data import environment...")
    
    # Install dependencies
    if not install_requirements():
        return
    
    # Create data directory
    create_data_directory()
    
    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("1. Place your CSV files in the 'data' directory:")
    print("   - TeamHistories.csv")
    print("   - Players.csv")
    print("   - Games.csv")
    print("   - TeamStatistics.csv")
    print("   - PlayerStatistics.csv")
    print("2. Run: python import_nba_data.py")

if __name__ == "__main__":
    main()
