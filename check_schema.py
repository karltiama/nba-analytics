#!/usr/bin/env python3
"""
Check database schema for player_stats table
"""
import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from data_import.database import DatabaseManager

async def check_schema():
    """Check the player_stats table schema"""
    db = DatabaseManager()
    
    try:
        await db.connect()
        
        # Get column information
        db.cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'player_stats' 
            ORDER BY ordinal_position
        """)
        
        columns = db.cursor.fetchall()
        print("Player stats table columns:")
        for row in columns:
            col_name = row[0]
            data_type = row[1]
            print(f"  {col_name}: {data_type}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(check_schema())
