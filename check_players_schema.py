#!/usr/bin/env python3
"""
Check players table schema
"""
import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from data_import.database import DatabaseManager

async def main():
    """Check players table schema"""
    print("🔍 Checking players table schema...")
    
    db_manager = DatabaseManager()
    
    try:
        # Connect to database
        await db_manager.connect()
        print("✅ Connected to database")
        
        # Check players table schema
        print("\n📋 === PLAYERS TABLE SCHEMA ===")
        db_manager.cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'players'
            ORDER BY ordinal_position
        """)
        
        columns = db_manager.cursor.fetchall()
        print("Players table columns:")
        for col in columns:
            print(f"  {col['column_name']}: {col['data_type']} ({'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'})")
        
        # Check a few sample players
        print("\n👥 === SAMPLE PLAYERS ===")
        db_manager.cursor.execute('''
            SELECT id, name
            FROM players 
            WHERE LOWER(name) LIKE '%giannis%' OR LOWER(name) LIKE '%antetokounmpo%'
            LIMIT 5
        ''')
        
        giannis_players = db_manager.cursor.fetchall()
        if giannis_players:
            print("Found Giannis records:")
            for player in giannis_players:
                print(f"  ID: {player['id']}, Name: {player['name']}")
        else:
            print("No Giannis records found, checking all players...")
            db_manager.cursor.execute('SELECT id, name FROM players LIMIT 10')
            all_players = db_manager.cursor.fetchall()
            for player in all_players:
                print(f"  ID: {player['id']}, Name: {player['name']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(main())

