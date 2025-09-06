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
        
        for _, row in df.iterrows():
            try:
                # Extract team information from your actual CSV format
                team_name = f"{row.get('teamCity', '').strip()} {row.get('teamName', '').strip()}".strip()
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
            'Atlanta Hawks': 'ATL',
            'Boston Celtics': 'BOS',
            'Brooklyn Nets': 'BKN',
            'Charlotte Hornets': 'CHA',
            'Chicago Bulls': 'CHI',
            'Cleveland Cavaliers': 'CLE',
            'Dallas Mavericks': 'DAL',
            'Denver Nuggets': 'DEN',
            'Detroit Pistons': 'DET',
            'Golden State Warriors': 'GSW',
            'Houston Rockets': 'HOU',
            'Indiana Pacers': 'IND',
            'Los Angeles Clippers': 'LAC',
            'Los Angeles Lakers': 'LAL',
            'Memphis Grizzlies': 'MEM',
            'Miami Heat': 'MIA',
            'Milwaukee Bucks': 'MIL',
            'Minnesota Timberwolves': 'MIN',
            'New Orleans Pelicans': 'NOP',
            'New York Knicks': 'NYK',
            'Oklahoma City Thunder': 'OKC',
            'Orlando Magic': 'ORL',
            'Philadelphia 76ers': 'PHI',
            'Phoenix Suns': 'PHX',
            'Portland Trail Blazers': 'POR',
            'Sacramento Kings': 'SAC',
            'San Antonio Spurs': 'SAS',
            'Toronto Raptors': 'TOR',
            'Utah Jazz': 'UTA',
            'Washington Wizards': 'WAS'
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
            'Atlanta Hawks', 'Boston Celtics', 'Brooklyn Nets', 'Charlotte Hornets',
            'Chicago Bulls', 'Cleveland Cavaliers', 'Detroit Pistons', 'Indiana Pacers',
            'Miami Heat', 'Milwaukee Bucks', 'New York Knicks', 'Orlando Magic',
            'Philadelphia 76ers', 'Toronto Raptors', 'Washington Wizards'
        }
        return 'Eastern' if team_name in eastern_teams else 'Western'
    
    def _get_division(self, team_name: str) -> str:
        """Get division for team"""
        divisions = {
            'Atlantic': {'Boston Celtics', 'Brooklyn Nets', 'New York Knicks', 'Philadelphia 76ers', 'Toronto Raptors'},
            'Central': {'Chicago Bulls', 'Cleveland Cavaliers', 'Detroit Pistons', 'Indiana Pacers', 'Milwaukee Bucks'},
            'Southeast': {'Atlanta Hawks', 'Charlotte Hornets', 'Miami Heat', 'Orlando Magic', 'Washington Wizards'},
            'Northwest': {'Denver Nuggets', 'Minnesota Timberwolves', 'Oklahoma City Thunder', 'Portland Trail Blazers', 'Utah Jazz'},
            'Pacific': {'Golden State Warriors', 'Los Angeles Clippers', 'Los Angeles Lakers', 'Phoenix Suns', 'Sacramento Kings'},
            'Southwest': {'Dallas Mavericks', 'Houston Rockets', 'Memphis Grizzlies', 'New Orleans Pelicans', 'San Antonio Spurs'}
        }
        
        for division, teams in divisions.items():
            if team_name in teams:
                return division
        return 'Unknown'
