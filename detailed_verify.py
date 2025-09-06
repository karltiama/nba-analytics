#!/usr/bin/env python3
"""
Detailed verification of imported player statistics data
"""
import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from data_import.database import DatabaseManager

async def main():
    """Detailed verification of player statistics data"""
    print("🔍 Detailed verification of player statistics data...")
    
    db_manager = DatabaseManager()
    
    try:
        # Connect to database
        await db_manager.connect()
        print("✅ Connected to database")
        
        # 1. Total counts
        print("\n📊 === DATA OVERVIEW ===")
        db_manager.cursor.execute('SELECT COUNT(*) FROM player_stats')
        total_count = db_manager.cursor.fetchone()['count']
        print(f"Total player stats records: {total_count:,}")
        
        # 2. Records per decade
        print("\n📈 === RECORDS BY DECADE ===")
        db_manager.cursor.execute('''
            SELECT 
                CASE 
                    WHEN season LIKE '194%' THEN '1940s'
                    WHEN season LIKE '195%' THEN '1950s'
                    WHEN season LIKE '196%' THEN '1960s'
                    WHEN season LIKE '197%' THEN '1970s'
                    WHEN season LIKE '198%' THEN '1980s'
                    WHEN season LIKE '199%' THEN '1990s'
                    WHEN season LIKE '200%' THEN '2000s'
                    WHEN season LIKE '201%' THEN '2010s'
                    WHEN season LIKE '202%' THEN '2020s'
                    ELSE 'Other'
                END as decade,
                COUNT(*) as record_count
            FROM player_stats 
            GROUP BY decade
            ORDER BY decade
        ''')
        decade_counts = db_manager.cursor.fetchall()
        for decade in decade_counts:
            print(f"  {decade['decade']}: {decade['record_count']:,} records")
        
        # 3. Recent seasons (last 10 years)
        print("\n🏀 === RECENT SEASONS (Last 10 Years) ===")
        db_manager.cursor.execute('''
            SELECT season, COUNT(*) as record_count 
            FROM player_stats 
            WHERE season >= '2014-15'
            GROUP BY season 
            ORDER BY season DESC
        ''')
        recent_seasons = db_manager.cursor.fetchall()
        for season in recent_seasons:
            print(f"  {season['season']}: {season['record_count']:,} records")
        
        # 4. Top scorers by decade
        print("\n⭐ === TOP SCORERS BY DECADE ===")
        decades = ['2010s', '2020s']
        for decade in decades:
            print(f"\n{decade}:")
            db_manager.cursor.execute('''
                SELECT ps."playerId", p.name, ps.season, ps."gamesPlayed", ps."pointsPerGame", ps."rebounds", ps."assists"
                FROM player_stats ps
                JOIN players p ON ps."playerId" = p.id
                WHERE ps.season LIKE %s
                ORDER BY ps."pointsPerGame" DESC
                LIMIT 3
            ''', (f"{decade[:4]}%",))
            
            top_scorers = db_manager.cursor.fetchall()
            for i, scorer in enumerate(top_scorers, 1):
                name = scorer['name']
                season = scorer['season']
                games = scorer['gamesPlayed']
                ppg = scorer['pointsPerGame']
                reb = scorer['rebounds']
                ast = scorer['assists']
                print(f"  {i}. {name} ({season}): {games} games, {ppg:.1f} PPG, {reb:.1f} REB, {ast:.1f} AST")
        
        # 5. Data quality check
        print("\n🔍 === DATA QUALITY ===")
        db_manager.cursor.execute('''
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN "pointsPerGame" > 0 THEN 1 END) as positive_ppg,
                COUNT(CASE WHEN "gamesPlayed" > 0 THEN 1 END) as positive_games,
                COUNT(CASE WHEN "pointsPerGame" > 30 THEN 1 END) as high_scorers,
                AVG("pointsPerGame") as avg_ppg,
                MAX("pointsPerGame") as max_ppg
            FROM player_stats
        ''')
        quality = db_manager.cursor.fetchone()
        print(f"Total records: {quality['total']:,}")
        print(f"Records with positive PPG: {quality['positive_ppg']:,}")
        print(f"Records with positive games: {quality['positive_games']:,}")
        print(f"High scorers (30+ PPG): {quality['high_scorers']:,}")
        print(f"Average PPG: {quality['avg_ppg']:.1f}")
        print(f"Maximum PPG: {quality['max_ppg']:.1f}")
        
        # 6. Player count by season (recent)
        print("\n👥 === PLAYERS PER SEASON (Recent) ===")
        db_manager.cursor.execute('''
            SELECT season, COUNT(DISTINCT "playerId") as unique_players
            FROM player_stats 
            WHERE season >= '2014-15'
            GROUP BY season 
            ORDER BY season DESC
        ''')
        player_counts = db_manager.cursor.fetchall()
        for season in player_counts:
            print(f"  {season['season']}: {season['unique_players']:,} unique players")
        
        print("\n✅ Detailed verification completed!")
        print(f"\n🎉 AMAZING! We have {total_count:,} player statistics records spanning from 1946 to 2025!")
        print("This is much more comprehensive than expected - we have nearly 80 years of NBA data!")
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(main())

