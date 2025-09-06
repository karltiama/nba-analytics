#!/usr/bin/env python3
"""
CSV Analysis Script
Analyzes your CSV files to see what columns they contain
"""
import pandas as pd
import os
from pathlib import Path

def analyze_csv_file(file_path: str):
    """Analyze a single CSV file"""
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    try:
        # Read just the first few rows to get column info
        df = pd.read_csv(file_path, nrows=5)
        
        print(f"\n📊 Analyzing: {file_path}")
        print(f"   Rows: {len(df)} (sample)")
        print(f"   Columns: {len(df.columns)}")
        print("   Column names:")
        
        for i, col in enumerate(df.columns, 1):
            print(f"     {i:2d}. {col}")
        
        # Show sample data
        print("   Sample data (first row):")
        for col in df.columns:
            value = df[col].iloc[0] if len(df) > 0 else "N/A"
            print(f"     {col}: {value}")
            
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")

def main():
    """Main function"""
    data_dir = Path("data")
    
    if not data_dir.exists():
        print("❌ Data directory not found. Please create 'data' directory and place CSV files there.")
        return
    
    print("🔍 Analyzing CSV files in data/ directory...")
    
    # List all CSV files
    csv_files = list(data_dir.glob("*.csv"))
    
    if not csv_files:
        print("❌ No CSV files found in data/ directory")
        print("Please place your CSV files there:")
        print("- TeamHistories.csv")
        print("- Players.csv")
        print("- Games.csv")
        print("- TeamStatistics.csv")
        print("- PlayerStatistics.csv")
        return
    
    print(f"📁 Found {len(csv_files)} CSV files:")
    for file in csv_files:
        print(f"   - {file.name}")
    
    # Analyze each file
    for file in csv_files:
        analyze_csv_file(str(file))
    
    print("\n✅ Analysis complete!")
    print("\nNext steps:")
    print("1. Check if the column names match what the import script expects")
    print("2. If not, we can modify the import script to match your data format")
    print("3. Run: python import_nba_data.py")

if __name__ == "__main__":
    main()

