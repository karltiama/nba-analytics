#!/usr/bin/env python3
"""
Check player statistics data
"""
import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from data_import.database import DatabaseManager

async def main():
    """Check player statistics data"""
    print("🔍 Checking player statistics data...")
    
    db_manager = DatabaseManager()
    
    try:
        # Connect to database
        await db_manager.connect()
        
        # Check total player stats count
        db_manager.cursor.execute('SELECT COUNT(*) FROM player_stats')
        total_count = db_manager.cursor.fetchone()[0]
        print(f"📊 Total player stats records: {total_count}")
        
        # Check 2023-24 season specifically
        db_manager.cursor.execute('SELECT COUNT(*) FROM player_stats WHERE season = %s', ('2023-24',))
        season_count = db_manager.cursor.fetchone()[0]
        print(f"📊 2023-24 season records: {season_count}")
        
        # Show a few sample records
        db_manager.cursor.execute('''
            SELECT "playerId", season, "gamesPlayed", "pointsPerGame" 
            FROM player_stats 
            WHERE season = %s 
            ORDER BY "pointsPerGame" DESC 
            LIMIT 5
        ''', ('2023-24',))
        
        samples = db_manager.cursor.fetchall()
        print("\n🏀 Top 5 scorers from 2023-24:")
        for sample in samples:
            print(f"  Player {sample[0][:8]}...: {sample[2]} games, {sample[3]:.1f} PPG")
        
        # Check seasons available
        db_manager.cursor.execute('SELECT DISTINCT season FROM player_stats ORDER BY season')
        seasons = db_manager.cursor.fetchall()
        print(f"\n📅 Available seasons: {[s[0] for s in seasons]}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(main())

