#!/usr/bin/env python3
"""
Investigate Giannis Antetokounmpo's data accuracy
"""
import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from data_import.database import DatabaseManager

async def main():
    """Investigate Giannis Antetokounmpo's data accuracy"""
    print("🔍 Investigating Giannis Antetokounmpo's data accuracy...")
    
    db_manager = DatabaseManager()
    
    try:
        # Connect to database
        await db_manager.connect()
        print("✅ Connected to database")
        
        # 1. Find Giannis in our database
        print("\n👤 === FINDING GIANNIS ANTETOKOUNMPO ===")
        db_manager.cursor.execute('''
            SELECT id, name
            FROM players 
            WHERE LOWER(name) LIKE '%giannis%' OR LOWER(name) LIKE '%antetokounmpo%'
        ''')
        giannis_players = db_manager.cursor.fetchall()
        
        if not giannis_players:
            print("❌ Giannis Antetokounmpo not found in players table")
            return
        
        print("Found Giannis records:")
        for player in giannis_players:
            print(f"  ID: {player['id']}, Name: {player['name']}")
        
        giannis_id = giannis_players[0]['id']
        print(f"\nUsing Giannis ID: {giannis_id}")
        
        # 2. Check his player stats records
        print("\n📊 === GIANNIS PLAYER STATS RECORDS ===")
        db_manager.cursor.execute('''
            SELECT season, "gamesPlayed", "pointsPerGame", "rebounds", "assists", "steals", "blocks"
            FROM player_stats 
            WHERE "playerId" = %s
            ORDER BY season DESC
        ''', (giannis_id,))
        
        giannis_stats = db_manager.cursor.fetchall()
        
        if not giannis_stats:
            print("❌ No player stats found for Giannis")
            return
        
        print("Giannis player stats by season:")
        print(f"{'Season':<10} {'Games':<6} {'PPG':<6} {'REB':<6} {'AST':<6} {'STL':<6} {'BLK':<6}")
        print("-" * 60)
        for stat in giannis_stats:
            print(f"{stat['season']:<10} {stat['gamesPlayed']:<6} {stat['pointsPerGame']:<6.1f} {stat['rebounds']:<6.1f} {stat['assists']:<6.1f} {stat['steals']:<6.1f} {stat['blocks']:<6.1f}")
        
        # 3. Check his individual game records
        print("\n🎮 === GIANNIS INDIVIDUAL GAME RECORDS ===")
        db_manager.cursor.execute('''
            SELECT g.season, COUNT(*) as game_count, 
                   MIN(g."gameDate") as first_game, 
                   MAX(g."gameDate") as last_game
            FROM games g
            JOIN player_stats ps ON g.season = ps.season
            WHERE ps."playerId" = %s
            GROUP BY g.season
            ORDER BY g.season DESC
        ''', (giannis_id,))
        
        game_records = db_manager.cursor.fetchall()
        
        if game_records:
            print("Games by season (from games table):")
            print(f"{'Season':<10} {'Count':<6} {'First Game':<12} {'Last Game':<12}")
            print("-" * 50)
            for record in game_records:
                first_game = record['first_game'].strftime('%Y-%m-%d') if record['first_game'] else 'N/A'
                last_game = record['last_game'].strftime('%Y-%m-%d') if record['last_game'] else 'N/A'
                print(f"{record['season']:<10} {record['game_count']:<6} {first_game:<12} {last_game:<12}")
        
        # 4. Check specific recent seasons
        print("\n🔍 === DETAILED ANALYSIS FOR RECENT SEASONS ===")
        recent_seasons = ['2023-24', '2022-23', '2021-22']
        
        for season in recent_seasons:
            print(f"\n{season} Season Analysis:")
            
            # Get player stats for this season
            db_manager.cursor.execute('''
                SELECT "gamesPlayed", "pointsPerGame", "rebounds", "assists"
                FROM player_stats 
                WHERE "playerId" = %s AND season = %s
            ''', (giannis_id, season))
            
            season_stat = db_manager.cursor.fetchone()
            if season_stat:
                print(f"  Player Stats: {season_stat['gamesPlayed']} games, {season_stat['pointsPerGame']:.1f} PPG")
                
                # Count actual games from games table
                db_manager.cursor.execute('''
                    SELECT COUNT(*) as actual_games
                    FROM games g
                    WHERE g.season = %s
                    AND (g."homeTeamId" = (SELECT "teamId" FROM players WHERE id = %s) 
                         OR g."awayTeamId" = (SELECT "teamId" FROM players WHERE id = %s))
                ''', (season, giannis_id, giannis_id))
                
                actual_games = db_manager.cursor.fetchone()
                if actual_games:
                    print(f"  Actual Games: {actual_games['actual_games']} games")
                    print(f"  Difference: {season_stat['gamesPlayed'] - actual_games['actual_games']} games")
        
        # 5. Check if there are any data quality issues
        print("\n⚠️ === DATA QUALITY CHECKS ===")
        
        # Check for duplicate records
        db_manager.cursor.execute('''
            SELECT season, COUNT(*) as record_count
            FROM player_stats 
            WHERE "playerId" = %s
            GROUP BY season
            HAVING COUNT(*) > 1
        ''', (giannis_id,))
        
        duplicates = db_manager.cursor.fetchall()
        if duplicates:
            print("❌ Found duplicate records:")
            for dup in duplicates:
                print(f"  {dup['season']}: {dup['record_count']} records")
        else:
            print("✅ No duplicate records found")
        
        # Check for unrealistic game counts
        db_manager.cursor.execute('''
            SELECT season, "gamesPlayed"
            FROM player_stats 
            WHERE "playerId" = %s AND "gamesPlayed" > 82
        ''', (giannis_id,))
        
        high_games = db_manager.cursor.fetchall()
        if high_games:
            print("⚠️ Found seasons with >82 games (unrealistic for regular season):")
            for record in high_games:
                print(f"  {record['season']}: {record['gamesPlayed']} games")
        else:
            print("✅ All game counts are realistic (≤82 games)")
        
        print("\n✅ Giannis data investigation completed!")
        
    except Exception as e:
        print(f"❌ Error during investigation: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
