"""
Import team data from CSV files
"""
import pandas as pd
from typing import Dict, List
from .database import DatabaseManager

class TeamImporter:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.team_mapping = {}
    
    async def import_teams_from_csv(self, csv_path: str):
        """Import teams from TeamHistories.csv"""
        print(f"🔄 Importing teams from {csv_path}")
        
        # Read CSV file
        df = pd.read_csv(csv_path)
        print(f"📊 Found {len(df)} team records")
        
        # Get existing teams to avoid duplicates
        existing_teams = await self.db.get_existing_teams()
        existing_names = {team['name'] for team in existing_teams}
        
        teams_created = 0
        teams_skipped = 0
        
        # Group by team name and get the most recent entry for each team
        df_sorted = df.sort_values('seasonActiveTill', ascending=False)
        current_teams = df_sorted.groupby('teamName').first().reset_index()
        
        for _, row in current_teams.iterrows():
            try:
                # Extract team information from your actual CSV format
                # Use only team name without city for consistency
                team_name = row.get('teamName', '').strip()
                team_abbrev = row.get('teamAbbrev', '').strip()
                
                if not team_name or team_name in existing_names:
                    teams_skipped += 1
                    continue
                
                # Map team data to our schema
                team_data = {
                    'name': team_name,
                    'abbreviation': team_abbrev if team_abbrev else self._get_team_abbreviation(team_name),
                    'city': row.get('teamCity', '').strip(),
                    'conference': self._get_conference(team_name),
                    'division': self._get_division(team_name),
                    'logoUrl': None
                }
                
                # Create team in database
                created_team = await self.db.create_team(team_data)
                self.team_mapping[team_name] = created_team['id']
                teams_created += 1
                
                print(f"✅ Created team: {team_name}")
                
            except Exception as e:
                print(f"❌ Error creating team {row.get('teamName', 'Unknown')}: {e}")
                teams_skipped += 1
                # Rollback the transaction and continue
                try:
                    self.db.connection.rollback()
                except:
                    pass
                # Skip this team and continue
                continue
        
        print(f"📊 Team import complete: {teams_created} created, {teams_skipped} skipped")
        return self.team_mapping
    
    def _get_team_abbreviation(self, team_name: str) -> str:
        """Get team abbreviation from team name"""
        abbreviations = {
            'Hawks': 'ATL',
            'Celtics': 'BOS',
            'Nets': 'BKN',
            'Hornets': 'CHA',
            'Bulls': 'CHI',
            'Cavaliers': 'CLE',
            'Mavericks': 'DAL',
            'Nuggets': 'DEN',
            'Pistons': 'DET',
            'Warriors': 'GSW',
            'Rockets': 'HOU',
            'Pacers': 'IND',
            'Clippers': 'LAC',
            'Lakers': 'LAL',
            'Grizzlies': 'MEM',
            'Heat': 'MIA',
            'Bucks': 'MIL',
            'Timberwolves': 'MIN',
            'Pelicans': 'NOP',
            'Knicks': 'NYK',
            'Thunder': 'OKC',
            'Magic': 'ORL',
            '76ers': 'PHI',
            'Suns': 'PHX',
            'Trail Blazers': 'POR',
            'Kings': 'SAC',
            'Spurs': 'SAS',
            'Raptors': 'TOR',
            'Jazz': 'UTA',
            'Wizards': 'WAS',
            'SuperSonics': 'SEA',
            'Royals': 'ROC',
            'Nationals': 'SYR',
            'Packers': 'CHI',
            'Zephyrs': 'CHI',
            'Bullets': 'WAS',
            'Bobcats': 'CHA'
        }
        return abbreviations.get(team_name, team_name[:3].upper())
    
    def _extract_city(self, team_name: str) -> str:
        """Extract city from team name"""
        # Remove common suffixes
        city = team_name.replace(' Hawks', '').replace(' Celtics', '').replace(' Nets', '')
        city = city.replace(' Hornets', '').replace(' Bulls', '').replace(' Cavaliers', '')
        city = city.replace(' Mavericks', '').replace(' Nuggets', '').replace(' Pistons', '')
        city = city.replace(' Warriors', '').replace(' Rockets', '').replace(' Pacers', '')
        city = city.replace(' Clippers', '').replace(' Lakers', '').replace(' Grizzlies', '')
        city = city.replace(' Heat', '').replace(' Bucks', '').replace(' Timberwolves', '')
        city = city.replace(' Pelicans', '').replace(' Knicks', '').replace(' Thunder', '')
        city = city.replace(' Magic', '').replace(' 76ers', '').replace(' Suns', '')
        city = city.replace(' Trail Blazers', '').replace(' Kings', '').replace(' Spurs', '')
        city = city.replace(' Raptors', '').replace(' Jazz', '').replace(' Wizards', '')
        return city
    
    def _get_conference(self, team_name: str) -> str:
        """Get conference for team"""
        eastern_teams = {
            'Hawks', 'Celtics', 'Nets', 'Hornets', 'Bulls', 'Cavaliers', 
            'Pistons', 'Pacers', 'Heat', 'Bucks', 'Knicks', 'Magic',
            '76ers', 'Raptors', 'Wizards', 'SuperSonics', 'Royals', 
            'Nationals', 'Packers', 'Zephyrs', 'Bullets', 'Bobcats'
        }
        return 'Eastern' if team_name in eastern_teams else 'Western'
    
    def _get_division(self, team_name: str) -> str:
        """Get division for team"""
        divisions = {
            'Atlantic': {'Celtics', 'Nets', 'Knicks', '76ers', 'Raptors'},
            'Central': {'Bulls', 'Cavaliers', 'Pistons', 'Pacers', 'Bucks'},
            'Southeast': {'Hawks', 'Hornets', 'Heat', 'Magic', 'Wizards'},
            'Northwest': {'Nuggets', 'Timberwolves', 'Thunder', 'Trail Blazers', 'Jazz'},
            'Pacific': {'Warriors', 'Clippers', 'Lakers', 'Suns', 'Kings'},
            'Southwest': {'Mavericks', 'Rockets', 'Grizzlies', 'Pelicans', 'Spurs'}
        }
        
        for division, teams in divisions.items():
            if team_name in teams:
                return division
        return 'Unknown'
