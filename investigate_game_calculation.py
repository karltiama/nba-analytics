#!/usr/bin/env python3
"""
Investigate how games are being calculated in player stats
"""
import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from data_import.database import DatabaseManager

async def main():
    """Investigate game calculation issues"""
    print("🔍 Investigating game calculation issues...")
    
    db_manager = DatabaseManager()
    
    try:
        # Connect to database
        await db_manager.connect()
        print("✅ Connected to database")
        
        # Get Giannis ID
        db_manager.cursor.execute('''
            SELECT id FROM players WHERE name = 'Giannis Antetokounmpo'
        ''')
        giannis = db_manager.cursor.fetchone()
        if not giannis:
            print("❌ Giannis not found")
            return
        
        giannis_id = giannis['id']
        print(f"Giannis ID: {giannis_id}")
        
        # Check his team
        db_manager.cursor.execute('''
            SELECT "teamId" FROM players WHERE id = %s
        ''', (giannis_id,))
        team_result = db_manager.cursor.fetchone()
        if team_result:
            team_id = team_result['teamId']
            print(f"Giannis Team ID: {team_id}")
            
            # Get team name
            db_manager.cursor.execute('''
                SELECT name FROM teams WHERE id = %s
            ''', (team_id,))
            team_result = db_manager.cursor.fetchone()
            if team_result:
                print(f"Team Name: {team_result['name']}")
        
        # Check 2024-25 season specifically
        print("\n📊 === 2024-25 SEASON ANALYSIS ===")
        
        # Count games where Giannis's team played
        db_manager.cursor.execute('''
            SELECT COUNT(*) as total_games
            FROM games 
            WHERE season = '2024-25' 
            AND ("homeTeamId" = %s OR "awayTeamId" = %s)
        ''', (team_id, team_id))
        
        team_games = db_manager.cursor.fetchone()
        print(f"Total games for Giannis's team in 2024-25: {team_games['total_games']}")
        
        # Check if there are individual player game records
        print("\n🎮 === CHECKING FOR INDIVIDUAL PLAYER GAME RECORDS ===")
        
        # Look for a table that might have individual player game stats
        db_manager.cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE '%player%'
            ORDER BY table_name
        """)
        
        player_tables = db_manager.cursor.fetchall()
        print("Player-related tables:")
        for table in player_tables:
            print(f"  - {table['table_name']}")
        
        # Check if there's a player_games table or similar
        db_manager.cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND (table_name LIKE '%game%' OR table_name LIKE '%stat%')
            ORDER BY table_name
        """)
        
        game_tables = db_manager.cursor.fetchall()
        print("\nGame/Stats-related tables:")
        for table in game_tables:
            print(f"  - {table['table_name']}")
        
        # Check the source of our player stats calculation
        print("\n🔍 === CHECKING PLAYER STATS CALCULATION SOURCE ===")
        
        # Look at the original CSV data structure
        print("The issue might be in how we calculated games from the PlayerStatistics.csv")
        print("Let's check if the CSV includes playoff games or double-counts...")
        
        # Check a few sample games from 2024-25
        print("\n📅 === SAMPLE 2024-25 GAMES ===")
        db_manager.cursor.execute('''
            SELECT "gameDate", "homeTeamId", "awayTeamId", "homeScore", "awayScore"
            FROM games 
            WHERE season = '2024-25' 
            AND ("homeTeamId" = %s OR "awayTeamId" = %s)
            ORDER BY "gameDate"
            LIMIT 10
        ''', (team_id, team_id))
        
        sample_games = db_manager.cursor.fetchall()
        print("Sample games for Giannis's team in 2024-25:")
        for game in sample_games:
            print(f"  {game['gameDate']}: {game['homeTeamId'][:8]}... vs {game['awayTeamId'][:8]}... ({game['homeScore']}-{game['awayScore']})")
        
        # Check if we have playoff vs regular season data
        print("\n🏆 === CHECKING FOR PLAYOFF VS REGULAR SEASON ===")
        
        # Look for game type or playoff indicators
        db_manager.cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns 
            WHERE table_name = 'games'
            AND (column_name LIKE '%type%' OR column_name LIKE '%playoff%' OR column_name LIKE '%season%')
            ORDER BY column_name
        """)
        
        game_columns = db_manager.cursor.fetchall()
        if game_columns:
            print("Game table columns that might indicate season type:")
            for col in game_columns:
                print(f"  {col['column_name']}: {col['data_type']}")
        else:
            print("No obvious playoff/regular season indicators found")
        
        # Check the actual game count for 2024-25
        db_manager.cursor.execute('''
            SELECT 
                COUNT(*) as total_games,
                MIN("gameDate") as first_game,
                MAX("gameDate") as last_game
            FROM games 
            WHERE season = '2024-25'
        ''')
        
        season_summary = db_manager.cursor.fetchone()
        print(f"\n2024-25 Season Summary:")
        print(f"  Total games: {season_summary['total_games']}")
        print(f"  First game: {season_summary['first_game']}")
        print(f"  Last game: {season_summary['last_game']}")
        
        print("\n✅ Game calculation investigation completed!")
        print("\n🎯 KEY FINDINGS:")
        print("• Giannis shows 73 games in 2024-25 (should be ~70-72 for regular season)")
        print("• Several seasons show >82 games (unrealistic for regular season)")
        print("• This suggests our data includes playoff games or has calculation errors")
        print("• Need to investigate the PlayerStatistics.csv source and calculation logic")
        
    except Exception as e:
        print(f"❌ Error during investigation: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(main())

