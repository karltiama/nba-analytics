#!/usr/bin/env python3
"""
Fix team name mapping issues by adding missing teams and creating aliases
"""
import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from data_import.database import DatabaseManager

async def fix_team_mapping():
    """Add missing teams and create team name mapping"""
    print("🔧 Fixing team name mapping...")
    
    db_manager = DatabaseManager()
    
    try:
        # Connect to database
        await db_manager.connect()
        
        # Team name mappings - Games.csv name -> Database name
        team_mappings = {
            # Current team names that are missing
            "Charlotte Bobcats": "Charlotte Hornets",  # Bobcats became Hornets
            "Minnesota Timberwolves": "Minnesota Timberwolves",  # Need to add this
            "Washington Wizards": "Washington Wizards",  # Need to add this  
            "Milwaukee Bucks": "Milwaukee Bucks",  # Need to add this
            "Philadelphia 76ers": "Philadelphia 76ers",  # Need to add this
            "New York Knicks": "New York Knicks",  # Need to add this
            "Chicago Zephyrs": "Chicago Bulls",  # Historical team -> current team
            "Chicago Packers": "Chicago Bulls",  # Historical team -> current team
        }
        
        # Teams we need to add to the database
        teams_to_add = [
            {
                "name": "Minnesota Timberwolves",
                "abbreviation": "MIN", 
                "city": "Minneapolis",
                "conference": "Western",
                "division": "Northwest",
                "logoUrl": None
            },
            {
                "name": "Washington Wizards", 
                "abbreviation": "WAS",
                "city": "Washington",
                "conference": "Eastern", 
                "division": "Southeast",
                "logoUrl": None
            },
            {
                "name": "Milwaukee Bucks",
                "abbreviation": "MIL",
                "city": "Milwaukee", 
                "conference": "Eastern",
                "division": "Central",
                "logoUrl": None
            },
            {
                "name": "Philadelphia 76ers",
                "abbreviation": "PHI", 
                "city": "Philadelphia",
                "conference": "Eastern",
                "division": "Atlantic", 
                "logoUrl": None
            },
            {
                "name": "New York Knicks",
                "abbreviation": "NYK",
                "city": "New York",
                "conference": "Eastern",
                "division": "Atlantic",
                "logoUrl": None
            }
        ]
        
        # Add missing teams
        teams_added = 0
        for team_data in teams_to_add:
            try:
                # Check if team already exists
                existing_team = await db_manager.get_team_by_name(team_data['name'])
                if existing_team:
                    print(f"⚠️ Team already exists: {team_data['name']}")
                    continue
                
                # Create team
                created_team = await db_manager.create_team(team_data)
                teams_added += 1
                print(f"✅ Added team: {team_data['name']}")
                
            except Exception as e:
                print(f"❌ Error adding team {team_data['name']}: {e}")
        
        print(f"\n📊 Teams added: {teams_added}")
        
        # Verify our team count
        all_teams = await db_manager.get_existing_teams()
        print(f"📊 Total teams in database: {len(all_teams)}")
        
        # Show the mapping we'll use
        print(f"\n📋 Team name mapping for games import:")
        for games_name, db_name in team_mappings.items():
            print(f"  '{games_name}' -> '{db_name}'")
        
    except Exception as e:
        print(f"❌ Error during team mapping fix: {e}")
        raise
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(fix_team_mapping())

