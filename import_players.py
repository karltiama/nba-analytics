#!/usr/bin/env python3
"""
Import Players from Players.csv
"""
import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from data_import.database import DatabaseManager
from data_import.player_importer import PlayerImporter

async def main():
    """Import players from CSV"""
    print("🚀 Starting Player Import...")
    
    db_manager = DatabaseManager()
    
    try:
        # Connect to database
        await db_manager.connect()
        
        # Get existing teams for mapping
        existing_teams = await db_manager.get_existing_teams()
        team_mapping = {team['name']: team['id'] for team in existing_teams}
        
        # Create player importer with team mapping
        player_importer = PlayerImporter(db_manager, team_mapping)
        
        # Import players
        player_mapping = await player_importer.import_players_from_csv("data/Players.csv")
        
        print(f"✅ Player import completed!")
        print(f"📊 Players imported: {len(player_mapping)}")
        
    except Exception as e:
        print(f"❌ Error during player import: {e}")
        raise
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
