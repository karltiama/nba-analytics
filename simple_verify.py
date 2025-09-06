#!/usr/bin/env python3
"""
Simple verification of imported player statistics data
"""
import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from data_import.database import DatabaseManager

async def main():
    """Simple verification of player statistics data"""
    print("🔍 Simple verification of player statistics data...")
    
    db_manager = DatabaseManager()
    
    try:
        # Connect to database
        await db_manager.connect()
        print("✅ Connected to database")
        
        # Check total counts
        print("\n📊 Checking total counts...")
        db_manager.cursor.execute('SELECT COUNT(*) FROM player_stats')
        result = db_manager.cursor.fetchone()
        if result:
            total_count = result['count']
            print(f"Total player stats records: {total_count:,}")
        else:
            print("❌ No result returned from count query")
        
        # Check seasons
        print("\n📅 Checking seasons...")
        db_manager.cursor.execute('SELECT DISTINCT season FROM player_stats ORDER BY season')
        seasons = db_manager.cursor.fetchall()
        if seasons:
            print(f"Seasons found: {[s['season'] for s in seasons]}")
        else:
            print("❌ No seasons found")
        
        # Check a few sample records
        print("\n📋 Sample records...")
        db_manager.cursor.execute('''
            SELECT "playerId", season, "gamesPlayed", "pointsPerGame", "rebounds", "assists"
            FROM player_stats 
            ORDER BY "pointsPerGame" DESC 
            LIMIT 5
        ''')
        samples = db_manager.cursor.fetchall()
        if samples:
            print("Top 5 scorers:")
            for i, sample in enumerate(samples, 1):
                player_id = sample['playerId']
                season = sample['season']
                games = sample['gamesPlayed']
                ppg = sample['pointsPerGame']
                reb = sample['rebounds']
                ast = sample['assists']
                print(f"  {i}. Player {player_id[:8]}... ({season}): {games} games, {ppg:.1f} PPG, {reb:.1f} REB, {ast:.1f} AST")
        else:
            print("❌ No sample records found")
        
        print("\n✅ Simple verification completed!")
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
