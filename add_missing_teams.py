#!/usr/bin/env python3
"""
Add the missing teams that we need for games import
"""
import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from data_import.database import DatabaseManager

async def add_missing_teams():
    """Add missing teams with unique abbreviations"""
    print("➕ Adding missing teams...")
    
    db_manager = DatabaseManager()
    
    try:
        # Connect to database
        await db_manager.connect()
        
        # Teams we need to add with unique abbreviations
        teams_to_add = [
            {
                "name": "Charlotte Bobcats",
                "abbreviation": "CHA2",  # Different from CHA (Hornets)
                "city": "Charlotte",
                "conference": "Eastern",
                "division": "Southeast",
                "logoUrl": None
            },
            {
                "name": "Chicago Packers",
                "abbreviation": "CHP",  # Unique abbreviation
                "city": "Chicago",
                "conference": "Eastern",
                "division": "Central",
                "logoUrl": None
            },
            {
                "name": "Chicago Zephyrs",
                "abbreviation": "CHZ",  # Unique abbreviation
                "city": "Chicago",
                "conference": "Eastern",
                "division": "Central",
                "logoUrl": None
            },
            {
                "name": "Milwaukee Bucks",
                "abbreviation": "MIL2",  # Different from existing MIL
                "city": "Milwaukee",
                "conference": "Eastern",
                "division": "Central",
                "logoUrl": None
            },
            {
                "name": "Minnesota Timberwolves",
                "abbreviation": "MIN2",  # Different from existing MIN
                "city": "Minneapolis",
                "conference": "Western",
                "division": "Northwest",
                "logoUrl": None
            },
            {
                "name": "Philadelphia 76ers",
                "abbreviation": "PHI2",  # Different from existing PHI
                "city": "Philadelphia",
                "conference": "Eastern",
                "division": "Atlantic",
                "logoUrl": None
            },
            {
                "name": "Washington Wizards",
                "abbreviation": "WAS2",  # Different from existing WAS
                "city": "Washington",
                "conference": "Eastern",
                "division": "Southeast",
                "logoUrl": None
            }
        ]
        
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
                print(f"✅ Added team: {team_data['name']} (ID: {created_team['id']})")
                
            except Exception as e:
                print(f"❌ Error adding team {team_data['name']}: {e}")
        
        print(f"\n📊 Teams added: {teams_added}")
        
        # Verify our team count
        all_teams = await db_manager.get_existing_teams()
        print(f"📊 Total teams in database: {len(all_teams)}")
        
    except Exception as e:
        print(f"❌ Error during team addition: {e}")
        raise
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(add_missing_teams())

