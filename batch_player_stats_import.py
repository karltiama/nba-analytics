#!/usr/bin/env python3
"""
Batch import player statistics for all years with optimized performance
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

class BatchPlayerStatsImporter:
    def __init__(self, db_manager: DatabaseManager, team_mapping: Dict[str, str], player_mapping: Dict[str, str]):
        self.db = db_manager
        self.team_mapping = team_mapping
        self.player_mapping = player_mapping
        self.stats_created = 0
        self.stats_skipped = 0
        self.stats_updated = 0
        self.batch_size = 1000  # Process 1000 records at a time
    
    def _safe_float(self, value) -> float:
        """Safely convert value to float"""
        try:
            return float(value) if pd.notna(value) and value != '' else 0.0
        except (ValueError, TypeError):
            return 0.0
    
    async def import_all_stats_batch(self, csv_path: str, start_year: int = 2014, end_year: int = 2024):
        """Import player statistics for all years using batch processing"""
        print(f"🚀 Batch importing player stats for {start_year}-{end_year} seasons from {csv_path}")
        start_time = time.time()
        
        # Read CSV file and filter by year range
        print("📊 Reading and filtering CSV data...")
        df = pd.read_csv(csv_path, low_memory=False)
        print(f"📊 Total records in CSV: {len(df):,}")
        
        # Convert gameDate to datetime and filter
        df['gameDate'] = pd.to_datetime(df['gameDate'])
        df['year'] = df['gameDate'].dt.year
        filtered_df = df[(df['year'] >= start_year) & (df['year'] <= end_year)].copy()
        print(f"📊 Records for {start_year}-{end_year} seasons: {len(filtered_df):,}")
        
        if len(filtered_df) == 0:
            print("❌ No data found!")
            return
        
        # Add season column
        filtered_df['season'] = filtered_df['gameDate'].dt.year
        filtered_df['season'] = filtered_df['season'].astype(str) + '-' + (filtered_df['season'] + 1).astype(str).str[2:]
        
        # Group by player and season
        grouped = filtered_df.groupby(['firstName', 'lastName', 'season'])
        total_groups = len(grouped)
        print(f"📊 Processing {total_groups:,} player-season combinations in batches of {self.batch_size:,}...")
        
        # Process in batches
        batch_data = []
        processed = 0
        
        for (first_name, last_name, season), group in grouped:
            try:
                # Get player ID
                player_name = f"{first_name} {last_name}"
                player_id = self.player_mapping.get(player_name)
                if not player_id:
                    self.stats_skipped += 1
                    continue
                
                # Calculate aggregated stats for the season
                stats_data = self._calculate_player_stats(group, player_id, season)
                if stats_data:
                    batch_data.append(stats_data)
                
                # Process batch when it reaches batch_size
                if len(batch_data) >= self.batch_size:
                    await self._process_batch(batch_data)
                    batch_data = []
                    
                    if processed % (self.batch_size * 5) == 0:  # Progress every 5 batches
                        elapsed = time.time() - start_time
                        rate = processed / elapsed if elapsed > 0 else 0
                        print(f"📊 Processed {processed:,}/{total_groups:,} ({processed/total_groups*100:.1f}%) - {rate:.0f} records/sec")
                
                processed += 1
                    
            except Exception as e:
                if processed % 10000 == 0:  # Only print every 10k to avoid spam
                    print(f"❌ Error processing {first_name} {last_name} {season}: {e}")
                self.stats_skipped += 1
                processed += 1
        
        # Process remaining batch
        if batch_data:
            await self._process_batch(batch_data)
        
        total_time = time.time() - start_time
        print(f"✅ Batch player stats import completed!")
        print(f"📊 Total processed: {processed:,} player-season combinations")
        print(f"📊 Stats created: {self.stats_created:,}")
        print(f"📊 Stats updated: {self.stats_updated:,}")
        print(f"📊 Stats skipped: {self.stats_skipped:,}")
        print(f"⏱️ Total time: {total_time:.1f}s")
        print(f"🚀 Average rate: {processed/total_time:.0f} records/sec")
    
    async def _process_batch(self, batch_data: List[Dict]):
        """Process a batch of player stats using bulk operations"""
        if not batch_data:
            return
        
        try:
            # Prepare bulk insert data
            insert_data = []
            update_data = []
            
            for stats in batch_data:
                # Check if record exists
                check_query = """
                SELECT id FROM player_stats 
                WHERE "playerId" = %s AND season = %s
                """
                
                self.db.cursor.execute(check_query, (stats.get('playerId'), stats.get('season')))
                existing = self.db.cursor.fetchone()
                
                if existing:
                    # Prepare for update
                    update_data.append((
                        stats.get('gamesPlayed', 0),
                        stats.get('minutesPerGame', 0),
                        stats.get('pointsPerGame', 0),
                        stats.get('rebounds', 0),
                        stats.get('assists', 0),
                        stats.get('steals', 0),
                        stats.get('blocks', 0),
                        stats.get('turnovers', 0),
                        stats.get('fieldGoalPct', 0),
                        stats.get('threePointPct', 0),
                        stats.get('freeThrowPct', 0),
                        stats.get('playerId'),
                        stats.get('season')
                    ))
                else:
                    # Prepare for insert
                    insert_data.append((
                        stats.get('playerId'),
                        stats.get('season'),
                        stats.get('gamesPlayed', 0),
                        stats.get('minutesPerGame', 0),
                        stats.get('pointsPerGame', 0),
                        stats.get('rebounds', 0),
                        stats.get('assists', 0),
                        stats.get('steals', 0),
                        stats.get('blocks', 0),
                        stats.get('turnovers', 0),
                        stats.get('fieldGoalPct', 0),
                        stats.get('threePointPct', 0),
                        stats.get('freeThrowPct', 0)
                    ))
            
            # Bulk insert new records
            if insert_data:
                insert_query = """
                INSERT INTO player_stats (
                    id, "playerId", season, "gamesPlayed", "minutesPerGame", "pointsPerGame",
                    rebounds, assists, steals, blocks, turnovers,
                    "fieldGoalPct", "threePointPct", "freeThrowPct", "createdAt", "updatedAt"
                ) VALUES (
                    gen_random_uuid(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
                )
                """
                self.db.cursor.executemany(insert_query, insert_data)
                self.stats_created += len(insert_data)
            
            # Bulk update existing records
            if update_data:
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
                self.db.cursor.executemany(update_query, update_data)
                self.stats_updated += len(update_data)
            
            # Commit the batch
            self.db.connection.commit()
            
        except Exception as e:
            print(f"❌ Error processing batch: {e}")
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
    """Import all player statistics using batch processing"""
    print("🚀 Starting Batch Player Statistics Import (All Years)...")
    
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
        
        # Create batch importer
        importer = BatchPlayerStatsImporter(db_manager, team_mapping, player_mapping)
        
        # Import all player stats (2014-2024 seasons)
        await importer.import_all_stats_batch("data/PlayerStatistics.csv", start_year=2014, end_year=2024)
        
    except Exception as e:
        print(f"❌ Error during batch player stats import: {e}")
        raise
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(main())

