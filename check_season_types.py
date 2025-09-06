#!/usr/bin/env python3
"""
Check season types in games table
"""
import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from data_import.database import DatabaseManager

async def main():
    """Check season types in games table"""
    print("🔍 Checking season types in games table...")
    
    db_manager = DatabaseManager()
    
    try:
        # Connect to database
        await db_manager.connect()
        print("✅ Connected to database")
        
        # Check season types
        print("\n📊 === SEASON TYPES IN GAMES TABLE ===")
        db_manager.cursor.execute('''
            SELECT "seasonType", COUNT(*) as game_count
            FROM games 
            GROUP BY "seasonType"
            ORDER BY "seasonType"
        ''')
        
        season_types = db_manager.cursor.fetchall()
        print("Season types and game counts:")
        for st in season_types:
            print(f"  {st['seasonType']}: {st['game_count']:,} games")
        
        # Check 2024-25 season specifically
        print("\n📅 === 2024-25 SEASON BREAKDOWN ===")
        db_manager.cursor.execute('''
            SELECT "seasonType", COUNT(*) as game_count
            FROM games 
            WHERE season = '2024-25'
            GROUP BY "seasonType"
            ORDER BY "seasonType"
        ''')
        
        season_breakdown = db_manager.cursor.fetchall()
        print("2024-25 season breakdown:")
        for sb in season_breakdown:
            print(f"  {sb['seasonType']}: {sb['game_count']:,} games")
        
        # Check recent seasons
        print("\n📈 === RECENT SEASONS BREAKDOWN ===")
        db_manager.cursor.execute('''
            SELECT season, "seasonType", COUNT(*) as game_count
            FROM games 
            WHERE season >= '2020-21'
            GROUP BY season, "seasonType"
            ORDER BY season DESC, "seasonType"
        ''')
        
        recent_breakdown = db_manager.cursor.fetchall()
        print("Recent seasons breakdown:")
        current_season = None
        for rb in recent_breakdown:
            if rb['season'] != current_season:
                print(f"\n{rb['season']}:")
                current_season = rb['season']
            print(f"  {rb['seasonType']}: {rb['game_count']:,} games")
        
        # Check if our player stats calculation is including playoffs
        print("\n🔍 === PLAYER STATS CALCULATION ISSUE ===")
        print("The problem is likely that our player stats calculation includes BOTH regular season AND playoff games")
        print("But NBA regular season is only 82 games per team, so we should only count regular season games")
        
        # Check Giannis's team and count only regular season games
        db_manager.cursor.execute('''
            SELECT "teamId" FROM players WHERE name = 'Giannis Antetokounmpo'
        ''')
        giannis_team = db_manager.cursor.fetchone()
        
        if giannis_team and giannis_team['teamId']:
            team_id = giannis_team['teamId']
            print(f"\nGiannis's Team ID: {team_id}")
            
            # Get team name
            db_manager.cursor.execute('''
                SELECT name FROM teams WHERE id = %s
            ''', (team_id,))
            team_name = db_manager.cursor.fetchone()
            if team_name:
                print(f"Team Name: {team_name['name']}")
            
            # Count only regular season games for 2024-25
            db_manager.cursor.execute('''
                SELECT COUNT(*) as regular_season_games
                FROM games 
                WHERE season = '2024-25' 
                AND "seasonType" = 'Regular Season'
                AND ("homeTeamId" = %s OR "awayTeamId" = %s)
            ''', (team_id, team_id))
            
            regular_games = db_manager.cursor.fetchone()
            print(f"Regular season games for Giannis's team in 2024-25: {regular_games['regular_season_games']}")
            
            # Count playoff games
            db_manager.cursor.execute('''
                SELECT COUNT(*) as playoff_games
                FROM games 
                WHERE season = '2024-25' 
                AND "seasonType" = 'Playoffs'
                AND ("homeTeamId" = %s OR "awayTeamId" = %s)
            ''', (team_id, team_id))
            
            playoff_games = db_manager.cursor.fetchone()
            print(f"Playoff games for Giannis's team in 2024-25: {playoff_games['playoff_games']}")
            
            total_games = regular_games['regular_season_games'] + playoff_games['playoff_games']
            print(f"Total games (regular + playoffs): {total_games}")
            
            if total_games > 0:
                print(f"Giannis's 73 games in player_stats likely includes both regular season ({regular_games['regular_season_games']}) and playoff games")
        
        print("\n✅ Season types investigation completed!")
        print("\n🎯 SOLUTION:")
        print("• We need to modify our player stats calculation to only count 'Regular Season' games")
        print("• This will give us accurate regular season statistics for betting models")
        print("• Playoff games should be tracked separately if needed")
        
    except Exception as e:
        print(f"❌ Error during investigation: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(main())

