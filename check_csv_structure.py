#!/usr/bin/env python3
"""
Check the actual CSV structure and how seasons were calculated
"""
import pandas as pd
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

def main():
    """Check CSV structure and season calculation"""
    print("🔍 Checking CSV structure and season calculation...")
    
    try:
        # Read CSV with low_memory=False to avoid warnings
        print("\n📊 === PLAYER STATISTICS CSV STRUCTURE ===")
        df = pd.read_csv("data/PlayerStatistics.csv", low_memory=False)
        print(f"CSV shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        
        # Check Giannis data
        print("\n👤 === GIANNIS DATA IN CSV ===")
        giannis_data = df[df['firstName'].str.contains('Giannis', na=False) & 
                         df['lastName'].str.contains('Antetokounmpo', na=False)]
        
        if not giannis_data.empty:
            print(f"Found {len(giannis_data)} Giannis records in CSV")
            
            # Check the date range
            giannis_data['gameDate'] = pd.to_datetime(giannis_data['gameDate'])
            print(f"Date range: {giannis_data['gameDate'].min()} to {giannis_data['gameDate'].max()}")
            
            # Check 2024-25 season (October 2024 to April 2025)
            giannis_2024_25 = giannis_data[
                (giannis_data['gameDate'] >= '2024-10-01') & 
                (giannis_data['gameDate'] <= '2025-04-30')
            ]
            print(f"Giannis 2024-25 records (Oct 2024 - Apr 2025): {len(giannis_2024_25)}")
            
            # Check if there are gameType indicators
            if 'gameType' in df.columns:
                print(f"\nGame types in Giannis 2024-25 data:")
                print(giannis_2024_25['gameType'].value_counts())
            
            # Check if there are gameLabel indicators
            if 'gameLabel' in df.columns:
                print(f"\nGame labels in Giannis 2024-25 data:")
                print(giannis_2024_25['gameLabel'].value_counts())
            
            # Check if there are seriesGameNumber indicators (playoffs)
            if 'seriesGameNumber' in df.columns:
                print(f"\nSeries game numbers in Giannis 2024-25 data:")
                print(giannis_2024_25['seriesGameNumber'].value_counts())
                
                # Check for playoff games (seriesGameNumber > 0)
                playoff_games = giannis_2024_25[giannis_2024_25['seriesGameNumber'].notna() & 
                                              (giannis_2024_25['seriesGameNumber'] > 0)]
                regular_games = giannis_2024_25[giannis_2024_25['seriesGameNumber'].isna() | 
                                              (giannis_2024_25['seriesGameNumber'] == 0)]
                
                print(f"Regular season games (seriesGameNumber = 0 or NaN): {len(regular_games)}")
                print(f"Playoff games (seriesGameNumber > 0): {len(playoff_games)}")
                print(f"Total games: {len(giannis_2024_25)}")
                
                if len(regular_games) + len(playoff_games) == len(giannis_2024_25):
                    print("✅ Game counts match - we can separate regular season from playoffs")
                else:
                    print("⚠️ Game counts don't match - there might be other categories")
            
            # Show sample records
            print(f"\nSample Giannis 2024-25 records:")
            sample_cols = ['gameDate', 'gameType', 'gameLabel', 'seriesGameNumber', 'points']
            print(giannis_2024_25[sample_cols].head(10))
            
        else:
            print("No Giannis records found in CSV")
        
        # Check overall game type distribution
        print(f"\n📈 === OVERALL GAME TYPE DISTRIBUTION ===")
        if 'gameType' in df.columns:
            print("Game types in entire CSV:")
            print(df['gameType'].value_counts())
        
        if 'gameLabel' in df.columns:
            print("\nGame labels in entire CSV:")
            print(df['gameLabel'].value_counts())
        
        if 'seriesGameNumber' in df.columns:
            print("\nSeries game numbers in entire CSV:")
            print(df['seriesGameNumber'].value_counts())
        
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

