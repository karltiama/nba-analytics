#!/usr/bin/env python3
"""
Create a comprehensive team name mapping for games import
"""
import asyncio
import sys
import pandas as pd
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from data_import.database import DatabaseManager

async def create_team_mapping():
    """Create a comprehensive team name mapping"""
    print("🗺️ Creating comprehensive team name mapping...")
    
    db_manager = DatabaseManager()
    
    try:
        # Connect to database
        await db_manager.connect()
        
        # Get teams from database
        db_teams = await db_manager.get_existing_teams()
        db_team_names = {team['name']: team['id'] for team in db_teams}
        
        print(f"📊 Teams in database: {len(db_team_names)}")
        
        # Read Games.csv to see what team names are used there
        df = pd.read_csv("data/Games.csv")
        
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
        
        # Create mapping dictionary
        team_mapping = {}
        unmapped_teams = set()
        
        for game_team in all_game_teams:
            if game_team in db_team_names:
                # Direct match
                team_mapping[game_team] = db_team_names[game_team]
            else:
                # Try to find a match
                found_match = False
                
                # Check for partial matches
                game_parts = set(game_team.lower().split())
                
                for db_team_name, db_team_id in db_team_names.items():
                    db_parts = set(db_team_name.lower().split())
                    
                    # Check for significant overlap
                    common_parts = game_parts.intersection(db_parts)
                    if len(common_parts) >= 2:  # At least 2 words in common
                        team_mapping[game_team] = db_team_id
                        found_match = True
                        print(f"🔄 Mapped: '{game_team}' -> '{db_team_name}'")
                        break
                
                if not found_match:
                    unmapped_teams.add(game_team)
        
        print(f"\n✅ Successfully mapped: {len(team_mapping)}")
        print(f"❌ Unmapped teams: {len(unmapped_teams)}")
        
        if unmapped_teams:
            print(f"\n📋 Unmapped teams:")
            for team in sorted(unmapped_teams):
                print(f"  ❌ {team}")
        
        # Create a mapping file for the game importer
        mapping_code = f"""
# Team name mapping for games import
TEAM_MAPPING = {{
"""
        for game_team, db_team_id in team_mapping.items():
            mapping_code += f'    "{game_team}": "{db_team_id}",\n'
        
        mapping_code += "}\n"
        
        with open("team_mapping.py", "w") as f:
            f.write(mapping_code)
        
        print(f"\n💾 Team mapping saved to team_mapping.py")
        print(f"📊 Mapping coverage: {len(team_mapping)}/{len(all_game_teams)} ({len(team_mapping)/len(all_game_teams)*100:.1f}%)")
        
    except Exception as e:
        print(f"❌ Error during mapping creation: {e}")
        raise
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(create_team_mapping())

