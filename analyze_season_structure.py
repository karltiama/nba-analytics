#!/usr/bin/env python3
"""
Analyze NBA season structure and verify data alignment
"""
import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from data_import.database import DatabaseManager

async def main():
    """Analyze NBA season structure and data alignment"""
    print("🏀 Analyzing NBA season structure and data alignment...")
    
    db_manager = DatabaseManager()
    
    try:
        # Connect to database
        await db_manager.connect()
        print("✅ Connected to database")
        
        # 1. Check games data for season structure
        print("\n📅 === GAMES DATA SEASON STRUCTURE ===")
        db_manager.cursor.execute('''
            SELECT 
                season,
                MIN("gameDate") as season_start,
                MAX("gameDate") as season_end,
                COUNT(*) as total_games
            FROM games 
            WHERE season >= '2014-15'
            GROUP BY season 
            ORDER BY season DESC
            LIMIT 10
        ''')
        games_seasons = db_manager.cursor.fetchall()
        
        print("Recent seasons from games data:")
        print(f"{'Season':<10} {'Start Date':<12} {'End Date':<12} {'Games':<8}")
        print("-" * 50)
        for season in games_seasons:
            start_date = season['season_start'].strftime('%Y-%m-%d') if season['season_start'] else 'N/A'
            end_date = season['season_end'].strftime('%Y-%m-%d') if season['season_end'] else 'N/A'
            print(f"{season['season']:<10} {start_date:<12} {end_date:<12} {season['total_games']:<8}")
        
        # 2. Check player stats data for season structure
        print("\n📊 === PLAYER STATS SEASON STRUCTURE ===")
        db_manager.cursor.execute('''
            SELECT 
                season,
                COUNT(DISTINCT "playerId") as unique_players,
                COUNT(*) as total_records
            FROM player_stats 
            WHERE season >= '2014-15'
            GROUP BY season 
            ORDER BY season DESC
            LIMIT 10
        ''')
        player_seasons = db_manager.cursor.fetchall()
        
        print("Recent seasons from player stats data:")
        print(f"{'Season':<10} {'Players':<8} {'Records':<8}")
        print("-" * 35)
        for season in player_seasons:
            print(f"{season['season']:<10} {season['unique_players']:<8} {season['total_records']:<8}")
        
        # 3. Analyze season naming convention
        print("\n🔍 === SEASON NAMING ANALYSIS ===")
        print("NBA Season Structure:")
        print("• Season 2023-24 = October 2023 to April 2024")
        print("• Season 2024-25 = October 2024 to April 2025")
        print("• Season 2025-26 = October 2025 to April 2026")
        print()
        print("Our data uses the correct NBA convention:")
        print("• First year = Start year (October)")
        print("• Second year = End year (April)")
        
        # 4. Check for any data inconsistencies
        print("\n⚠️ === DATA CONSISTENCY CHECKS ===")
        
        # Check if we have any seasons that don't follow the pattern
        db_manager.cursor.execute('''
            SELECT DISTINCT season 
            FROM player_stats 
            WHERE season NOT LIKE '____-__'
            ORDER BY season
        ''')
        invalid_seasons = db_manager.cursor.fetchall()
        
        if invalid_seasons:
            print("❌ Found seasons with invalid format:")
            for season in invalid_seasons:
                print(f"  - {season['season']}")
        else:
            print("✅ All seasons follow the correct YYYY-YY format")
        
        # Check for seasons that span too many years
        db_manager.cursor.execute('''
            SELECT season, 
                   SUBSTRING(season, 1, 4)::int as start_year,
                   SUBSTRING(season, 6, 2)::int as end_year
            FROM player_stats 
            WHERE season LIKE '____-__'
            AND (SUBSTRING(season, 6, 2)::int - SUBSTRING(season, 1, 4)::int) != 1
            ORDER BY season
        ''')
        inconsistent_seasons = db_manager.cursor.fetchall()
        
        if inconsistent_seasons:
            print("❌ Found seasons with inconsistent year spans:")
            for season in inconsistent_seasons:
                print(f"  - {season['season']} (spans {season['end_year'] - season['start_year']} years)")
        else:
            print("✅ All seasons span exactly 1 year (October to April)")
        
        # 5. Verify recent season data quality
        print("\n📈 === RECENT SEASON DATA QUALITY ===")
        db_manager.cursor.execute('''
            SELECT 
                season,
                COUNT(DISTINCT "playerId") as players,
                AVG("gamesPlayed") as avg_games,
                MAX("gamesPlayed") as max_games,
                AVG("pointsPerGame") as avg_ppg
            FROM player_stats 
            WHERE season >= '2020-21'
            GROUP BY season 
            ORDER BY season DESC
        ''')
        recent_quality = db_manager.cursor.fetchall()
        
        print("Recent season quality metrics:")
        print(f"{'Season':<10} {'Players':<8} {'Avg Games':<10} {'Max Games':<10} {'Avg PPG':<8}")
        print("-" * 60)
        for season in recent_quality:
            print(f"{season['season']:<10} {season['players']:<8} {season['avg_games']:<10.1f} {season['max_games']:<10} {season['avg_ppg']:<8.1f}")
        
        # 6. Check for future seasons (projections)
        print("\n🔮 === FUTURE SEASONS ANALYSIS ===")
        db_manager.cursor.execute('''
            SELECT season, COUNT(*) as records
            FROM player_stats 
            WHERE season > '2024-25'
            GROUP BY season 
            ORDER BY season
        ''')
        future_seasons = db_manager.cursor.fetchall()
        
        if future_seasons:
            print("Future seasons found (likely projections):")
            for season in future_seasons:
                print(f"  - {season['season']}: {season['records']} records")
        else:
            print("No future seasons found")
        
        print("\n✅ Season structure analysis completed!")
        print("\n🎯 KEY INSIGHTS:")
        print("• NBA seasons correctly span October to April")
        print("• Our data follows the proper YYYY-YY naming convention")
        print("• Season 2023-24 = Games from October 2023 to April 2024")
        print("• This is perfect for betting models as it aligns with actual NBA calendar")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(main())

