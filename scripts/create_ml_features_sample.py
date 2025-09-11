import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import psycopg2
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_database_connection():
    """Get database connection using environment variables"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL not found in environment variables")
    
    # Convert to SQLAlchemy format if needed
    if database_url.startswith('postgresql://'):
        database_url = database_url.replace('postgresql://', 'postgresql+psycopg2://')
    
    return create_engine(database_url)

def create_ml_features_sample(sample_size=10000):
    """Create ML features for a sample of NBA games"""
    print(f"🔧 Creating ML features for {sample_size} sample games...\n")
    
    try:
        # Connect to database
        engine = get_database_connection()
        
        # 1. Get games with betting data (prioritize 2024-25 season, then others)
        query = f"""
        SELECT 
            g.id as game_id,
            g."gameDate" as game_date,
            g.season,
            g."seasonType",
            g."homeTeamId",
            g."awayTeamId",
            g."homeScore",
            g."awayScore",
            g.spread,
            g.total,
            g."moneylineHome",
            g."moneylineAway",
            g."idSpread",
            g."idTotal",
            g."whosFavored",
            ht.abbreviation as home_team_abbr,
            at.abbreviation as away_team_abbr
        FROM games g
        JOIN teams ht ON g."homeTeamId" = ht.id
        JOIN teams at ON g."awayTeamId" = at.id
        WHERE g.spread IS NOT NULL 
        AND g."homeScore" IS NOT NULL 
        AND g."awayScore" IS NOT NULL
        AND g.season IN ('2023-24', '2022-23', '2021-22', '2020-21', '2019-20', '2018-19', '2017-18', '2016-17', '2015-16')
        ORDER BY 
            CASE 
                WHEN g.season = '2023-24' THEN 1
                WHEN g.season = '2022-23' THEN 2
                WHEN g.season = '2021-22' THEN 3
                WHEN g.season = '2020-21' THEN 4
                WHEN g.season = '2019-20' THEN 5
                WHEN g.season = '2018-19' THEN 6
                WHEN g.season = '2017-18' THEN 7
                WHEN g.season = '2016-17' THEN 8
                WHEN g.season = '2015-16' THEN 9
                ELSE 10
            END,
            g."gameDate" DESC
        LIMIT {sample_size}
        """
        
        print("📊 Loading sample game data...")
        games_df = pd.read_sql(query, engine)
        print(f"Found {len(games_df)} sample games")
        
        # 2. Create features for each game
        features_list = []
        
        for idx, game in games_df.iterrows():
            print(f"Processing game {idx + 1}/{len(games_df)}: {game['away_team_abbr']} @ {game['home_team_abbr']} ({game['game_date'].strftime('%Y-%m-%d')})")
            
            # Get historical data for both teams (simplified - just last 10 games)
            home_history = get_team_history_simple(engine, game['homeTeamId'], game['game_date'], 10)
            away_history = get_team_history_simple(engine, game['awayTeamId'], game['game_date'], 10)
            
            # Get head-to-head history (last 5 games)
            h2h_history = get_head_to_head_history_simple(engine, game['homeTeamId'], game['awayTeamId'], game['game_date'], 5)
            
            # Calculate basic features
            features = {
                # Basic game info
                'game_id': game['game_id'],
                'game_date': game['game_date'],
                'season': game['season'],
                'season_type': game['seasonType'],
                'home_team_abbr': game['home_team_abbr'],
                'away_team_abbr': game['away_team_abbr'],
                
                # Target variables
                'spread': game['spread'],
                'total': game['total'],
                'moneyline_home': game['moneylineHome'],
                'moneyline_away': game['moneylineAway'],
                'id_spread': game['idSpread'],
                'id_total': game['idTotal'],
                
                # Home team features
                'home_win_rate': calculate_win_rate_simple(home_history, game['homeTeamId']),
                'home_points_for': calculate_points_for_simple(home_history, game['homeTeamId']),
                'home_points_against': calculate_points_against_simple(home_history, game['homeTeamId']),
                'home_point_differential': calculate_point_differential_simple(home_history, game['homeTeamId']),
                'home_recent_form_5': calculate_recent_form_simple(home_history, game['homeTeamId'], 5),
                'home_rest_days': calculate_rest_days_simple(home_history, game['homeTeamId'], game['game_date']),
                
                # Away team features
                'away_win_rate': calculate_win_rate_simple(away_history, game['awayTeamId']),
                'away_points_for': calculate_points_for_simple(away_history, game['awayTeamId']),
                'away_points_against': calculate_points_against_simple(away_history, game['awayTeamId']),
                'away_point_differential': calculate_point_differential_simple(away_history, game['awayTeamId']),
                'away_recent_form_5': calculate_recent_form_simple(away_history, game['awayTeamId'], 5),
                'away_rest_days': calculate_rest_days_simple(away_history, game['awayTeamId'], game['game_date']),
                
                # Head-to-head features
                'h2h_games': len(h2h_history),
                'h2h_home_wins': calculate_h2h_home_wins_simple(h2h_history, game['homeTeamId']),
                'h2h_away_wins': calculate_h2h_away_wins_simple(h2h_history, game['awayTeamId']),
                
                # Derived features
                'win_rate_difference': calculate_win_rate_simple(home_history, game['homeTeamId']) - calculate_win_rate_simple(away_history, game['awayTeamId']),
                'point_differential_difference': calculate_point_differential_simple(home_history, game['homeTeamId']) - calculate_point_differential_simple(away_history, game['awayTeamId']),
                'recent_form_difference': calculate_recent_form_simple(home_history, game['homeTeamId'], 5) - calculate_recent_form_simple(away_history, game['awayTeamId'], 5),
                'rest_days_difference': calculate_rest_days_simple(home_history, game['homeTeamId'], game['game_date']) - calculate_rest_days_simple(away_history, game['awayTeamId'], game['game_date']),
                
                # Season progression
                'season_progress': calculate_season_progress_simple(game['game_date'], game['season']),
                'is_playoffs': game['seasonType'] == 'Playoffs',
                'is_regular_season': game['seasonType'] == 'Regular Season',
                
                # Betting market features
                'spread_magnitude': abs(game['spread']),
                'total_magnitude': game['total'],
                'is_home_favorite': game['whosFavored'] == 'home',
                'is_away_favorite': game['whosFavored'] == 'away',
                'favorite_spread': game['spread'] if game['whosFavored'] == 'home' else -game['spread'],
            }
            
            features_list.append(features)
        
        # 3. Convert to DataFrame
        features_df = pd.DataFrame(features_list)
        
        print(f"\n✅ Created {len(features_df)} feature sets")
        print(f"Feature columns: {len(features_df.columns)}")
        
        # 4. Save to CSV
        features_df.to_csv('ml_features_sample.csv', index=False)
        print("📁 Sample features saved to ml_features_sample.csv")
        
        # 5. Display summary
        display_feature_summary(features_df)
        
        return features_df
        
    except Exception as e:
        print(f"❌ Feature creation failed: {e}")
        raise

def get_team_history_simple(engine, team_id, game_date, limit=10):
    """Get limited historical games for a team before the given date"""
    query = """
    SELECT 
        "gameDate",
        "homeTeamId",
        "awayTeamId",
        "homeScore",
        "awayScore"
    FROM games
    WHERE ("homeTeamId" = %(team_id)s OR "awayTeamId" = %(team_id)s)
    AND "gameDate" < %(game_date)s
    AND "homeScore" IS NOT NULL
    AND "awayScore" IS NOT NULL
    ORDER BY "gameDate" DESC
    LIMIT %(limit)s
    """
    
    return pd.read_sql(query, engine, params={'team_id': team_id, 'game_date': game_date, 'limit': limit})

def get_head_to_head_history_simple(engine, home_team_id, away_team_id, game_date, limit=5):
    """Get limited head-to-head history between two teams"""
    query = """
    SELECT 
        "gameDate",
        "homeTeamId",
        "awayTeamId",
        "homeScore",
        "awayScore"
    FROM games
    WHERE (("homeTeamId" = %(home_team_id)s AND "awayTeamId" = %(away_team_id)s) OR ("homeTeamId" = %(away_team_id)s AND "awayTeamId" = %(home_team_id)s))
    AND "gameDate" < %(game_date)s
    AND "homeScore" IS NOT NULL
    AND "awayScore" IS NOT NULL
    ORDER BY "gameDate" DESC
    LIMIT %(limit)s
    """
    
    return pd.read_sql(query, engine, params={'home_team_id': home_team_id, 'away_team_id': away_team_id, 'game_date': game_date, 'limit': limit})

def calculate_win_rate_simple(games_df, team_id):
    """Calculate win rate for a team"""
    if len(games_df) == 0:
        return 0.5
    
    wins = 0
    for _, game in games_df.iterrows():
        if game['homeTeamId'] == team_id:
            wins += 1 if game['homeScore'] > game['awayScore'] else 0
        else:
            wins += 1 if game['awayScore'] > game['homeScore'] else 0
    
    return wins / len(games_df)

def calculate_points_for_simple(games_df, team_id):
    """Calculate average points scored by a team"""
    if len(games_df) == 0:
        return 0
    
    total_points = 0
    for _, game in games_df.iterrows():
        if game['homeTeamId'] == team_id:
            total_points += game['homeScore']
        else:
            total_points += game['awayScore']
    
    return total_points / len(games_df)

def calculate_points_against_simple(games_df, team_id):
    """Calculate average points allowed by a team"""
    if len(games_df) == 0:
        return 0
    
    total_points = 0
    for _, game in games_df.iterrows():
        if game['homeTeamId'] == team_id:
            total_points += game['awayScore']
        else:
            total_points += game['homeScore']
    
    return total_points / len(games_df)

def calculate_point_differential_simple(games_df, team_id):
    """Calculate point differential for a team"""
    return calculate_points_for_simple(games_df, team_id) - calculate_points_against_simple(games_df, team_id)

def calculate_recent_form_simple(games_df, team_id, num_games):
    """Calculate recent form (win rate in last N games)"""
    recent_games = games_df.head(num_games)
    return calculate_win_rate_simple(recent_games, team_id)

def calculate_rest_days_simple(games_df, team_id, game_date):
    """Calculate rest days since last game"""
    if len(games_df) == 0:
        return 7
    
    last_game = games_df.iloc[0]
    time_diff = game_date - last_game['gameDate']
    return time_diff.days

def calculate_h2h_home_wins_simple(h2h_df, home_team_id):
    """Calculate head-to-head home wins"""
    home_games = h2h_df[h2h_df['homeTeamId'] == home_team_id]
    return sum(1 for _, game in home_games.iterrows() if game['homeScore'] > game['awayScore'])

def calculate_h2h_away_wins_simple(h2h_df, away_team_id):
    """Calculate head-to-head away wins"""
    away_games = h2h_df[h2h_df['awayTeamId'] == away_team_id]
    return sum(1 for _, game in away_games.iterrows() if game['awayScore'] > game['homeScore'])

def calculate_season_progress_simple(game_date, season):
    """Calculate season progress (0-1)"""
    try:
        year = int(season.split('-')[0])
        season_start = datetime(year, 10, 1)
        season_end = datetime(year + 1, 6, 30)
        
        total_days = (season_end - season_start).days
        days_elapsed = (game_date - season_start).days
        
        return max(0, min(1, days_elapsed / total_days))
    except:
        return 0.5

def display_feature_summary(features_df):
    """Display summary of created features"""
    print("\n📊 Feature Summary:")
    print(f"Total features: {len(features_df)}")
    print(f"Feature columns: {len(features_df.columns)}")
    
    # Show sample of first few features
    print("\nSample features (first 3 games):")
    for i in range(min(3, len(features_df))):
        game = features_df.iloc[i]
        print(f"\nGame {i + 1}:")
        print(f"  Date: {game['game_date'].strftime('%Y-%m-%d')}")
        print(f"  Teams: {game['away_team_abbr']} @ {game['home_team_abbr']}")
        print(f"  Spread: {game['spread']}, Total: {game['total']}")
        print(f"  Home Win Rate: {game['home_win_rate']:.3f}")
        print(f"  Away Win Rate: {game['away_win_rate']:.3f}")
        print(f"  Recent Form Diff: {game['recent_form_difference']:.3f}")
        print(f"  Rest Days Diff: {game['rest_days_difference']}")
    
    # Show feature statistics
    print(f"\nFeature Statistics:")
    print(f"  Win Rate Difference: {features_df['win_rate_difference'].mean():.3f} ± {features_df['win_rate_difference'].std():.3f}")
    print(f"  Point Differential Diff: {features_df['point_differential_difference'].mean():.3f} ± {features_df['point_differential_difference'].std():.3f}")
    print(f"  Recent Form Diff: {features_df['recent_form_difference'].mean():.3f} ± {features_df['recent_form_difference'].std():.3f}")
    print(f"  Rest Days Diff: {features_df['rest_days_difference'].mean():.1f} ± {features_df['rest_days_difference'].std():.1f}")

if __name__ == "__main__":
    # Run with sample size of 10000 games (multiple seasons + historical data)
    create_ml_features_sample(sample_size=10000)
