#!/usr/bin/env python3
"""
Import Games from Games.csv
"""
import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from data_import.database import DatabaseManager
from data_import.game_importer import GameImporter

async def main():
    """Import games from CSV"""
    print("🚀 Starting Game Import...")
    
    db_manager = DatabaseManager()
    
    try:
        # Connect to database
        await db_manager.connect()
        
        # Get existing teams for mapping
        existing_teams = await db_manager.get_existing_teams()
        team_mapping = {team['name']: team['id'] for team in existing_teams}
        
        # Create game importer with team mapping
        game_importer = GameImporter(db_manager, team_mapping)
        
        # Import games
        game_mapping = await game_importer.import_games_from_csv("data/Games.csv")
        
        print(f"✅ Game import completed!")
        print(f"📊 Games imported: {len(game_mapping) if game_mapping else 0}")
        
    except Exception as e:
        print(f"❌ Error during game import: {e}")
        raise
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
