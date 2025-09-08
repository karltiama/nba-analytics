"""
Database connection and utilities for NBA data import
"""
import os
import asyncio
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.cursor = None
    
    async def connect(self):
        """Connect to the database"""
        try:
            # Get database URL from environment
            database_url = os.getenv('DATABASE_URL')
            if not database_url:
                raise ValueError("DATABASE_URL not found in environment variables")
            
            # Parse the URL
            import urllib.parse
            parsed = urllib.parse.urlparse(database_url)
            
            # Connect to PostgreSQL
            self.connection = psycopg2.connect(
                host=parsed.hostname,
                port=parsed.port,
                database=parsed.path[1:],  # Remove leading slash
                user=parsed.username,
                password=parsed.password
            )
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            print("✅ Connected to database")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from the database"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("✅ Disconnected from database")
    
    async def get_team_by_name(self, name: str) -> Optional[dict]:
        """Get team by name"""
        self.cursor.execute("SELECT * FROM teams WHERE name = %s", (name,))
        result = self.cursor.fetchone()
        return dict(result) if result else None
    
    async def get_team_by_abbreviation(self, abbreviation: str) -> Optional[dict]:
        """Get team by abbreviation"""
        self.cursor.execute("SELECT * FROM teams WHERE abbreviation = %s", (abbreviation,))
        result = self.cursor.fetchone()
        return dict(result) if result else None
    
    async def create_team(self, team_data: dict) -> dict:
        """Create a new team"""
        query = """
            INSERT INTO teams (id, name, abbreviation, city, conference, division, "logoUrl", "createdAt", "updatedAt")
            VALUES (gen_random_uuid(), %(name)s, %(abbreviation)s, %(city)s, %(conference)s, %(division)s, %(logoUrl)s, NOW(), NOW())
            ON CONFLICT (name) DO UPDATE SET
                abbreviation = EXCLUDED.abbreviation,
                city = EXCLUDED.city,
                conference = EXCLUDED.conference,
                division = EXCLUDED.division,
                "updatedAt" = NOW()
            RETURNING *
        """
        self.cursor.execute(query, team_data)
        result = self.cursor.fetchone()
        self.connection.commit()
        return dict(result)
    
    async def create_player(self, player_data: dict) -> dict:
        """Create a new player"""
        query = """
            INSERT INTO players (id, name, position, height, weight, "jerseyNumber", "teamId", "isActive", "createdAt", "updatedAt")
            VALUES (gen_random_uuid(), %(name)s, %(position)s, %(height)s, %(weight)s, %(jerseyNumber)s, %(teamId)s, %(isActive)s, NOW(), NOW())
            RETURNING *
        """
        self.cursor.execute(query, player_data)
        result = self.cursor.fetchone()
        self.connection.commit()
        return dict(result)
    
    async def create_game(self, game_data: dict) -> dict:
        """Create a new game"""
        query = """
            INSERT INTO games (id, "gameDate", season, "seasonType", "homeTeamId", "awayTeamId", 
                             "homeScore", "awayScore", status, attendance, venue, "createdAt", "updatedAt")
            VALUES (gen_random_uuid(), %(gameDate)s, %(season)s, %(seasonType)s, %(homeTeamId)s, %(awayTeamId)s,
                    %(homeScore)s, %(awayScore)s, %(status)s, %(attendance)s, %(venue)s, NOW(), NOW())
            RETURNING *
        """
        self.cursor.execute(query, game_data)
        result = self.cursor.fetchone()
        self.connection.commit()
        return dict(result)
    
    async def create_team_stats(self, stats_data: dict) -> dict:
        """Create team statistics with duplicate handling"""
        query = """
            INSERT INTO team_stats (id, "teamId", season, "gamesPlayed", wins, losses, "pointsPerGame",
                                   "pointsAllowed", "fieldGoalPct", "threePointPct", "freeThrowPct",
                                   rebounds, assists, turnovers, steals, blocks, "createdAt", "updatedAt")
            VALUES (gen_random_uuid(), %(teamId)s, %(season)s, %(gamesPlayed)s, %(wins)s, %(losses)s, %(pointsPerGame)s,
                   %(pointsAllowed)s, %(fieldGoalPct)s, %(threePointPct)s, %(freeThrowPct)s,
                   %(rebounds)s, %(assists)s, %(turnovers)s, %(steals)s, %(blocks)s, NOW(), NOW())
            ON CONFLICT ("teamId", season) DO UPDATE SET
                "gamesPlayed" = EXCLUDED."gamesPlayed",
                wins = EXCLUDED.wins,
                losses = EXCLUDED.losses,
                "pointsPerGame" = EXCLUDED."pointsPerGame",
                "pointsAllowed" = EXCLUDED."pointsAllowed",
                "fieldGoalPct" = EXCLUDED."fieldGoalPct",
                "threePointPct" = EXCLUDED."threePointPct",
                "freeThrowPct" = EXCLUDED."freeThrowPct",
                rebounds = EXCLUDED.rebounds,
                assists = EXCLUDED.assists,
                turnovers = EXCLUDED.turnovers,
                steals = EXCLUDED.steals,
                blocks = EXCLUDED.blocks,
                "updatedAt" = NOW()
            RETURNING *
        """
        self.cursor.execute(query, stats_data)
        result = self.cursor.fetchone()
        self.connection.commit()
        return dict(result)
    
    async def create_player_stats(self, stats_data: dict) -> dict:
        """Create player statistics"""
        query = """
            INSERT INTO player_stats (id, "playerId", season, "seasonType", "gamesPlayed", "minutesPerGame", "pointsPerGame",
                                     rebounds, assists, steals, blocks, turnovers, "fieldGoalPct",
                                     "threePointPct", "freeThrowPct", "createdAt", "updatedAt")
            VALUES (gen_random_uuid(), %(playerId)s, %(season)s, %(seasonType)s, %(gamesPlayed)s, %(minutesPerGame)s, %(pointsPerGame)s,
                   %(rebounds)s, %(assists)s, %(steals)s, %(blocks)s, %(turnovers)s, %(fieldGoalPct)s,
                   %(threePointPct)s, %(freeThrowPct)s, NOW(), NOW())
            ON CONFLICT ("playerId", season, "seasonType") DO UPDATE SET
                "gamesPlayed" = EXCLUDED."gamesPlayed",
                "minutesPerGame" = EXCLUDED."minutesPerGame",
                "pointsPerGame" = EXCLUDED."pointsPerGame",
                rebounds = EXCLUDED.rebounds,
                assists = EXCLUDED.assists,
                steals = EXCLUDED.steals,
                blocks = EXCLUDED.blocks,
                turnovers = EXCLUDED.turnovers,
                "fieldGoalPct" = EXCLUDED."fieldGoalPct",
                "threePointPct" = EXCLUDED."threePointPct",
                "freeThrowPct" = EXCLUDED."freeThrowPct",
                "updatedAt" = NOW()
            RETURNING *
        """
        self.cursor.execute(query, stats_data)
        result = self.cursor.fetchone()
        self.connection.commit()
        return dict(result)
    
    async def get_existing_teams(self) -> list:
        """Get all existing teams"""
        self.cursor.execute("SELECT * FROM teams")
        results = self.cursor.fetchall()
        return [dict(row) for row in results]
    
    async def clear_teams(self):
        """Clear all teams from the database"""
        try:
            # Delete in order to respect foreign key constraints
            # First delete dependent tables
            self.cursor.execute("DELETE FROM team_stats")
            self.cursor.execute("DELETE FROM player_stats")
            self.cursor.execute("DELETE FROM players")
            self.cursor.execute("DELETE FROM games")
            self.cursor.execute("DELETE FROM teams")
            self.connection.commit()
            print("✅ Cleared all teams and related data from database")
        except Exception as e:
            self.connection.rollback()
            print(f"❌ Error clearing teams: {e}")
            raise
    
    async def get_existing_players(self) -> list:
        """Get all existing players"""
        self.cursor.execute("SELECT * FROM players")
        results = self.cursor.fetchall()
        return [dict(row) for row in results]
    
    async def get_existing_games(self) -> list:
        """Get all existing games"""
        self.cursor.execute("SELECT * FROM games")
        results = self.cursor.fetchall()
        return [dict(row) for row in results]
    
    async def bulk_create_player_stats(self, stats_list: list) -> int:
        """Bulk create player statistics"""
        if not stats_list:
            return 0
        
        # Prepare the data for bulk insert (using snake_case column names)
        columns = [
            'playerId', 'season', 'gamesPlayed', 'minutesPerGame', 'pointsPerGame', 
            'rebounds', 'assists', 'steals', 'blocks', 'turnovers', 
            'fieldGoalPct', 'threePointPct', 'freeThrowPct', 'createdAt', 'updatedAt'
        ]
        
        # Create values list
        values_list = []
        for stats in stats_list:
            values = [
                stats.get('playerId'),
                stats.get('season'),
                stats.get('gamesPlayed', 0),
                stats.get('minutesPerGame', 0),
                stats.get('pointsPerGame', 0),
                stats.get('rebounds', 0),
                stats.get('assists', 0),
                stats.get('steals', 0),
                stats.get('blocks', 0),
                stats.get('turnovers', 0),
                stats.get('fieldGoalPct', 0),
                stats.get('threePointPct', 0),
                stats.get('freeThrowPct', 0),
                'NOW()',
                'NOW()'
            ]
            values_list.append(values)
        
        # Create the bulk insert query with proper column quoting
        quoted_columns = [f'"{col}"' for col in columns]
        placeholders = ', '.join(['%s'] * len(columns))
        query = f"""
        INSERT INTO player_stats ({', '.join(quoted_columns)})
        VALUES ({placeholders})
        ON CONFLICT ("playerId", season) DO UPDATE SET
            "gamesPlayed" = EXCLUDED."gamesPlayed",
            "minutesPerGame" = EXCLUDED."minutesPerGame",
            "pointsPerGame" = EXCLUDED."pointsPerGame",
            "rebounds" = EXCLUDED."rebounds",
            "assists" = EXCLUDED."assists",
            "steals" = EXCLUDED."steals",
            "blocks" = EXCLUDED."blocks",
            "turnovers" = EXCLUDED."turnovers",
            "fieldGoalPct" = EXCLUDED."fieldGoalPct",
            "threePointPct" = EXCLUDED."threePointPct",
            "freeThrowPct" = EXCLUDED."freeThrowPct",
            "updatedAt" = NOW()
        """
        
        # Execute bulk insert
        self.cursor.executemany(query, values_list)
        await self.connection.commit()
        
        return len(values_list)
    
    async def execute_query(self, query: str, params: list = None) -> list:
        """Execute a custom query and return results"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            results = self.cursor.fetchall()
            return [dict(row) for row in results]
        except Exception as e:
            print(f"❌ Error executing query: {e}")
            return []
    
    async def get_game_by_teams_and_date(self, home_team_id: str, away_team_id: str, game_date) -> Optional[dict]:
        """Get game by teams and date"""
        self.cursor.execute(
            "SELECT * FROM games WHERE \"homeTeamId\" = %s AND \"awayTeamId\" = %s AND \"gameDate\" = %s",
            (home_team_id, away_team_id, game_date)
        )
        result = self.cursor.fetchone()
        return dict(result) if result else None
    
    async def create_individual_player_stat(self, stats_data: dict) -> dict:
        """Create individual player statistics record"""
        query = """
            INSERT INTO player_stats (id, "playerId", "gameId", season, "seasonType", "gamesPlayed", 
                                     "minutesPerGame", "pointsPerGame", rebounds, assists, steals, blocks, 
                                     turnovers, "fieldGoalPct", "threePointPct", "freeThrowPct", 
                                     "createdAt", "updatedAt")
            VALUES (gen_random_uuid(), %(playerId)s, %(gameId)s, %(season)s, %(seasonType)s, %(gamesPlayed)s,
                   %(minutesPerGame)s, %(pointsPerGame)s, %(rebounds)s, %(assists)s, %(steals)s, %(blocks)s,
                   %(turnovers)s, %(fieldGoalPct)s, %(threePointPct)s, %(freeThrowPct)s, NOW(), NOW())
            RETURNING *
        """
        self.cursor.execute(query, stats_data)
        result = self.cursor.fetchone()
        self.connection.commit()
        return dict(result)