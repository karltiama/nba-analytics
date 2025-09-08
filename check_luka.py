import asyncio
from data_import.database import DatabaseManager

async def check_luka():
    db = DatabaseManager()
    await db.connect()
    
    try:
        # Check Luka Doncic stats
        db.cursor.execute('''
            SELECT "playerId", name, season, "seasonType", "gamesPlayed" 
            FROM player_stats ps 
            JOIN players p ON ps."playerId" = p.id 
            WHERE p.name LIKE '%Luka%' 
            ORDER BY season, "seasonType"
        ''')
        results = db.cursor.fetchall()
        print('Luka Doncic stats:')
        for row in results:
            print(f'Season: {row["season"]} | Type: {row["seasonType"]} | Games: {row["gamesPlayed"]}')
        
        # Check some playoff data to see the pattern
        print('\nSample playoff data:')
        db.cursor.execute('''
            SELECT season, "seasonType", COUNT(*) as count, MAX("gamesPlayed") as max_games
            FROM player_stats 
            WHERE "seasonType" = 'Playoffs'
            GROUP BY season, "seasonType"
            ORDER BY season
            LIMIT 10
        ''')
        results = db.cursor.fetchall()
        for row in results:
            print(f'Season: {row["season"]} | Type: {row["seasonType"]} | Count: {row["count"]} | Max Games: {row["max_games"]}')
            
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
    finally:
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(check_luka())

