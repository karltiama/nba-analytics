#!/usr/bin/env python3
"""
NBA Data Import Script
Imports historical NBA data from CSV files into Supabase database
"""
import asyncio
import os
import sys
from pathlib import Path
from typing import Dict

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from data_import.database import DatabaseManager
from data_import.team_importer import TeamImporter
from data_import.game_importer import GameImporter
from data_import.player_importer import PlayerImporter
from data_import.stats_importer import StatsImporter

class NBADataImporter:
    def __init__(self, data_directory: str = "data"):
        self.data_directory = Path(data_directory)
        self.db_manager = DatabaseManager()
        self.team_mapping: Dict[str, str] = {}
        self.player_mapping: Dict[str, str] = {}
    
    async def import_all_data(self):
        """Import all NBA data from CSV files"""
        print("🚀 Starting NBA data import process...")
        
        try:
            # Connect to database
            await self.db_manager.connect()
            
            # Step 1: Import teams
            await self._import_teams()
            
            # Step 2: Import players
            await self._import_players()
            
            # Step 3: Import games
            await self._import_games()
            
            # Step 4: Import team statistics
            await self._import_team_stats()
            
            # Step 5: Import player statistics
            await self._import_player_stats()
            
            print("✅ NBA data import completed successfully!")
            
        except Exception as e:
            print(f"❌ Error during import: {e}")
            raise
        finally:
            await self.db_manager.disconnect()
    
    async def _import_teams(self):
        """Import team data"""
        print("\n📊 Step 1: Importing teams...")
        
        team_file = self.data_directory / "TeamHistories.csv"
        if not team_file.exists():
            print(f"⚠️ Team file not found: {team_file}")
            return
        
        importer = TeamImporter(self.db_manager)
        self.team_mapping = await importer.import_teams_from_csv(str(team_file))
        print(f"✅ Teams imported: {len(self.team_mapping)} teams")
    
    async def _import_players(self):
        """Import player data"""
        print("\n📊 Step 2: Importing players...")
        
        player_file = self.data_directory / "Players.csv"
        if not player_file.exists():
            print(f"⚠️ Player file not found: {player_file}")
            return
        
        importer = PlayerImporter(self.db_manager, self.team_mapping)
        await importer.import_players_from_csv(str(player_file))
        
        # Build player mapping for stats import
        players = await self.db_manager.get_existing_players()
        self.player_mapping = {player['name']: player['id'] for player in players}
        print(f"✅ Players imported: {len(self.player_mapping)} players")
    
    async def _import_games(self):
        """Import game data"""
        print("\n📊 Step 3: Importing games...")
        
        game_file = self.data_directory / "Games.csv"
        if not game_file.exists():
            print(f"⚠️ Game file not found: {game_file}")
            return
        
        importer = GameImporter(self.db_manager, self.team_mapping)
        await importer.import_games_from_csv(str(game_file))
        print(f"✅ Games imported: {importer.games_created} games")
    
    async def _import_team_stats(self):
        """Import team statistics"""
        print("\n📊 Step 4: Importing team statistics...")
        
        stats_file = self.data_directory / "TeamStatistics.csv"
        if not stats_file.exists():
            print(f"⚠️ Team stats file not found: {stats_file}")
            return
        
        importer = StatsImporter(self.db_manager, self.team_mapping, self.player_mapping)
        await importer.import_team_stats_from_csv(str(stats_file))
        print(f"✅ Team stats imported: {importer.stats_created} records")
    
    async def _import_player_stats(self):
        """Import player statistics"""
        print("\n📊 Step 5: Importing player statistics...")
        
        stats_file = self.data_directory / "PlayerStatistics.csv"
        if not stats_file.exists():
            print(f"⚠️ Player stats file not found: {stats_file}")
            return
        
        importer = StatsImporter(self.db_manager, self.team_mapping, self.player_mapping)
        await importer.import_player_stats_from_csv(str(stats_file))
        print(f"✅ Player stats imported: {importer.stats_created} records")

async def main():
    """Main function"""
    # Check if data directory exists
    data_dir = "data"
    if not Path(data_dir).exists():
        print(f"❌ Data directory not found: {data_dir}")
        print("Please create a 'data' directory and place your CSV files there:")
        print("- TeamHistories.csv")
        print("- Players.csv")
        print("- Games.csv")
        print("- TeamStatistics.csv")
        print("- PlayerStatistics.csv")
        return
    
    # Check for required CSV files
    required_files = [
        "TeamHistories.csv",
        "Players.csv", 
        "Games.csv",
        "TeamStatistics.csv",
        "PlayerStatistics.csv"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(data_dir) / file:
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return
    
    # Start import process
    importer = NBADataImporter(data_dir)
    await importer.import_all_data()

if __name__ == "__main__":
    asyncio.run(main())
