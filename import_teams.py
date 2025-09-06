#!/usr/bin/env python3
"""
Import Teams from TeamHistories.csv
"""
import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from data_import.database import DatabaseManager
from data_import.team_importer import TeamImporter

async def main():
    """Import teams from CSV"""
    print("🚀 Starting Team Import...")
    
    db_manager = DatabaseManager()
    team_importer = TeamImporter(db_manager)
    
    try:
        # Connect to database
        await db_manager.connect()
        
        # Import teams
        team_mapping = await team_importer.import_teams_from_csv("data/TeamHistories.csv")
        
        print(f"✅ Team import completed!")
        print(f"📊 Teams imported: {len(team_mapping)}")
        
    except Exception as e:
        print(f"❌ Error during team import: {e}")
        raise
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(main())

