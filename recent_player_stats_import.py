#!/usr/bin/env python3
"""
Import player statistics for the last 5 years only
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

class RecentPlayerStatsImporter:
    def __init__(self, db_manager: DatabaseManager, team_mapping: Dict[str, str], player_mapping: Dict[str, str]):
        self.db = db_manager
        self.team_mapping = team_mapping
        self.player_mapping = player_mapping
        self.stats_created = 0
        self.stats_skipped = 0
        self.batch_size = 1000
    
    def _safe_float(self, value) -> float:
        """Safely convert value to float"""
        try:
            return float(value) if pd.notna(value) and value != '' else 0.0
        except (ValueError, TypeError):
            return 0.0
    
    async def import_recent_player_stats(self, csv_path: str, years_back: int = 5):
        """Import player statistics for recent years only"""
        print(f"🚀 Importing player stats for last {years_back} years from {csv_path}")
        start_time = time.time()
        
        # Calculate cutoff date
        current_year = 2024  # Current NBA season
        cutoff_year = current_year - years_back
        print(f"📅 Importing data from {cutoff_year} onwards")
        
        # Read CSV file and filter by date
        print("📊 Reading and filtering CSV data...")
        df = pd.read_csv(csv_path, low_memory=False)
        print(f"📊 Total records in CSV: {len(df):,}")
        
        # Convert gameDate to datetime and filter
        df['gameDate'] = pd.to_datetime(df['gameDate'])
        df['year'] = df['gameDate'].dt.year
        recent_df = df[df['year'] >= cutoff_year].copy()
        print(f"📊 Records for last {years_back} years: {len(recent_df):,}")
        
        if len(recent_df) == 0:
            print("❌ No recent data found!")
            return
        
        # Process in chunks
        chunk_size = 20000
        total_processed = 0
        
        for chunk_num in range(0, len(recent_df), chunk_size):
            chunk = recent_df.iloc[chunk_num:chunk_num + chunk_size]
            print(f"📊 Processing chunk {chunk_num // chunk_size + 1} ({len(chunk)} records)...")
            
            await self._process_chunk_recent(chunk)
            total_processed += len(chunk)
            
            elapsed = time.time() - start_time
            rate = total_processed / elapsed if elapsed > 0 else 0
            print(f"⏱️ Processed {total_processed:,} records in {elapsed:.1f}s ({rate:.0f} records/sec)")
            print(f"📊 Stats created: {self.stats_created}, skipped: {self.stats_skipped}")
        
        total_time = time.time() - start_time
        print(f"✅ Recent player stats import completed!")
        print(f"📊 Total processed: {total_processed:,} records")
        print(f"📊 Stats created: {self.stats_created:,}")
        print(f"📊 Stats skipped: {self.stats_skipped:,}")
        print(f"⏱️ Total time: {total_time:.1f}s")
        print(f"🚀 Average rate: {total_processed/total_time:.0f} records/sec")
    
    async def _process_chunk_recent(self, chunk: pd.DataFrame):
        """Process a chunk of recent data"""
        # Add season column
        chunk['season'] = chunk['gameDate'].dt.year
        chunk['season'] = chunk['season'].astype(str) + '-' + (chunk['season'] + 1).astype(str).str[2:]
        
        # Group by player and season
        grouped = chunk.groupby(['firstName', 'lastName', 'season'])
        
        # Process in batches
        batch_data = []
        batch_count = 0
        
        for (first_name, last_name, season), group in grouped:
            try:
                # Get player ID
                player_name = f"{first_name} {last_name}"
                player_id = self.player_mapping.get(player_name)
                if not player_id:
                    self.stats_skipped += 1
                    continue
                
                # Calculate aggregated stats for the season
                stats_data = self._calculate_player_stats_recent(group, player_id, season)
                if stats_data:
                    batch_data.append(stats_data)
                    batch_count += 1
                
                # Process batch when it reaches batch_size
                if len(batch_data) >= self.batch_size:
                    await self._process_batch_recent(batch_data)
                    batch_data = []
                    
            except Exception as e:
                print(f"❌ Error processing {first_name} {last_name} {season}: {e}")
                self.stats_skipped += 1
        
        # Process remaining data in batch
        if batch_data:
            await self._process_batch_recent(batch_data)
    
    async def _process_batch_recent(self, batch_data: List[Dict]):
        """Process a batch of recent player stats"""
        try:
            created = await self.db.bulk_create_player_stats(batch_data)
            self.stats_created += created
            print(f"📦 Processed batch: {created} stats created")
        except Exception as e:
            print(f"❌ Error processing batch: {e}")
            # Fallback to individual inserts
            for stats in batch_data:
                try:
                    await self._insert_single_player_stats(stats)
                    self.stats_created += 1
                except Exception as e2:
                    print(f"❌ Error inserting individual stats: {e2}")
                    self.stats_skipped += 1
    
    async def _insert_single_player_stats(self, stats_data: Dict):
        """Insert a single player stats record"""
        try:
            query = """
            INSERT INTO player_stats (
                "playerId", season, "gamesPlayed", "minutesPerGame", "pointsPerGame",
                rebounds, assists, steals, blocks, turnovers,
                "fieldGoalPct", "threePointPct", "freeThrowPct", "createdAt", "updatedAt"
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
            ) ON CONFLICT ("playerId", season) DO UPDATE SET
                "gamesPlayed" = EXCLUDED."gamesPlayed",
                "minutesPerGame" = EXCLUDED."minutesPerGame",
                "pointsPerGame" = EXCLUDED."pointsPerGame",
                rebounds = EXCLUDED.rebounds,
                assists = EXCLUDED.assists,
                steals = EXCLUDED.steals,
                blocks = EXCLUDED.blocks,
                turnovers = EXCLUDED.turnovers,
                "fieldGoalPct" = EXCLUDED."fieldGoalPct",
                "threePointPct" = EXCLUDED."threePointPct",
                "freeThrowPct" = EXCLUDED."freeThrowPct",
                "updatedAt" = NOW()
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
            
            self.db.cursor.execute(query, values)
            await self.db.connection.commit()
            
        except Exception as e:
            print(f"❌ Error inserting player stats: {e}")
            await self.db.connection.rollback()
            raise
    
    def _calculate_player_stats_recent(self, group: pd.DataFrame, player_id: str, season: str) -> Dict:
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
    """Import recent player statistics"""
    print("🚀 Starting Recent Player Statistics Import (Last 5 Years)...")
    
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
        
        # Create recent importer
        importer = RecentPlayerStatsImporter(db_manager, team_mapping, player_mapping)
        
        # Import recent player stats (last 5 years)
        await importer.import_recent_player_stats("data/PlayerStatistics.csv", years_back=5)
        
    except Exception as e:
        print(f"❌ Error during recent player stats import: {e}")
        raise
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(main())

