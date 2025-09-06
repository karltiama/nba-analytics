#!/usr/bin/env python3
"""
Simple NBA Data Import Script
Imports only current NBA teams and some sample data
"""
import asyncio
import os
import sys
from pathlib import Path
from typing import Dict

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from data_import.database import DatabaseManager

class SimpleNBAImporter:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.team_mapping: Dict[str, str] = {}
    
    async def import_current_teams(self):
        """Import only current NBA teams"""
        print("🚀 Starting simple NBA data import...")
        
        try:
            # Connect to database
            await self.db_manager.connect()
            
            # Create current NBA teams
            await self._create_current_teams()
            
            print("✅ Simple import completed successfully!")
            
        except Exception as e:
            print(f"❌ Error during import: {e}")
            raise
        finally:
            await self.db_manager.disconnect()
    
    async def _create_current_teams(self):
        """Create current NBA teams"""
        print("📊 Creating current NBA teams...")
        
        current_teams = [
            # Eastern Conference
            {"name": "Atlanta Hawks", "abbreviation": "ATL", "city": "Atlanta", "conference": "Eastern", "division": "Southeast", "logoUrl": None},
            {"name": "Boston Celtics", "abbreviation": "BOS", "city": "Boston", "conference": "Eastern", "division": "Atlantic", "logoUrl": None},
            {"name": "Brooklyn Nets", "abbreviation": "BKN", "city": "Brooklyn", "conference": "Eastern", "division": "Atlantic", "logoUrl": None},
            {"name": "Charlotte Hornets", "abbreviation": "CHA", "city": "Charlotte", "conference": "Eastern", "division": "Southeast", "logoUrl": None},
            {"name": "Chicago Bulls", "abbreviation": "CHI", "city": "Chicago", "conference": "Eastern", "division": "Central", "logoUrl": None},
            {"name": "Cleveland Cavaliers", "abbreviation": "CLE", "city": "Cleveland", "conference": "Eastern", "division": "Central", "logoUrl": None},
            {"name": "Detroit Pistons", "abbreviation": "DET", "city": "Detroit", "conference": "Eastern", "division": "Central", "logoUrl": None},
            {"name": "Indiana Pacers", "abbreviation": "IND", "city": "Indianapolis", "conference": "Eastern", "division": "Central", "logoUrl": None},
            {"name": "Miami Heat", "abbreviation": "MIA", "city": "Miami", "conference": "Eastern", "division": "Southeast", "logoUrl": None},
            {"name": "Milwaukee Bucks", "abbreviation": "MIL", "city": "Milwaukee", "conference": "Eastern", "division": "Central", "logoUrl": None},
            {"name": "New York Knicks", "abbreviation": "NYK", "city": "New York", "conference": "Eastern", "division": "Atlantic", "logoUrl": None},
            {"name": "Orlando Magic", "abbreviation": "ORL", "city": "Orlando", "conference": "Eastern", "division": "Southeast", "logoUrl": None},
            {"name": "Philadelphia 76ers", "abbreviation": "PHI", "city": "Philadelphia", "conference": "Eastern", "division": "Atlantic", "logoUrl": None},
            {"name": "Toronto Raptors", "abbreviation": "TOR", "city": "Toronto", "conference": "Eastern", "division": "Atlantic", "logoUrl": None},
            {"name": "Washington Wizards", "abbreviation": "WAS", "city": "Washington", "conference": "Eastern", "division": "Southeast", "logoUrl": None},
            
            # Western Conference
            {"name": "Dallas Mavericks", "abbreviation": "DAL", "city": "Dallas", "conference": "Western", "division": "Southwest", "logoUrl": None},
            {"name": "Denver Nuggets", "abbreviation": "DEN", "city": "Denver", "conference": "Western", "division": "Northwest", "logoUrl": None},
            {"name": "Golden State Warriors", "abbreviation": "GSW", "city": "San Francisco", "conference": "Western", "division": "Pacific", "logoUrl": None},
            {"name": "Houston Rockets", "abbreviation": "HOU", "city": "Houston", "conference": "Western", "division": "Southwest", "logoUrl": None},
            {"name": "Los Angeles Clippers", "abbreviation": "LAC", "city": "Los Angeles", "conference": "Western", "division": "Pacific", "logoUrl": None},
            {"name": "Los Angeles Lakers", "abbreviation": "LAL", "city": "Los Angeles", "conference": "Western", "division": "Pacific", "logoUrl": None},
            {"name": "Memphis Grizzlies", "abbreviation": "MEM", "city": "Memphis", "conference": "Western", "division": "Southwest", "logoUrl": None},
            {"name": "Minnesota Timberwolves", "abbreviation": "MIN", "city": "Minneapolis", "conference": "Western", "division": "Northwest", "logoUrl": None},
            {"name": "New Orleans Pelicans", "abbreviation": "NOP", "city": "New Orleans", "conference": "Western", "division": "Southwest", "logoUrl": None},
            {"name": "Oklahoma City Thunder", "abbreviation": "OKC", "city": "Oklahoma City", "conference": "Western", "division": "Northwest", "logoUrl": None},
            {"name": "Phoenix Suns", "abbreviation": "PHX", "city": "Phoenix", "conference": "Western", "division": "Pacific", "logoUrl": None},
            {"name": "Portland Trail Blazers", "abbreviation": "POR", "city": "Portland", "conference": "Western", "division": "Northwest", "logoUrl": None},
            {"name": "Sacramento Kings", "abbreviation": "SAC", "city": "Sacramento", "conference": "Western", "division": "Pacific", "logoUrl": None},
            {"name": "San Antonio Spurs", "abbreviation": "SAS", "city": "San Antonio", "conference": "Western", "division": "Southwest", "logoUrl": None},
            {"name": "Utah Jazz", "abbreviation": "UTA", "city": "Salt Lake City", "conference": "Western", "division": "Northwest", "logoUrl": None},
        ]
        
        teams_created = 0
        teams_skipped = 0
        
        for team_data in current_teams:
            try:
                # Check if team already exists
                existing_team = await self.db_manager.get_team_by_name(team_data['name'])
                if existing_team:
                    print(f"⚠️ Team already exists: {team_data['name']}")
                    teams_skipped += 1
                    self.team_mapping[team_data['name']] = existing_team['id']
                    continue
                
                # Create team
                created_team = await self.db_manager.create_team(team_data)
                self.team_mapping[team_data['name']] = created_team['id']
                teams_created += 1
                
                print(f"✅ Created team: {team_data['name']}")
                
            except Exception as e:
                print(f"❌ Error creating team {team_data['name']}: {e}")
                teams_skipped += 1
        
        print(f"📊 Team creation complete: {teams_created} created, {teams_skipped} skipped")
        print(f"📊 Total teams in mapping: {len(self.team_mapping)}")

async def main():
    """Main function"""
    importer = SimpleNBAImporter()
    await importer.import_current_teams()

if __name__ == "__main__":
    asyncio.run(main())
