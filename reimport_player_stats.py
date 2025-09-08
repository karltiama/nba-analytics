"""
Re-import player statistics with correct seasonType field
"""
import asyncio
from data_import.database import DatabaseManager
from data_import.stats_importer import StatsImporter
from data_import.player_importer import PlayerImporter
from data_import.team_importer import TeamImporter

async def reimport_player_stats():
    """Clear and re-import player statistics with correct seasonType"""
    db = DatabaseManager()
    await db.connect()
    
    try:
        print("🗑️ Clearing existing player stats...")
        db.cursor.execute("DELETE FROM player_stats")
        db.connection.commit()
        print("✅ Cleared existing player stats")
        
        # Get team and player mappings
        print("📋 Getting team and player mappings...")
        
        teams = await db.get_existing_teams()
        team_mapping = {team['name']: team['id'] for team in teams}
        
        players = await db.get_existing_players()
        player_mapping = {player['name']: player['id'] for player in players}
        
        print(f"📊 Found {len(team_mapping)} teams and {len(player_mapping)} players")
        
        # Import player stats with correct seasonType
        print("🔄 Re-importing player stats with correct seasonType...")
        stats_importer = StatsImporter(db, team_mapping, player_mapping)
        await stats_importer.import_player_stats_from_csv('data/PlayerStatistics.csv')
        
        print("✅ Player stats re-import complete!")
        
    except Exception as e:
        print(f"❌ Error during re-import: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(reimport_player_stats())
