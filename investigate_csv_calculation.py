#!/usr/bin/env python3
"""
Investigate how player stats were calculated from CSV
"""
import pandas as pd
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

def main():
    """Investigate how player stats were calculated from CSV"""
    print("🔍 Investigating CSV calculation method...")
    
    # Check the PlayerStatistics.csv structure
    print("\n📊 === PLAYER STATISTICS CSV STRUCTURE ===")
    try:
        # Read a sample of the CSV
        df = pd.read_csv("data/PlayerStatistics.csv", nrows=1000)
        print(f"CSV columns: {list(df.columns)}")
        print(f"Sample data shape: {df.shape}")
        
        # Check if there's a season type column
        if 'seasonType' in df.columns:
            print("\n✅ Found seasonType column in CSV!")
            print("Season types in CSV:")
            print(df['seasonType'].value_counts())
        else:
            print("\n❌ No seasonType column found in CSV")
            print("Available columns:")
            for col in df.columns:
                print(f"  - {col}")
        
        # Check Giannis data in CSV
        print("\n👤 === GIANNIS DATA IN CSV ===")
        giannis_data = df[df['firstName'].str.contains('Giannis', na=False) & 
                         df['lastName'].str.contains('Antetokounmpo', na=False)]
        
        if not giannis_data.empty:
            print(f"Found {len(giannis_data)} Giannis records in CSV sample")
            print("Sample Giannis records:")
            print(giannis_data[['firstName', 'lastName', 'gameDate', 'season']].head())
            
            # Check if there are season types
            if 'seasonType' in df.columns:
                giannis_season_types = giannis_data['seasonType'].value_counts()
                print(f"\nGiannis season types in CSV:")
                print(giannis_season_types)
        else:
            print("No Giannis records found in CSV sample")
        
        # Check the full CSV for Giannis
        print("\n🔍 === CHECKING FULL CSV FOR GIANNIS ===")
        df_full = pd.read_csv("data/PlayerStatistics.csv")
        giannis_full = df_full[df_full['firstName'].str.contains('Giannis', na=False) & 
                              df_full['lastName'].str.contains('Antetokounmpo', na=False)]
        
        if not giannis_full.empty:
            print(f"Found {len(giannis_full)} total Giannis records in full CSV")
            
            # Check 2024-25 season specifically
            giannis_2024_25 = giannis_full[giannis_full['season'] == '2024-25']
            print(f"Giannis 2024-25 records: {len(giannis_2024_25)}")
            
            if 'seasonType' in df_full.columns:
                print("Giannis 2024-25 season types:")
                print(giannis_2024_25['seasonType'].value_counts())
                
                # Count regular season vs playoff games
                regular_season = giannis_2024_25[giannis_2024_25['seasonType'] == 'Regular Season']
                playoffs = giannis_2024_25[giannis_2024_25['seasonType'] == 'Playoffs']
                
                print(f"Regular season games: {len(regular_season)}")
                print(f"Playoff games: {len(playoffs)}")
                print(f"Total games: {len(giannis_2024_25)}")
                
                if len(regular_season) + len(playoffs) == len(giannis_2024_25):
                    print("✅ Game counts match - CSV includes both regular season and playoffs")
                else:
                    print("⚠️ Game counts don't match - there might be other season types")
            else:
                print("No seasonType column - CSV might only have regular season data")
        else:
            print("No Giannis records found in full CSV")
        
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

