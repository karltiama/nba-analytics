from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime
import psycopg2
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="NBA Betting ML Service", version="1.0.0")

# Global variables for model and scaler
model = None
scaler = None
model_metadata = None

class PredictionRequest(BaseModel):
    game_id: str
    features: dict

class PredictionResponse(BaseModel):
    game_id: str
    predicted_class: int
    confidence: float
    probabilities: list
    recommendation: dict

def load_model():
    """Load the trained model and scaler"""
    global model, scaler, model_metadata
    
    if model is None:
        try:
            model = joblib.load('best_advanced_model.pkl')
            scaler = joblib.load('feature_scaler_advanced.pkl')
            
            import json
            with open('model_metadata.json', 'r') as f:
                model_metadata = json.load(f)
                
            print("✅ Model loaded successfully")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            raise e

def get_database_connection():
    """Get database connection"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL not found in environment variables")
    
    if database_url.startswith('postgresql://'):
        database_url = database_url.replace('postgresql://', 'postgresql+psycopg2://')
    
    return create_engine(database_url)

def calculate_win_rate(games_df, team_id):
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

def calculate_points_for(games_df, team_id):
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

def calculate_points_against(games_df, team_id):
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

def calculate_point_differential(games_df, team_id):
    """Calculate point differential for a team"""
    return calculate_points_for(games_df, team_id) - calculate_points_against(games_df, team_id)

def calculate_recent_form(games_df, team_id, num_games):
    """Calculate recent form (win rate in last N games)"""
    recent_games = games_df.head(num_games)
    return calculate_win_rate(recent_games, team_id)

def calculate_rest_days(games_df, team_id, game_date):
    """Calculate rest days since last game"""
    if len(games_df) == 0:
        return 7
    
    last_game = games_df.iloc[0]
    time_diff = game_date - last_game['gameDate']
    return time_diff.days

def calculate_season_progress(game_date, season):
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

async def generate_game_features(game_data):
    """Generate features for a game"""
    try:
        engine = get_database_connection()
        
        # Get historical data for both teams
        home_history_query = """
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
        LIMIT 10
        """
        
        home_history = pd.read_sql(home_history_query, engine, params={
            'team_id': game_data['homeTeamId'], 
            'game_date': game_data['gameDate']
        })
        
        away_history = pd.read_sql(home_history_query, engine, params={
            'team_id': game_data['awayTeamId'], 
            'game_date': game_data['gameDate']
        })
        
        # Calculate features
        features = {
            'spread': game_data['spread'] or 0,
            'total': game_data['total'] or 0,
            'home_win_rate': calculate_win_rate(home_history, game_data['homeTeamId']),
            'away_win_rate': calculate_win_rate(away_history, game_data['awayTeamId']),
            'home_points_for': calculate_points_for(home_history, game_data['homeTeamId']),
            'away_points_for': calculate_points_for(away_history, game_data['awayTeamId']),
            'home_points_against': calculate_points_against(home_history, game_data['homeTeamId']),
            'away_points_against': calculate_points_against(away_history, game_data['awayTeamId']),
            'home_point_differential': calculate_point_differential(home_history, game_data['homeTeamId']),
            'away_point_differential': calculate_point_differential(away_history, game_data['awayTeamId']),
            'home_recent_form_5': calculate_recent_form(home_history, game_data['homeTeamId'], 5),
            'away_recent_form_5': calculate_recent_form(away_history, game_data['awayTeamId'], 5),
            'home_rest_days': calculate_rest_days(home_history, game_data['homeTeamId'], game_data['gameDate']),
            'away_rest_days': calculate_rest_days(away_history, game_data['awayTeamId'], game_data['gameDate']),
            'h2h_games': 0,  # Simplified for now
            'h2h_home_wins': 0,
            'h2h_away_wins': 0,
            'win_rate_difference': calculate_win_rate(home_history, game_data['homeTeamId']) - calculate_win_rate(away_history, game_data['awayTeamId']),
            'point_differential_difference': calculate_point_differential(home_history, game_data['homeTeamId']) - calculate_point_differential(away_history, game_data['awayTeamId']),
            'recent_form_difference': calculate_recent_form(home_history, game_data['homeTeamId'], 5) - calculate_recent_form(away_history, game_data['awayTeamId'], 5),
            'rest_days_difference': calculate_rest_days(home_history, game_data['homeTeamId'], game_data['gameDate']) - calculate_rest_days(away_history, game_data['awayTeamId'], game_data['gameDate']),
            'season_progress': calculate_season_progress(game_data['gameDate'], game_data['season']),
            'is_playoffs': game_data['seasonType'] == 'Playoffs',
            'is_regular_season': game_data['seasonType'] == 'Regular Season',
            'spread_magnitude': abs(game_data['spread'] or 0),
            'total_magnitude': game_data['total'] or 0,
            'is_home_favorite': game_data['whosFavored'] == 'home',
            'is_away_favorite': game_data['whosFavored'] == 'away',
            'favorite_spread': game_data['spread'] if game_data['whosFavored'] == 'home' else -(game_data['spread'] or 0)
        }
        
        return features
        
    except Exception as e:
        print(f"Error generating features: {e}")
        return None

@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    load_model()

@app.get("/")
async def root():
    return {"message": "NBA Betting ML Service is running"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """Make a prediction for a game"""
    try:
        if model is None:
            load_model()
        
        # Convert features to array in the correct order
        feature_array = [request.features.get(col, 0) for col in model_metadata['feature_columns']]
        
        # Scale features
        scaled_features = scaler.transform([feature_array])
        
        # Make prediction
        predicted_class = model.predict(scaled_features)[0]
        probabilities = model.predict_proba(scaled_features)[0]
        confidence = float(np.max(probabilities))
        
        # Generate recommendation
        threshold = model_metadata['best_threshold']
        should_bet = confidence >= threshold
        bet_type = "Favorite Covers" if predicted_class == 1 else "Underdog Covers"
        
        recommendation = {
            "should_bet": should_bet,
            "bet_type": bet_type if should_bet else None,
            "confidence": confidence,
            "recommendation": f"Bet on {bet_type}" if should_bet else f"No bet - Confidence too low ({confidence:.1%} < {threshold:.1%})"
        }
        
        return PredictionResponse(
            game_id=request.game_id,
            predicted_class=int(predicted_class),
            confidence=confidence,
            probabilities=probabilities.tolist(),
            recommendation=recommendation
        )
        
    except Exception as e:
        print(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.post("/predict-game/{game_id}")
async def predict_game(game_id: str):
    """Generate features and predict for a specific game"""
    try:
        if model is None:
            load_model()
        
        # Get game data from database
        engine = get_database_connection()
        game_query = """
        SELECT 
            g.id,
            g."gameDate",
            g.season,
            g."seasonType",
            g."homeTeamId",
            g."awayTeamId",
            g.spread,
            g.total,
            g."whosFavored"
        FROM games g
        WHERE g.id = %(game_id)s
        """
        
        game_data = pd.read_sql(game_query, engine, params={'game_id': game_id})
        
        if game_data.empty:
            raise HTTPException(status_code=404, detail="Game not found")
        
        game = game_data.iloc[0].to_dict()
        
        # Generate features
        features = await generate_game_features(game)
        
        if features is None:
            raise HTTPException(status_code=400, detail="Unable to generate features")
        
        # Make prediction
        prediction_request = PredictionRequest(
            game_id=game_id,
            features=features
        )
        
        return await predict(prediction_request)
        
    except Exception as e:
        print(f"Game prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Game prediction failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
