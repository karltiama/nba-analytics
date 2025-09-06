"""
Import player data from CSV files
"""
import pandas as pd
from typing import Dict, List, Optional
from .database import DatabaseManager

class PlayerImporter:
    def __init__(self, db_manager: DatabaseManager, team_mapping: Dict[str, str]):
        self.db = db_manager
        self.team_mapping = team_mapping
        self.players_created = 0
        self.players_skipped = 0
    
    async def import_players_from_csv(self, csv_path: str):
        """Import players from Players.csv"""
        print(f"🔄 Importing players from {csv_path}")
        
        # Read CSV file
        df = pd.read_csv(csv_path)
        print(f"📊 Found {len(df)} player records")
        
        # Get existing players to avoid duplicates
        existing_players = await self.db.get_existing_players()
        existing_names = {player['name'] for player in existing_players}
        
        for _, row in df.iterrows():
            try:
                # Extract player information
                player_data = await self._process_player_row(row)
                if not player_data:
                    self.players_skipped += 1
                    continue
                
                # Check if player already exists
                if player_data['name'] in existing_names:
                    self.players_skipped += 1
                    continue
                
                # Create player in database
                await self.db.create_player(player_data)
                self.players_created += 1
                
                if self.players_created % 500 == 0:
                    print(f"📊 Processed {self.players_created} players...")
                
            except Exception as e:
                print(f"❌ Error creating player: {e}")
                self.players_skipped += 1
        
        print(f"📊 Player import complete: {self.players_created} created, {self.players_skipped} skipped")
        return self.player_mapping if hasattr(self, 'player_mapping') and self.player_mapping else {}
    
    async def _process_player_row(self, row: pd.Series) -> Optional[Dict]:
        """Process a single player row from CSV"""
        try:
            # Extract basic player information from your actual CSV format
            first_name = str(row.get('firstName', '') or '').strip()
            last_name = str(row.get('lastName', '') or '').strip()
            name = f"{first_name} {last_name}".strip()
            
            if not name:
                return None
            
            # Extract position from your position flags
            position = self._determine_position_from_flags(
                bool(row.get('guard', False)),
                bool(row.get('forward', False)),
                bool(row.get('center', False))
            )
            
            # Extract physical attributes
            height = self._safe_int(row.get('height'))
            weight = self._safe_int(row.get('bodyWeight'))
            jersey_number = None  # Not available in your data
            
            # Extract team information (not available in Players.csv, will be set later)
            team_id = None
            
            # Determine if player is active (based on draft year)
            is_active = self._is_player_active(row)
            
            return {
                'name': name,
                'position': position,
                'height': height,
                'weight': weight,
                'jerseyNumber': jersey_number,
                'teamId': team_id,
                'isActive': is_active
            }
            
        except Exception as e:
            print(f"❌ Error processing player row: {e}")
            return None
    
    def _determine_position_from_flags(self, guard: bool, forward: bool, center: bool) -> str:
        """Determine position from guard/forward/center flags"""
        if center:
            return 'C'
        elif forward and guard:
            return 'SF'  # Small Forward
        elif forward:
            return 'PF'  # Power Forward
        elif guard:
            return 'PG'  # Point Guard
        else:
            return 'Unknown'
    
    def _normalize_position(self, position: str) -> str:
        """Normalize player position"""
        if not position or pd.isna(position):
            return 'Unknown'
        
        position = str(position).strip().upper()
        
        # Map common position variations
        position_mapping = {
            'PG': 'PG', 'POINT GUARD': 'PG', 'G': 'PG',
            'SG': 'SG', 'SHOOTING GUARD': 'SG', 'G-F': 'SG',
            'SF': 'SF', 'SMALL FORWARD': 'SF', 'F': 'SF', 'F-G': 'SF',
            'PF': 'PF', 'POWER FORWARD': 'PF', 'F-C': 'PF',
            'C': 'C', 'CENTER': 'C', 'C-F': 'C'
        }
        
        return position_mapping.get(position, position)
    
    def _parse_height(self, height_str: str) -> Optional[int]:
        """Parse height from string (convert to inches)"""
        if not height_str or pd.isna(height_str):
            return None
        
        try:
            height_str = str(height_str).strip()
            
            # Handle format like "6-8" or "6'8\""
            if '-' in height_str:
                feet, inches = height_str.split('-')
                return int(feet) * 12 + int(inches)
            elif "'" in height_str and '"' in height_str:
                # Format like "6'8\""
                parts = height_str.replace('"', '').split("'")
                feet = int(parts[0])
                inches = int(parts[1]) if len(parts) > 1 else 0
                return feet * 12 + inches
            else:
                # Assume it's already in inches
                return int(float(height_str))
                
        except (ValueError, TypeError):
            return None
    
    def _is_player_active(self, row: pd.Series) -> bool:
        """Determine if player is currently active"""
        # This is a simple heuristic - you might need to adjust based on your data
        # You could check for recent seasons, current team, etc.
        team = row.get('Team', '').strip()
        return bool(team)  # If they have a team, they're active
    
    def _safe_int(self, value) -> Optional[int]:
        """Safely convert value to int"""
        if pd.isna(value) or value == '' or value is None:
            return None
        
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None
