#!/usr/bin/env python3
"""
Analyze team name matching between Games.csv and our database
"""
import asyncio
import sys
import pandas as pd
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from data_import.database import DatabaseManager

async def analyze_team_matching():
    """Analyze team name mismatches"""
    print("🔍 Analyzing team name matching...")
    
    db_manager = DatabaseManager()
    
    try:
        # Connect to database
        await db_manager.connect()
        
        # Get teams from database
        db_teams = await db_manager.get_existing_teams()
        db_team_names = {team['name'] for team in db_teams}
        
        print(f"📊 Teams in database: {len(db_team_names)}")
        
        # Read Games.csv to see what team names are used there
        df = pd.read_csv("data/Games.csv")
        print(f"📊 Games in CSV: {len(df)}")
        
        # Get unique team names from games
        home_teams = set()
        away_teams = set()
        
        for _, row in df.iterrows():
            home_team = f"{row.get('hometeamCity', '')} {row.get('hometeamName', '')}".strip()
            away_team = f"{row.get('awayteamCity', '')} {row.get('awayteamName', '')}".strip()
            
            if home_team:
                home_teams.add(home_team)
            if away_team:
                away_teams.add(away_team)
        
        all_game_teams = home_teams.union(away_teams)
        print(f"📊 Unique teams in games: {len(all_game_teams)}")
        
        # Find matches and mismatches
        matches = db_team_names.intersection(all_game_teams)
        home_mismatches = home_teams - db_team_names
        away_mismatches = away_teams - db_team_names
        all_mismatches = all_game_teams - db_team_names
        
        print(f"\n✅ Teams that match: {len(matches)}")
        print(f"❌ Home team mismatches: {len(home_mismatches)}")
        print(f"❌ Away team mismatches: {len(away_mismatches)}")
        print(f"❌ Total mismatches: {len(all_mismatches)}")
        
        print(f"\n📋 Sample matches:")
        for team in list(matches)[:10]:
            print(f"  ✅ {team}")
        
        print(f"\n📋 Sample mismatches:")
        for team in list(all_mismatches)[:20]:
            print(f"  ❌ {team}")
        
        # Check for partial matches
        print(f"\n🔍 Looking for partial matches...")
        partial_matches = []
        
        for game_team in list(all_mismatches)[:50]:  # Check first 50
            for db_team in db_team_names:
                # Check if any part of the team name matches
                game_parts = game_team.lower().split()
                db_parts = db_team.lower().split()
                
                # Check for common words
                common_words = set(game_parts).intersection(set(db_parts))
                if common_words and len(common_words) >= 1:
                    partial_matches.append((game_team, db_team, common_words))
        
        print(f"📋 Partial matches found: {len(partial_matches)}")
        for game_team, db_team, common in partial_matches[:10]:
            print(f"  🔄 '{game_team}' ↔ '{db_team}' (common: {common})")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        raise
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(analyze_team_matching())

