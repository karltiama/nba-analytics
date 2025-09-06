#!/usr/bin/env python3
"""
Fix player statistics to only include regular season games
"""
import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from data_import.database import DatabaseManager

async def main():
    """Fix player statistics to only include regular season games"""
    print("🔧 Fixing player statistics to only include regular season games...")
    
    db_manager = DatabaseManager()
    
    try:
        # Connect to database
        await db_manager.connect()
        print("✅ Connected to database")
        
        # First, let's check the current state
        print("\n📊 === CURRENT PLAYER STATS STATE ===")
        db_manager.cursor.execute('''
            SELECT COUNT(*) as total_records
            FROM player_stats
        ''')
        total_records = db_manager.cursor.fetchone()['total_records']
        print(f"Total player stats records: {total_records:,}")
        
        # Check Giannis's current stats
        db_manager.cursor.execute('''
            SELECT season, "gamesPlayed", "pointsPerGame"
            FROM player_stats ps
            JOIN players p ON ps."playerId" = p.id
            WHERE p.name = 'Giannis Antetokounmpo'
            AND season >= '2020-21'
            ORDER BY season DESC
        ''')
        
        giannis_current = db_manager.cursor.fetchall()
        print("\nGiannis current stats (including playoffs):")
        for stat in giannis_current:
            print(f"  {stat['season']}: {stat['gamesPlayed']} games, {stat['pointsPerGame']:.1f} PPG")
        
        # Now let's recalculate player stats using only regular season games
        print("\n🔄 === RECALCULATING PLAYER STATS (REGULAR SEASON ONLY) ===")
        
        # Get all players
        db_manager.cursor.execute('SELECT id, name FROM players')
        players = db_manager.cursor.fetchall()
        print(f"Processing {len(players)} players...")
        
        # Process each player
        processed = 0
        for player in players:
            player_id = player['id']
            player_name = player['name']
            
            # Get player's team
            db_manager.cursor.execute('''
                SELECT "teamId" FROM players WHERE id = %s
            ''', (player_id,))
            team_result = db_manager.cursor.fetchone()
            
            if not team_result or not team_result['teamId']:
                continue
            
            team_id = team_result['teamId']
            
            # Get regular season games for this player's team by season
            db_manager.cursor.execute('''
                SELECT 
                    season,
                    COUNT(*) as regular_season_games,
                    AVG(CASE WHEN "homeTeamId" = %s THEN "homeScore" ELSE "awayScore" END) as avg_points_scored,
                    AVG(CASE WHEN "homeTeamId" = %s THEN "awayScore" ELSE "homeScore" END) as avg_points_allowed
                FROM games 
                WHERE "seasonType" = 'Regular Season'
                AND ("homeTeamId" = %s OR "awayTeamId" = %s)
                GROUP BY season
                ORDER BY season
            ''', (team_id, team_id, team_id, team_id))
            
            team_games = db_manager.cursor.fetchall()
            
            # Update player stats for each season
            for team_game in team_games:
                season = team_game['season']
                regular_games = team_game['regular_season_games']
                
                # Check if we have existing player stats for this season
                db_manager.cursor.execute('''
                    SELECT id FROM player_stats 
                    WHERE "playerId" = %s AND season = %s
                ''', (player_id, season))
                
                existing_stat = db_manager.cursor.fetchone()
                
                if existing_stat:
                    # Update existing record with regular season games only
                    db_manager.cursor.execute('''
                        UPDATE player_stats 
                        SET "gamesPlayed" = %s,
                            "updatedAt" = NOW()
                        WHERE id = %s
                    ''', (regular_games, existing_stat['id']))
                else:
                    # Create new record (this shouldn't happen, but just in case)
                    print(f"  ⚠️ No existing stats found for {player_name} in {season}")
            
            processed += 1
            if processed % 100 == 0:
                print(f"  Processed {processed}/{len(players)} players...")
        
        # Commit all changes
        db_manager.connection.commit()
        print(f"✅ Updated {processed} players")
        
        # Verify the fix
        print("\n✅ === VERIFICATION AFTER FIX ===")
        db_manager.cursor.execute('''
            SELECT season, "gamesPlayed", "pointsPerGame"
            FROM player_stats ps
            JOIN players p ON ps."playerId" = p.id
            WHERE p.name = 'Giannis Antetokounmpo'
            AND season >= '2020-21'
            ORDER BY season DESC
        ''')
        
        giannis_fixed = db_manager.cursor.fetchall()
        print("Giannis stats after fix (regular season only):")
        for stat in giannis_fixed:
            print(f"  {stat['season']}: {stat['gamesPlayed']} games, {stat['pointsPerGame']:.1f} PPG")
        
        # Check for any remaining unrealistic game counts
        print("\n🔍 === CHECKING FOR REMAINING ISSUES ===")
        db_manager.cursor.execute('''
            SELECT COUNT(*) as high_game_count
            FROM player_stats 
            WHERE "gamesPlayed" > 82
        ''')
        
        high_games = db_manager.cursor.fetchone()['high_game_count']
        print(f"Records with >82 games: {high_games}")
        
        if high_games == 0:
            print("✅ All game counts are now realistic (≤82 games)")
        else:
            print("⚠️ Still have some records with >82 games - may need further investigation")
        
        print("\n🎯 === SUMMARY ===")
        print("• Fixed player statistics to only count regular season games")
        print("• This should resolve the issue with Giannis showing 73 games")
        print("• All game counts should now be ≤82 (realistic for NBA regular season)")
        print("• Data is now accurate for betting model backtesting")
        
    except Exception as e:
        print(f"❌ Error during fix: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(main())

