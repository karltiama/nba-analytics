"""
Feature Engineering Module for NBA Player Performance Prediction
Implements the 6 key features for predicting NBA player game performance
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
from .database import DatabaseManager

class FeatureEngineer:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        
    async def compute_recent_performance_features(self, player_id: str, game_date: datetime, 
                                                lookback_games: int = 5) -> Dict[str, float]:
        """
        Feature 1: Recent Player Performance
        Calculate rolling averages for the last N games for key stats
        
        Args:
            player_id: Player ID
            game_date: Date of the game to predict
            lookback_games: Number of recent games to look back (default 5)
            
        Returns:
            Dictionary with recent performance features
        """
        try:
            # Get player's recent games before the target date
            recent_games = await self._get_player_recent_games(player_id, game_date, lookback_games)
            
            if len(recent_games) == 0:
                return self._get_default_recent_performance_features()
            
            # Calculate rolling averages for key stats
            features = {}
            
            # Points rolling average
            points = recent_games['points'].values
            features['recent_points_avg'] = np.mean(points)
            features['recent_points_std'] = np.std(points) if len(points) > 1 else 0.0
            
            # Assists rolling average
            assists = recent_games['assists'].values
            features['recent_assists_avg'] = np.mean(assists)
            features['recent_assists_std'] = np.std(assists) if len(assists) > 1 else 0.0
            
            # Rebounds rolling average
            rebounds = recent_games['reboundsTotal'].values
            features['recent_rebounds_avg'] = np.mean(rebounds)
            features['recent_rebounds_std'] = np.std(rebounds) if len(rebounds) > 1 else 0.0
            
            # Minutes played rolling average
            minutes = recent_games['numMinutes'].values
            features['recent_minutes_avg'] = np.mean(minutes)
            features['recent_minutes_std'] = np.std(minutes) if len(minutes) > 1 else 0.0
            
            # Shooting percentages
            fg_pct = recent_games['fieldGoalsPercentage'].values
            features['recent_fg_pct_avg'] = np.mean(fg_pct)
            
            three_pct = recent_games['threePointersPercentage'].values
            features['recent_three_pct_avg'] = np.mean(three_pct)
            
            ft_pct = recent_games['freeThrowsPercentage'].values
            features['recent_ft_pct_avg'] = np.mean(ft_pct)
            
            # Additional performance indicators
            features['recent_games_count'] = len(recent_games)
            features['recent_win_rate'] = recent_games['win'].mean() if 'win' in recent_games.columns else 0.0
            
            # Trend indicators (comparing first half vs second half of recent games)
            if len(recent_games) >= 4:
                mid_point = len(recent_games) // 2
                recent_half = recent_games.iloc[:mid_point]
                older_half = recent_games.iloc[mid_point:]
                
                features['points_trend'] = recent_half['points'].mean() - older_half['points'].mean()
                features['assists_trend'] = recent_half['assists'].mean() - older_half['assists'].mean()
                features['rebounds_trend'] = recent_half['reboundsTotal'].mean() - older_half['reboundsTotal'].mean()
            else:
                features['points_trend'] = 0.0
                features['assists_trend'] = 0.0
                features['rebounds_trend'] = 0.0
            
            return features
            
        except Exception as e:
            print(f"❌ Error computing recent performance features for player {player_id}: {e}")
            return self._get_default_recent_performance_features()
    
    async def _get_player_recent_games(self, player_id: str, game_date: datetime, 
                                     lookback_games: int) -> pd.DataFrame:
        """Get player's recent games before a specific date"""
        try:
            # Since player_stats doesn't have individual game records, we need to work differently
            # For now, let's get the player's season averages as a fallback
            # In a real implementation, you'd need individual game records
            
            query = """
            SELECT 
                "pointsPerGame" as points,
                assists,
                rebounds,
                "minutesPerGame" as numMinutes,
                "fieldGoalPct" as fieldGoalsPercentage,
                "threePointPct" as threePointersPercentage,
                "freeThrowPct" as freeThrowsPercentage,
                steals,
                blocks,
                turnovers,
                0 as plusMinusPoints,
                NOW() as gameDate,
                '' as homeTeamId,
                '' as awayTeamId,
                0 as homeScore,
                0 as awayScore,
                0.5 as win
            FROM player_stats 
            WHERE "playerId" = %s 
            AND season = %s
            ORDER BY "createdAt" DESC
            LIMIT 1
            """
            
            # Get current season (simplified)
            current_year = game_date.year
            if game_date.month >= 10:  # NBA season starts in October
                season = f"{current_year}-{str(current_year + 1)[2:]}"
            else:
                season = f"{current_year - 1}-{str(current_year)[2:]}"
            
            # Execute the query using the database manager
            result = await self.db.execute_query(query, [player_id, season])
            
            if result:
                # For demonstration, create multiple rows with the same data
                # In reality, you'd need individual game records
                df = pd.DataFrame(result)
                if not df.empty:
                    # Replicate the row to simulate multiple games
                    df = pd.concat([df] * min(lookback_games, 3), ignore_index=True)
                return df
            else:
                return pd.DataFrame()
            
        except Exception as e:
            print(f"❌ Error fetching recent games for player {player_id}: {e}")
            return pd.DataFrame()
    
    def _get_default_recent_performance_features(self) -> Dict[str, float]:
        """Return default values when no recent games are available"""
        return {
            'recent_points_avg': 0.0,
            'recent_points_std': 0.0,
            'recent_assists_avg': 0.0,
            'recent_assists_std': 0.0,
            'recent_rebounds_avg': 0.0,
            'recent_rebounds_std': 0.0,
            'recent_minutes_avg': 0.0,
            'recent_minutes_std': 0.0,
            'recent_fg_pct_avg': 0.0,
            'recent_three_pct_avg': 0.0,
            'recent_ft_pct_avg': 0.0,
            'recent_games_count': 0,
            'recent_win_rate': 0.0,
            'points_trend': 0.0,
            'assists_trend': 0.0,
            'rebounds_trend': 0.0
        }
    
    async def compute_all_features(self, player_id: str, game_date: datetime, 
                                 opponent_team_id: str, home_team_id: str) -> Dict[str, float]:
        """
        Compute all 6 feature sets for a player's game performance prediction
        
        Args:
            player_id: Player ID
            game_date: Date of the game
            opponent_team_id: Opponent team ID
            home_team_id: Home team ID (to determine if player is home/away)
            
        Returns:
            Dictionary with all computed features
        """
        features = {}
        
        # Feature 1: Recent Player Performance
        recent_perf = await self.compute_recent_performance_features(player_id, game_date)
        features.update(recent_perf)
        
        # TODO: Implement other features
        # Feature 2: Opponent Defensive Strength
        # Feature 3: Home/Away Indicator  
        # Feature 4: Minutes Played
        # Feature 5: Rest Days
        # Feature 6: Game Context
        
        return features
