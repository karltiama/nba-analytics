#!/usr/bin/env python3
"""
Check what years of game data we have in the database
"""
import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from data_import.database import DatabaseManager

async def check_game_years():
    """Check what years of game data we have"""
    print("📅 Checking game data years...")
    
    db_manager = DatabaseManager()
    
    try:
        # Connect to database
        await db_manager.connect()
        
        # Query to get year distribution
        query = """
        SELECT 
            EXTRACT(YEAR FROM "gameDate") as year,
            COUNT(*) as game_count,
            MIN("gameDate") as earliest_game,
            MAX("gameDate") as latest_game
        FROM games 
        WHERE "gameDate" IS NOT NULL
        GROUP BY EXTRACT(YEAR FROM "gameDate")
        ORDER BY year
        """
        
        db_manager.cursor.execute(query)
        results = db_manager.cursor.fetchall()
        
        print(f"📊 Game data by year:")
        print(f"{'Year':<6} {'Games':<8} {'Earliest':<12} {'Latest':<12}")
        print("-" * 50)
        
        total_games = 0
        for row in results:
            year = int(row['year']) if row['year'] else 'Unknown'
            count = row['game_count']
            earliest = row['earliest_game'].strftime('%Y-%m-%d') if row['earliest_game'] else 'N/A'
            latest = row['latest_game'].strftime('%Y-%m-%d') if row['latest_game'] else 'N/A'
            
            print(f"{year:<6} {count:<8} {earliest:<12} {latest:<12}")
            total_games += count
        
        print("-" * 50)
        print(f"Total games: {total_games}")
        
        # Get some sample games
        print(f"\n📋 Sample games:")
        sample_query = """
        SELECT "gameDate", season, "homeTeamId", "awayTeamId", "homeScore", "awayScore"
        FROM games 
        ORDER BY "gameDate" DESC
        LIMIT 5
        """
        
        db_manager.cursor.execute(sample_query)
        sample_results = db_manager.cursor.fetchall()
        
        for game in sample_results:
            print(f"  {game['gameDate']} | Season: {game['season']} | Score: {game['homeScore']}-{game['awayScore']}")
        
    except Exception as e:
        print(f"❌ Error checking game years: {e}")
        raise
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(check_game_years())

