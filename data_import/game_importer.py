"""
Import game data from CSV files
"""
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
from .database import DatabaseManager

# Import team mapping
try:
    from team_mapping import TEAM_MAPPING
except ImportError:
    TEAM_MAPPING = {}

class GameImporter:
    def __init__(self, db_manager: DatabaseManager, team_mapping: Dict[str, str]):
        self.db = db_manager
        self.team_mapping = team_mapping
        self.games_created = 0
        self.games_skipped = 0
    
    async def import_games_from_csv(self, csv_path: str):
        """Import games from Games.csv"""
        print(f"🔄 Importing games from {csv_path}")
        
        # Read CSV file
        df = pd.read_csv(csv_path)
        print(f"📊 Found {len(df)} game records")
        
        # Get existing games to avoid duplicates
        existing_games = await self.db.get_existing_games()
        existing_game_keys = set()
        for game in existing_games:
            key = f"{game['gameDate']}_{game['homeTeamId']}_{game['awayTeamId']}"
            existing_game_keys.add(key)
        
        for _, row in df.iterrows():
            try:
                # Extract game information
                game_data = await self._process_game_row(row)
                if not game_data:
                    self.games_skipped += 1
                    continue
                
                # Check if game already exists
                game_key = f"{game_data['gameDate']}_{game_data['homeTeamId']}_{game_data['awayTeamId']}"
                if game_key in existing_game_keys:
                    self.games_skipped += 1
                    continue
                
                # Create game in database
                await self.db.create_game(game_data)
                self.games_created += 1
                
                if self.games_created % 1000 == 0:
                    print(f"📊 Processed {self.games_created} games...")
                
            except Exception as e:
                print(f"❌ Error creating game: {e}")
                self.games_skipped += 1
        
        print(f"📊 Game import complete: {self.games_created} created, {self.games_skipped} skipped")
        return {}  # Return empty dict for now since we don't track game mapping
    
    async def _process_game_row(self, row: pd.Series) -> Optional[Dict]:
        """Process a single game row from CSV"""
        try:
            # Extract basic game information from your actual CSV format
            home_team = f"{str(row.get('hometeamCity', '') or '').strip()} {str(row.get('hometeamName', '') or '').strip()}".strip()
            away_team = f"{str(row.get('awayteamCity', '') or '').strip()} {str(row.get('awayteamName', '') or '').strip()}".strip()
            
            if not home_team or not away_team:
                return None
            
            # Get team IDs from mapping (try both local and global mapping)
            home_team_id = self.team_mapping.get(home_team) or TEAM_MAPPING.get(home_team)
            away_team_id = self.team_mapping.get(away_team) or TEAM_MAPPING.get(away_team)
            
            if not home_team_id or not away_team_id:
                print(f"⚠️ Team not found: {home_team} or {away_team}")
                return None
            
            # Parse game date
            game_date = self._parse_game_date(row.get('gameDate', ''))
            if not game_date:
                return None
            
            # Extract scores
            home_score = self._safe_int(row.get('homeScore'))
            away_score = self._safe_int(row.get('awayScore'))
            
            # Determine game status
            status = 'Final' if home_score is not None and away_score is not None else 'Scheduled'
            
            # Extract season information
            season = self._extract_season(game_date)
            season_type = self._get_season_type(row.get('gameType', 'Regular Season'))
            
            # Extract additional information
            attendance = self._safe_int(row.get('attendance'))
            venue = str(row.get('gameLabel', '') or '').strip() or None
            
            return {
                'gameDate': game_date,
                'season': season,
                'seasonType': season_type,
                'homeTeamId': home_team_id,
                'awayTeamId': away_team_id,
                'homeScore': home_score,
                'awayScore': away_score,
                'status': status,
                'attendance': attendance,
                'venue': venue
            }
            
        except Exception as e:
            print(f"❌ Error processing game row: {e}")
            return None
    
    def _parse_game_date(self, date_str: str) -> Optional[datetime]:
        """Parse game date from string"""
        if not date_str or pd.isna(date_str):
            return None
        
        try:
            # Try different date formats
            date_formats = [
                '%Y-%m-%d',
                '%m/%d/%Y',
                '%d/%m/%Y',
                '%Y-%m-%d %H:%M:%S',
                '%m/%d/%Y %H:%M:%S'
            ]
            
            for fmt in date_formats:
                try:
                    return datetime.strptime(str(date_str), fmt)
                except ValueError:
                    continue
            
            # If none work, try pandas parsing
            return pd.to_datetime(date_str)
            
        except Exception as e:
            print(f"❌ Error parsing date '{date_str}': {e}")
            return None
    
    def _extract_season(self, game_date: datetime) -> str:
        """Extract season from game date"""
        year = game_date.year
        month = game_date.month
        
        # NBA season typically starts in October
        if month >= 10:
            return f"{year}-{str(year + 1)[2:]}"
        else:
            return f"{year - 1}-{str(year)[2:]}"
    
    def _get_season_type(self, season_type: str) -> str:
        """Normalize season type"""
        if not season_type or pd.isna(season_type):
            return 'Regular Season'
        
        season_type = str(season_type).strip().lower()
        if 'playoff' in season_type:
            return 'Playoffs'
        elif 'preseason' in season_type:
            return 'Preseason'
        else:
            return 'Regular Season'
    
    def _safe_int(self, value) -> Optional[int]:
        """Safely convert value to int"""
        if pd.isna(value) or value == '' or value is None:
            return None
        
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None
