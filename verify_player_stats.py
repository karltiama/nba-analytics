#!/usr/bin/env python3
"""
Verify imported player statistics data
"""
import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from data_import.database import DatabaseManager

async def main():
    """Verify player statistics data"""
    print("🔍 Verifying imported player statistics data...")
    
    db_manager = DatabaseManager()
    
    try:
        # Connect to database
        await db_manager.connect()
        
        # 1. Check total counts
        print("\n📊 === DATA COUNTS ===")
        db_manager.cursor.execute('SELECT COUNT(*) FROM player_stats')
        total_count = db_manager.cursor.fetchone()[0]
        print(f"Total player stats records: {total_count:,}")
        
        # 2. Check seasons available
        print("\n📅 === SEASONS AVAILABLE ===")
        db_manager.cursor.execute('SELECT DISTINCT season FROM player_stats ORDER BY season')
        seasons = db_manager.cursor.fetchall()
        print(f"Seasons: {[s[0] for s in seasons]}")
        
        # 3. Check records per season
        print("\n📈 === RECORDS PER SEASON ===")
        db_manager.cursor.execute('''
            SELECT season, COUNT(*) as record_count 
            FROM player_stats 
            GROUP BY season 
            ORDER BY season
        ''')
        season_counts = db_manager.cursor.fetchall()
        for season, count in season_counts:
            print(f"  {season}: {count:,} records")
        
        # 4. Check top scorers by season (last 3 seasons)
        print("\n🏀 === TOP SCORERS (Last 3 Seasons) ===")
        recent_seasons = [s[0] for s in seasons[-3:]]
        for season in recent_seasons:
            print(f"\n{season} Season:")
            db_manager.cursor.execute('''
                SELECT ps."playerId", p.name, ps."gamesPlayed", ps."pointsPerGame", ps."rebounds", ps."assists"
                FROM player_stats ps
                JOIN players p ON ps."playerId" = p.id
                WHERE ps.season = %s
                ORDER BY ps."pointsPerGame" DESC
                LIMIT 5
            ''', (season,))
            
            top_scorers = db_manager.cursor.fetchall()
            for i, scorer in enumerate(top_scorers, 1):
                player_id, name, games, ppg, reb, ast = scorer
                print(f"  {i}. {name}: {games} games, {ppg:.1f} PPG, {reb:.1f} REB, {ast:.1f} AST")
        
        # 5. Check data quality - look for any null or invalid values
        print("\n🔍 === DATA QUALITY CHECKS ===")
        
        # Check for null values in key fields
        db_manager.cursor.execute('''
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN "pointsPerGame" IS NULL THEN 1 END) as null_ppg,
                COUNT(CASE WHEN "gamesPlayed" = 0 THEN 1 END) as zero_games,
                COUNT(CASE WHEN "pointsPerGame" < 0 THEN 1 END) as negative_ppg
            FROM player_stats
        ''')
        quality_check = db_manager.cursor.fetchone()
        total, null_ppg, zero_games, negative_ppg = quality_check
        print(f"Total records: {total:,}")
        print(f"Records with null PPG: {null_ppg:,}")
        print(f"Records with 0 games: {zero_games:,}")
        print(f"Records with negative PPG: {negative_ppg:,}")
        
        # 6. Check statistical ranges
        print("\n📊 === STATISTICAL RANGES ===")
        db_manager.cursor.execute('''
            SELECT 
                MIN("pointsPerGame") as min_ppg,
                MAX("pointsPerGame") as max_ppg,
                AVG("pointsPerGame") as avg_ppg,
                MIN("gamesPlayed") as min_games,
                MAX("gamesPlayed") as max_games,
                AVG("gamesPlayed") as avg_games
            FROM player_stats
        ''')
        stats = db_manager.cursor.fetchone()
        min_ppg, max_ppg, avg_ppg, min_games, max_games, avg_games = stats
        print(f"Points per game: {min_ppg:.1f} - {max_ppg:.1f} (avg: {avg_ppg:.1f})")
        print(f"Games played: {min_games} - {max_games} (avg: {avg_games:.1f})")
        
        # 7. Check for duplicate player-season combinations
        print("\n🔍 === DUPLICATE CHECK ===")
        db_manager.cursor.execute('''
            SELECT "playerId", season, COUNT(*) as count
            FROM player_stats
            GROUP BY "playerId", season
            HAVING COUNT(*) > 1
            LIMIT 5
        ''')
        duplicates = db_manager.cursor.fetchall()
        if duplicates:
            print(f"Found {len(duplicates)} duplicate player-season combinations:")
            for dup in duplicates:
                print(f"  Player {dup[0][:8]}... in {dup[1]}: {dup[2]} records")
        else:
            print("✅ No duplicate player-season combinations found")
        
        # 8. Sample recent records
        print("\n📋 === SAMPLE RECENT RECORDS ===")
        db_manager.cursor.execute('''
            SELECT ps."playerId", p.name, ps.season, ps."gamesPlayed", ps."pointsPerGame", 
                   ps."rebounds", ps."assists", ps."steals", ps."blocks"
            FROM player_stats ps
            JOIN players p ON ps."playerId" = p.id
            WHERE ps.season = %s
            ORDER BY ps."pointsPerGame" DESC
            LIMIT 10
        ''', (recent_seasons[-1],))
        
        sample_records = db_manager.cursor.fetchall()
        print(f"Top 10 players from {recent_seasons[-1]}:")
        print(f"{'Rank':<4} {'Player':<25} {'Games':<6} {'PPG':<6} {'REB':<6} {'AST':<6} {'STL':<6} {'BLK':<6}")
        print("-" * 80)
        for i, record in enumerate(sample_records, 1):
            player_id, name, season, games, ppg, reb, ast, stl, blk = record
            print(f"{i:<4} {name[:24]:<25} {games:<6} {ppg:<6.1f} {reb:<6.1f} {ast:<6.1f} {stl:<6.1f} {blk:<6.1f}")
        
        print("\n✅ Data verification completed!")
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(main())

