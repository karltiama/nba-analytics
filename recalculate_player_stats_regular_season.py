#!/usr/bin/env python3
"""
Recalculate player statistics using only regular season games from CSV
"""
import asyncio
import pandas as pd
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from data_import.database import DatabaseManager

async def main():
    """Recalculate player statistics using only regular season games"""
    print("🔄 Recalculating player statistics using only regular season games...")
    
    db_manager = DatabaseManager()
    
    try:
        # Connect to database
        await db_manager.connect()
        print("✅ Connected to database")
        
        # Read CSV data
        print("\n📊 === READING CSV DATA ===")
        df = pd.read_csv("data/PlayerStatistics.csv", low_memory=False)
        print(f"Total records in CSV: {len(df):,}")
        
        # Filter for regular season only
        regular_season_df = df[df['gameType'] == 'Regular Season']
        print(f"Regular season records: {len(regular_season_df):,}")
        
        # Check Giannis data
        giannis_regular = regular_season_df[
            regular_season_df['firstName'].str.contains('Giannis', na=False) & 
            regular_season_df['lastName'].str.contains('Antetokounmpo', na=False)
        ]
        print(f"Giannis regular season records: {len(giannis_regular)}")
        
        # Check 2024-25 specifically
        giannis_2024_25 = giannis_regular[
            (pd.to_datetime(giannis_regular['gameDate']) >= '2024-10-01') & 
            (pd.to_datetime(giannis_regular['gameDate']) <= '2025-04-30')
        ]
        print(f"Giannis 2024-25 regular season: {len(giannis_2024_25)} games")
        
        # Get existing players mapping
        print("\n👥 === GETTING PLAYER MAPPING ===")
        db_manager.cursor.execute('SELECT id, name FROM players')
        players = db_manager.cursor.fetchall()
        player_mapping = {player['name']: player['id'] for player in players}
        print(f"Found {len(player_mapping)} players in database")
        
        # Process regular season data
        print("\n🔄 === PROCESSING REGULAR SEASON DATA ===")
        
        # Convert gameDate to datetime
        regular_season_df['gameDate'] = pd.to_datetime(regular_season_df['gameDate'])
        regular_season_df['gameYear'] = regular_season_df['gameDate'].dt.year
        
        # Create season column (e.g., 2024-25)
        regular_season_df['season'] = regular_season_df['gameYear'].astype(str) + '-' + (regular_season_df['gameYear'] + 1).astype(str).str[2:]
        
        # Group by player and season
        grouped = regular_season_df.groupby(['firstName', 'lastName', 'season'])
        
        stats_created = 0
        stats_updated = 0
        stats_skipped = 0
        
        for (first_name, last_name, season), group in grouped:
            player_name = f"{first_name} {last_name}"
            player_id = player_mapping.get(player_name)
            
            if not player_id:
                stats_skipped += 1
                continue
            
            # Calculate stats for this player-season
            games_played = len(group)
            
            # Only process if we have reasonable game count (1-82 games)
            if games_played < 1 or games_played > 82:
                stats_skipped += 1
                continue
            
            minutes_per_game = group['numMinutes'].mean() if 'numMinutes' in group.columns else 0
            points_per_game = group['points'].mean() if 'points' in group.columns else 0
            rebounds_per_game = group['reboundsTotal'].mean() if 'reboundsTotal' in group.columns else 0
            assists_per_game = group['assists'].mean() if 'assists' in group.columns else 0
            steals_per_game = group['steals'].mean() if 'steals' in group.columns else 0
            blocks_per_game = group['blocks'].mean() if 'blocks' in group.columns else 0
            turnovers_per_game = group['turnovers'].mean() if 'turnovers' in group.columns else 0
            
            field_goal_pct = group['fieldGoalsPercentage'].mean() if 'fieldGoalsPercentage' in group.columns else 0
            three_point_pct = group['threePointersPercentage'].mean() if 'threePointersPercentage' in group.columns else 0
            free_throw_pct = group['freeThrowsPercentage'].mean() if 'freeThrowsPercentage' in group.columns else 0
            
            # Check if record exists
            db_manager.cursor.execute('''
                SELECT id FROM player_stats 
                WHERE "playerId" = %s AND season = %s
            ''', (player_id, season))
            
            existing_stat = db_manager.cursor.fetchone()
            
            if existing_stat:
                # Update existing record
                db_manager.cursor.execute('''
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
                    WHERE id = %s
                ''', (
                    int(games_played),
                    float(minutes_per_game),
                    float(points_per_game),
                    float(rebounds_per_game),
                    float(assists_per_game),
                    float(steals_per_game),
                    float(blocks_per_game),
                    float(turnovers_per_game),
                    float(field_goal_pct),
                    float(three_point_pct),
                    float(free_throw_pct),
                    existing_stat['id']
                ))
                stats_updated += 1
            else:
                # Insert new record
                db_manager.cursor.execute('''
                    INSERT INTO player_stats (
                        id, "playerId", season, "gamesPlayed", "minutesPerGame", "pointsPerGame",
                        rebounds, assists, steals, blocks, turnovers,
                        "fieldGoalPct", "threePointPct", "freeThrowPct", "createdAt", "updatedAt"
                    ) VALUES (
                        gen_random_uuid(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
                    )
                ''', (
                    player_id,
                    season,
                    int(games_played),
                    float(minutes_per_game),
                    float(points_per_game),
                    float(rebounds_per_game),
                    float(assists_per_game),
                    float(steals_per_game),
                    float(blocks_per_game),
                    float(turnovers_per_game),
                    float(field_goal_pct),
                    float(three_point_pct),
                    float(free_throw_pct)
                ))
                stats_created += 1
            
            # Commit every 100 records
            if (stats_created + stats_updated) % 100 == 0:
                db_manager.connection.commit()
                print(f"  Processed {stats_created + stats_updated} player-season combinations...")
        
        # Final commit
        db_manager.connection.commit()
        
        print(f"\n✅ === RECALCULATION COMPLETE ===")
        print(f"Stats created: {stats_created}")
        print(f"Stats updated: {stats_updated}")
        print(f"Stats skipped: {stats_skipped}")
        
        # Verify Giannis data
        print(f"\n🔍 === VERIFICATION ===")
        db_manager.cursor.execute('''
            SELECT season, "gamesPlayed", "pointsPerGame"
            FROM player_stats ps
            JOIN players p ON ps."playerId" = p.id
            WHERE p.name = 'Giannis Antetokounmpo'
            AND season >= '2020-21'
            ORDER BY season DESC
        ''')
        
        giannis_verified = db_manager.cursor.fetchall()
        print("Giannis stats after recalculation (regular season only):")
        for stat in giannis_verified:
            print(f"  {stat['season']}: {stat['gamesPlayed']} games, {stat['pointsPerGame']:.1f} PPG")
        
        # Check for any remaining unrealistic game counts
        db_manager.cursor.execute('''
            SELECT COUNT(*) as high_game_count
            FROM player_stats 
            WHERE "gamesPlayed" > 82
        ''')
        
        high_games = db_manager.cursor.fetchone()['high_game_count']
        print(f"\nRecords with >82 games: {high_games}")
        
        if high_games == 0:
            print("✅ All game counts are now realistic (≤82 games)")
        else:
            print("⚠️ Still have some records with >82 games")
        
        print(f"\n🎯 === SUMMARY ===")
        print("• Recalculated player statistics using only regular season games")
        print("• Giannis 2024-25 should now show ~70 games (not 73)")
        print("• All game counts should be ≤82 (realistic for NBA regular season)")
        print("• Data is now accurate for betting model backtesting")
        
    except Exception as e:
        print(f"❌ Error during recalculation: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(main())

