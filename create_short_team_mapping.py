#!/usr/bin/env python3
"""
Create mapping for short team names to full team names
"""
import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from data_import.database import DatabaseManager

async def create_short_team_mapping():
    """Create mapping for short team names used in statistics"""
    print("🗺️ Creating short team name mapping...")
    
    db_manager = DatabaseManager()
    
    try:
        # Connect to database
        await db_manager.connect()
        
        # Get teams from database
        db_teams = await db_manager.get_existing_teams()
        
        # Create mapping from short names to full names
        short_to_full_mapping = {
            # Current NBA teams
            "Hawks": "Atlanta Hawks",
            "Celtics": "Boston Celtics", 
            "Nets": "Brooklyn Nets",
            "Hornets": "Charlotte Hornets",
            "Bulls": "Chicago Bulls",
            "Cavaliers": "Cleveland Cavaliers",
            "Mavericks": "Dallas Mavericks",
            "Nuggets": "Denver Nuggets",
            "Pistons": "Detroit Pistons",
            "Warriors": "Golden State Warriors",
            "Rockets": "Houston Rockets",
            "Pacers": "Indiana Pacers",
            "Clippers": "Los Angeles Clippers",
            "Lakers": "Los Angeles Lakers",
            "Grizzlies": "Memphis Grizzlies",
            "Heat": "Miami Heat",
            "Bucks": "Milwaukee Bucks",
            "Timberwolves": "Minnesota Timberwolves",
            "Pelicans": "New Orleans Pelicans",
            "Knicks": "New York Knicks",
            "Thunder": "Oklahoma City Thunder",
            "Magic": "Orlando Magic",
            "76ers": "Philadelphia 76ers",
            "Suns": "Phoenix Suns",
            "Trail Blazers": "Portland Trail Blazers",
            "Kings": "Sacramento Kings",
            "Spurs": "San Antonio Spurs",
            "Raptors": "Toronto Raptors",
            "Jazz": "Utah Jazz",
            "Wizards": "Washington Wizards",
            
            # Historical teams that might appear
            "SuperSonics": "Seattle SuperSonics",
            "Royals": "Rochester Royals",
            "Nationals": "Syracuse Nationals",
            "Packers": "Chicago Packers",
            "Zephyrs": "Chicago Zephyrs",
            "Bullets": "Washington Bullets",
            "Bobcats": "Charlotte Bobcats"
        }
        
        # Create the actual mapping with team IDs
        short_team_mapping = {}
        for short_name, full_name in short_to_full_mapping.items():
            # Find the team in our database
            team = next((t for t in db_teams if t['name'] == full_name), None)
            if team:
                short_team_mapping[short_name] = team['id']
                print(f"✅ Mapped: {short_name} -> {full_name}")
            else:
                print(f"❌ Not found: {full_name}")
        
        # Create mapping file
        mapping_code = f"""
# Short team name mapping for statistics import
SHORT_TEAM_MAPPING = {{
"""
        for short_name, team_id in short_team_mapping.items():
            mapping_code += f'    "{short_name}": "{team_id}",\n'
        
        mapping_code += "}\n"
        
        with open("short_team_mapping.py", "w") as f:
            f.write(mapping_code)
        
        print(f"\n💾 Short team mapping saved to short_team_mapping.py")
        print(f"📊 Mapped teams: {len(short_team_mapping)}")
        
    except Exception as e:
        print(f"❌ Error creating short team mapping: {e}")
        raise
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(create_short_team_mapping())

