"""
Import statistics data from CSV files
"""
import pandas as pd
from typing import Dict, List, Optional
from .database import DatabaseManager

# Import short team mapping
try:
    from short_team_mapping import SHORT_TEAM_MAPPING
except ImportError:
    SHORT_TEAM_MAPPING = {}

class StatsImporter:
    def __init__(self, db_manager: DatabaseManager, team_mapping: Dict[str, str], player_mapping: Dict[str, str]):
        self.db = db_manager
        self.team_mapping = team_mapping
        self.player_mapping = player_mapping
        self.stats_created = 0
        self.stats_skipped = 0
    
    async def import_team_stats_from_csv(self, csv_path: str):
        """Import team statistics from TeamStatistics.csv"""
        print(f"🔄 Importing team stats from {csv_path}")
        
        # Read CSV file
        df = pd.read_csv(csv_path)
        print(f"📊 Found {len(df)} team stat records")
        
        # Group by team and season (extract season from gameDate)
        # For playoffs, use the previous season since playoffs happen in April-June
        df['gameDate'] = pd.to_datetime(df['gameDate'])
        df['year'] = df['gameDate'].dt.year
        df['month'] = df['gameDate'].dt.month
        
        # For playoffs (April-June), use the previous year's season
        # For regular season and preseason (October-March), use the current year's season
        df['season_year'] = df['year']
        df.loc[(df['gameType'] == 'Playoffs') & (df['month'] >= 4) & (df['month'] <= 6), 'season_year'] = df['year'] - 1
        
        df['season'] = df['season_year'].astype(str) + '-' + (df['season_year'] + 1).astype(str).str[2:]
        
        grouped = df.groupby(['teamName', 'season'])
        
        for (team_name, season), group in grouped:
            try:
                # Get team ID using short team mapping first
                team_id = SHORT_TEAM_MAPPING.get(team_name)
                if not team_id:
                    # Fallback to full team mapping
                    team_id = self.team_mapping.get(team_name)
                if not team_id:
                    print(f"⚠️ Team not found: {team_name}")
                    continue
                
                # Calculate aggregated stats for the season
                stats_data = await self._process_team_stats_group(group, team_id, season)
                if not stats_data:
                    continue
                
                # Create team stats in database
                await self.db.create_team_stats(stats_data)
                self.stats_created += 1
                
                if self.stats_created % 100 == 0:
                    print(f"📊 Processed {self.stats_created} team stat records...")
                
            except Exception as e:
                print(f"❌ Error creating team stats for {team_name} {season}: {e}")
                self.stats_skipped += 1
        
        print(f"📊 Team stats import complete: {self.stats_created} created, {self.stats_skipped} skipped")
    
    async def import_player_stats_from_csv(self, csv_path: str):
        """Import player statistics from PlayerStatistics.csv"""
        print(f"🔄 Importing player stats from {csv_path}")
        
        # Read CSV file
        df = pd.read_csv(csv_path)
        print(f"📊 Found {len(df)} player stat records")
        
        # Group by player, season, and gameType (extract season from gameDate)
        # For playoffs, use the previous season since playoffs happen in April-June
        df['gameDate'] = pd.to_datetime(df['gameDate'])
        df['year'] = df['gameDate'].dt.year
        df['month'] = df['gameDate'].dt.month
        
        # For playoffs (April-June), use the previous year's season
        # For regular season and preseason (October-March), use the current year's season
        df['season_year'] = df['year']
        df.loc[(df['gameType'] == 'Playoffs') & (df['month'] >= 4) & (df['month'] <= 6), 'season_year'] = df['year'] - 1
        
        df['season'] = df['season_year'].astype(str) + '-' + (df['season_year'] + 1).astype(str).str[2:]
        
        grouped = df.groupby(['firstName', 'lastName', 'season', 'gameType'])
        
        for (first_name, last_name, season, game_type), group in grouped:
            try:
                # Get player ID
                player_name = f"{first_name} {last_name}"
                player_id = self.player_mapping.get(player_name)
                if not player_id:
                    print(f"⚠️ Player not found: {player_name}")
                    continue
                
                # Calculate aggregated stats for the season and game type
                stats_data = await self._process_player_stats_group(group, player_id, season, game_type)
                if not stats_data:
                    continue
                
                # Create player stats in database
                await self.db.create_player_stats(stats_data)
                self.stats_created += 1
                
                if self.stats_created % 500 == 0:
                    print(f"📊 Processed {self.stats_created} player stat records...")
                
            except Exception as e:
                print(f"❌ Error creating player stats for {player_name} {season} {game_type}: {e}")
                self.stats_skipped += 1
        
        print(f"📊 Player stats import complete: {self.stats_created} created, {self.stats_skipped} skipped")
    
    async def _process_team_stats_group(self, group: pd.DataFrame, team_id: str, season: str) -> Optional[Dict]:
        """Process team stats for a season"""
        try:
            # Calculate basic stats
            games_played = len(group)
            wins = len(group[group['win'] == 1]) if 'win' in group.columns else 0
            losses = games_played - wins
            
            # Calculate averages
            points_per_game = self._safe_float(group['teamScore'].mean()) if 'teamScore' in group.columns else 0
            points_allowed = self._safe_float(group['opponentScore'].mean()) if 'opponentScore' in group.columns else 0
            
            # Calculate shooting percentages (if available)
            field_goal_pct = self._safe_float(group['fieldGoalsPercentage'].mean()) if 'fieldGoalsPercentage' in group.columns else 0
            three_point_pct = self._safe_float(group['threePointersPercentage'].mean()) if 'threePointersPercentage' in group.columns else 0
            free_throw_pct = self._safe_float(group['freeThrowsPercentage'].mean()) if 'freeThrowsPercentage' in group.columns else 0
            
            # Calculate other stats (if available)
            rebounds = self._safe_float(group['reboundsTotal'].mean()) if 'reboundsTotal' in group.columns else 0
            assists = self._safe_float(group['assists'].mean()) if 'assists' in group.columns else 0
            turnovers = self._safe_float(group['turnovers'].mean()) if 'turnovers' in group.columns else 0
            steals = self._safe_float(group['steals'].mean()) if 'steals' in group.columns else 0
            blocks = self._safe_float(group['blocks'].mean()) if 'blocks' in group.columns else 0
            
            return {
                'teamId': team_id,
                'season': season,
                'gamesPlayed': games_played,
                'wins': wins,
                'losses': losses,
                'pointsPerGame': points_per_game,
                'pointsAllowed': points_allowed,
                'fieldGoalPct': field_goal_pct,
                'threePointPct': three_point_pct,
                'freeThrowPct': free_throw_pct,
                'rebounds': rebounds,
                'assists': assists,
                'turnovers': turnovers,
                'steals': steals,
                'blocks': blocks
            }
            
        except Exception as e:
            print(f"❌ Error processing team stats: {e}")
            return None
    
    async def _process_player_stats_group(self, group: pd.DataFrame, player_id: str, season: str, game_type: str) -> Optional[Dict]:
        """Process player stats for a season and game type"""
        try:
            # Calculate basic stats
            games_played = len(group)
            
            # Calculate averages
            minutes_per_game = self._safe_float(group['numMinutes'].mean()) if 'numMinutes' in group.columns else 0
            points_per_game = self._safe_float(group['points'].mean()) if 'points' in group.columns else 0
            rebounds = self._safe_float(group['reboundsTotal'].mean()) if 'reboundsTotal' in group.columns else 0
            assists = self._safe_float(group['assists'].mean()) if 'assists' in group.columns else 0
            steals = self._safe_float(group['steals'].mean()) if 'steals' in group.columns else 0
            blocks = self._safe_float(group['blocks'].mean()) if 'blocks' in group.columns else 0
            turnovers = self._safe_float(group['turnovers'].mean()) if 'turnovers' in group.columns else 0
            
            # Calculate shooting percentages
            field_goal_pct = self._safe_float(group['fieldGoalsPercentage'].mean()) if 'fieldGoalsPercentage' in group.columns else 0
            three_point_pct = self._safe_float(group['threePointersPercentage'].mean()) if 'threePointersPercentage' in group.columns else 0
            free_throw_pct = self._safe_float(group['freeThrowsPercentage'].mean()) if 'freeThrowsPercentage' in group.columns else 0
            
            return {
                'playerId': player_id,
                'season': season,
                'seasonType': game_type,
                'gamesPlayed': games_played,
                'minutesPerGame': minutes_per_game,
                'pointsPerGame': points_per_game,
                'rebounds': rebounds,
                'assists': assists,
                'steals': steals,
                'blocks': blocks,
                'turnovers': turnovers,
                'fieldGoalPct': field_goal_pct,
                'threePointPct': three_point_pct,
                'freeThrowPct': free_throw_pct
            }
            
        except Exception as e:
            print(f"❌ Error processing player stats: {e}")
            return None
    
    def _safe_float(self, value) -> float:
        """Safely convert value to float"""
        if pd.isna(value) or value == '' or value is None:
            return 0.0
        
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0
