import asyncio
from data_import.database import DatabaseManager

async def check_data():
    db = DatabaseManager()
    await db.connect()
    
    try:
        # Check what's in the database
        db.cursor.execute('SELECT season, "seasonType", COUNT(*) as count, MAX("gamesPlayed") as max_games FROM player_stats GROUP BY season, "seasonType" ORDER BY season, "seasonType"')
        results = db.cursor.fetchall()
        print('Database data:')
        print(f'Number of results: {len(results)}')
        for i, row in enumerate(results):
            if i < 10:  # Only print first 10 rows
                print(f'Season: {row["season"]} | Type: {row["seasonType"]} | Count: {row["count"]} | Max Games: {row["max_games"]}')
        
        # Check a specific player's data
        db.cursor.execute('SELECT "playerId", season, "seasonType", "gamesPlayed" FROM player_stats WHERE "gamesPlayed" > 20 ORDER BY "gamesPlayed" DESC LIMIT 10')
        results = db.cursor.fetchall()
        print('\nTop 10 by games played:')
        for row in results:
            print(f'Player: {row["playerId"]} | Season: {row["season"]} | Type: {row["seasonType"]} | Games: {row["gamesPlayed"]}')
        
        # Check if seasonType is being set correctly
        db.cursor.execute('SELECT DISTINCT "seasonType" FROM player_stats')
        results = db.cursor.fetchall()
        print('\nUnique season types in database:')
        for row in results:
            print(f'Type: {row["seasonType"]}')
            
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
    finally:
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(check_data())
