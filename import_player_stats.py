#!/usr/bin/env python3
"""
Import player statistics from PlayerStatistics.csv
"""
import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from data_import.database import DatabaseManager
from data_import.stats_importer import StatsImporter

async def main():
    """Import player statistics from CSV"""
    print("🚀 Starting Player Statistics Import...")
    
    db_manager = DatabaseManager()
    
    try:
        # Connect to database
        await db_manager.connect()
        
        # Get existing teams and players for mapping
        existing_teams = await db_manager.get_existing_teams()
        existing_players = await db_manager.get_existing_players()
        team_mapping = {team['name']: team['id'] for team in existing_teams}
        player_mapping = {player['name']: player['id'] for player in existing_players}
        
        # Create stats importer with mappings
        stats_importer = StatsImporter(db_manager, team_mapping, player_mapping)
        
        # Import player stats
        stats_mapping = await stats_importer.import_player_stats_from_csv("data/PlayerStatistics.csv")
        
        print(f"✅ Player statistics import completed!")
        print(f"📊 Player stats imported: {len(stats_mapping) if stats_mapping else 0}")
        
    except Exception as e:
        print(f"❌ Error during player stats import: {e}")
        raise
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(main())