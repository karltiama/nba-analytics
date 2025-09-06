#!/usr/bin/env python3
"""
Import player statistics for just the most recent year (2023-24)
"""
import asyncio
import sys
import pandas as pd
from pathlib import Path
from typing import Dict, List
import time

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from data_import.database import DatabaseManager

# Import short team mapping
try:
    from short_team_mapping import SHORT_TEAM_MAPPING
except ImportError:
    SHORT_TEAM_MAPPING = {}

class RecentYearPlayerStatsImporter:
    def __init__(self, db_manager: DatabaseManager, team_mapping: Dict[str, str], player_mapping: Dict[str, str]):
        self.db = db_manager
        self.team_mapping = team_mapping
        self.player_mapping = player_mapping
        self.stats_created = 0
        self.stats_skipped = 0
        self.stats_updated = 0
    
    def _safe_float(self, value) -> float:
        """Safely convert value to float"""
        try:
            return float(value) if pd.notna(value) and value != '' else 0.0
        except (ValueError, TypeError):
            return 0.0
    
    async def import_recent_year_stats(self, csv_path: str, target_year: int = 2023):
        """Import player statistics for just the most recent year"""
        print(f"🚀 Importing player stats for {target_year}-{target_year+1} season from {csv_path}")
        start_time = time.time()
        
        # Read CSV file and filter by year
        print("📊 Reading and filtering CSV data...")
        df = pd.read_csv(csv_path, low_memory=False)
        print(f"📊 Total records in CSV: {len(df):,}")
        
        # Convert gameDate to datetime and filter
        df['gameDate'] = pd.to_datetime(df['gameDate'])
        df['year'] = df['gameDate'].dt.year
        recent_df = df[df['year'] == target_year].copy()
        print(f"📊 Records for {target_year}-{target_year+1} season: {len(recent_df):,}")
        
        if len(recent_df) == 0:
            print(f"❌ No data found for {target_year}!")
            return
        
        # Add season column
        recent_df['season'] = f"{target_year}-{str(target_year+1)[2:]}"
        
        # Group by player and season
        grouped = recent_df.groupby(['firstName', 'lastName', 'season'])
        total_groups = len(grouped)
        print(f"📊 Processing {total_groups} player-season combinations...")
        
        processed = 0
        for (first_name, last_name, season), group in grouped:
            try:
                # Get player ID
                player_name = f"{first_name} {last_name}"
                player_id = self.player_mapping.get(player_name)
                if not player_id:
                    print(f"⚠️ Player not found: {player_name}")
                    self.stats_skipped += 1
                    continue
                
                # Calculate aggregated stats for the season
                stats_data = self._calculate_player_stats(group, player_id, season)
                if stats_data:
                    # Insert or update individual record
                    await self._upsert_player_stats(stats_data)
                    
                    if self.stats_created % 50 == 0:
                        elapsed = time.time() - start_time
                        rate = processed / elapsed if elapsed > 0 else 0
                        print(f"📊 Processed {processed}/{total_groups} ({processed/total_groups*100:.1f}%) - {rate:.0f} records/sec")
                
                processed += 1
                    
            except Exception as e:
                print(f"❌ Error processing {first_name} {last_name} {season}: {e}")
                self.stats_skipped += 1
                processed += 1
        
        total_time = time.time() - start_time
        print(f"✅ Recent year player stats import completed!")
        print(f"📊 Total processed: {processed:,} player-season combinations")
        print(f"📊 Stats created: {self.stats_created:,}")
        print(f"📊 Stats updated: {self.stats_updated:,}")
        print(f"📊 Stats skipped: {self.stats_skipped:,}")
        print(f"⏱️ Total time: {total_time:.1f}s")
        print(f"🚀 Average rate: {processed/total_time:.0f} records/sec")
    
    async def _upsert_player_stats(self, stats_data: Dict):
        """Insert or update a single player stats record"""
        try:
            # First, check if record exists
            check_query = """
            SELECT id FROM player_stats 
            WHERE "playerId" = %s AND season = %s
            """
            
            self.db.cursor.execute(check_query, (stats_data.get('playerId'), stats_data.get('season')))
            existing = self.db.cursor.fetchone()
            
            if existing:
                # Update existing record
                update_query = """
                UPDATE player_stats SET
                    "gamesPlayed" = %s,
                    "minutesPerGame" = %s,
                    "pointsPerGame" = %s,
                    rebounds = %s,
                    assists = %s,
                    steals = %s,
                    blocks = %s,
                    turnovers = %s,
                    "fieldGoalPct" = %s,
                    "threePointPct" = %s,
                    "freeThrowPct" = %s,
                    "updatedAt" = NOW()
                WHERE "playerId" = %s AND season = %s
                """
                
                values = (
                    stats_data.get('gamesPlayed', 0),
                    stats_data.get('minutesPerGame', 0),
                    stats_data.get('pointsPerGame', 0),
                    stats_data.get('rebounds', 0),
                    stats_data.get('assists', 0),
                    stats_data.get('steals', 0),
                    stats_data.get('blocks', 0),
                    stats_data.get('turnovers', 0),
                    stats_data.get('fieldGoalPct', 0),
                    stats_data.get('threePointPct', 0),
                    stats_data.get('freeThrowPct', 0),
                    stats_data.get('playerId'),
                    stats_data.get('season')
                )
                
                self.db.cursor.execute(update_query, values)
                self.stats_updated += 1
            else:
                # Insert new record
                insert_query = """
                INSERT INTO player_stats (
                    id, "playerId", season, "gamesPlayed", "minutesPerGame", "pointsPerGame",
                    rebounds, assists, steals, blocks, turnovers,
                    "fieldGoalPct", "threePointPct", "freeThrowPct", "createdAt", "updatedAt"
                ) VALUES (
                    gen_random_uuid(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
                )
                """
                
                values = (
                    stats_data.get('playerId'),
                    stats_data.get('season'),
                    stats_data.get('gamesPlayed', 0),
                    stats_data.get('minutesPerGame', 0),
                    stats_data.get('pointsPerGame', 0),
                    stats_data.get('rebounds', 0),
                    stats_data.get('assists', 0),
                    stats_data.get('steals', 0),
                    stats_data.get('blocks', 0),
                    stats_data.get('turnovers', 0),
                    stats_data.get('fieldGoalPct', 0),
                    stats_data.get('threePointPct', 0),
                    stats_data.get('freeThrowPct', 0)
                )
                
                self.db.cursor.execute(insert_query, values)
                self.stats_created += 1
            
            # Commit after each record for reliability
            self.db.connection.commit()
            
        except Exception as e:
            print(f"❌ Error upserting player stats: {e}")
            self.db.connection.rollback()
            raise
    
    def _calculate_player_stats(self, group: pd.DataFrame, player_id: str, season: str) -> Dict:
        """Calculate player statistics for a season"""
        try:
            # Basic stats
            games_played = len(group)
            
            # Calculate averages
            points_per_game = self._safe_float(group['points'].mean()) if 'points' in group.columns else 0
            rebounds_per_game = self._safe_float(group['reboundsTotal'].mean()) if 'reboundsTotal' in group.columns else 0
            assists_per_game = self._safe_float(group['assists'].mean()) if 'assists' in group.columns else 0
            steals_per_game = self._safe_float(group['steals'].mean()) if 'steals' in group.columns else 0
            blocks_per_game = self._safe_float(group['blocks'].mean()) if 'blocks' in group.columns else 0
            turnovers_per_game = self._safe_float(group['turnovers'].mean()) if 'turnovers' in group.columns else 0
            minutes_per_game = self._safe_float(group['numMinutes'].mean()) if 'numMinutes' in group.columns else 0
            
            # Shooting percentages
            field_goal_pct = self._safe_float(group['fieldGoalsPercentage'].mean()) if 'fieldGoalsPercentage' in group.columns else 0
            three_point_pct = self._safe_float(group['threePointersPercentage'].mean()) if 'threePointersPercentage' in group.columns else 0
            free_throw_pct = self._safe_float(group['freeThrowsPercentage'].mean()) if 'freeThrowsPercentage' in group.columns else 0
            
            return {
                'playerId': player_id,
                'season': season,
                'gamesPlayed': games_played,
                'minutesPerGame': minutes_per_game,
                'pointsPerGame': points_per_game,
                'rebounds': rebounds_per_game,
                'assists': assists_per_game,
                'steals': steals_per_game,
                'blocks': blocks_per_game,
                'turnovers': turnovers_per_game,
                'fieldGoalPct': field_goal_pct,
                'threePointPct': three_point_pct,
                'freeThrowPct': free_throw_pct
            }
        except Exception as e:
            print(f"❌ Error calculating stats: {e}")
            return None

async def main():
    """Import recent year player statistics"""
    print("🚀 Starting Recent Year Player Statistics Import (2023-24 Season)...")
    
    db_manager = DatabaseManager()
    
    try:
        # Connect to database
        await db_manager.connect()
        
        # Get existing teams and players for mapping
        existing_teams = await db_manager.get_existing_teams()
        existing_players = await db_manager.get_existing_players()
        team_mapping = {team['name']: team['id'] for team in existing_teams}
        player_mapping = {player['name']: player['id'] for player in existing_players}
        
        print(f"📊 Found {len(team_mapping)} teams and {len(player_mapping)} players")
        
        # Create recent year importer
        importer = RecentYearPlayerStatsImporter(db_manager, team_mapping, player_mapping)
        
        # Import recent year player stats (2023-24 season)
        await importer.import_recent_year_stats("data/PlayerStatistics.csv", target_year=2023)
        
    except Exception as e:
        print(f"❌ Error during recent year player stats import: {e}")
        raise
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
