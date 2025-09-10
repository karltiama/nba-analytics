import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import joblib
import json
from sklearn.metrics import accuracy_score, classification_report
import warnings
warnings.filterwarnings('ignore')

def load_model_and_features():
    """Load the trained model and feature columns"""
    try:
        # Load the best model
        model = joblib.load('best_advanced_model.pkl')
        scaler = joblib.load('feature_scaler_advanced.pkl')
        
        # Load model metadata
        with open('model_metadata.json', 'r') as f:
            metadata = json.load(f)
        
        return model, scaler, metadata
    except FileNotFoundError as e:
        print(f"❌ Model files not found: {e}")
        print("Please run create_advanced_ml_models.py first")
        return None, None, None

def create_backtest_data(season_start='2020-21', season_end='2023-24'):
    """Create backtest data for specific seasons"""
    print(f"🔍 Creating backtest data for seasons {season_start} to {season_end}...")
    
    try:
        # Load the full features dataset
        df = pd.read_csv('ml_features_sample.csv')
        df['game_date'] = pd.to_datetime(df['game_date'])
        
        # Filter by season range
        season_filter = (df['season'] >= season_start) & (df['season'] <= season_end)
        backtest_df = df[season_filter].copy()
        
        print(f"Found {len(backtest_df)} games for backtesting")
        print(f"Seasons: {sorted(backtest_df['season'].unique())}")
        
        return backtest_df
        
    except Exception as e:
        print(f"❌ Error creating backtest data: {e}")
        return None

def walk_forward_validation(df, model, scaler, feature_cols, retrain_frequency=50):
    """Perform walk-forward validation for time series data"""
    print(f"🚀 Starting walk-forward validation (retrain every {retrain_frequency} games)...")
    
    # Sort by date to ensure chronological order
    df_sorted = df.sort_values('game_date').reset_index(drop=True)
    
    predictions = []
    probabilities = []
    actuals = []
    game_info = []
    
    # Start with minimum training set (first 100 games)
    min_training_size = 100
    
    for i in range(min_training_size, len(df_sorted)):
        current_game = df_sorted.iloc[i]
        
        # Get training data (all games before current game)
        train_data = df_sorted.iloc[:i]
        
        # Skip if not enough data
        if len(train_data) < min_training_size:
            continue
            
        # Prepare features
        X_train = train_data[feature_cols].fillna(0)
        y_train = train_data['id_spread'].fillna(0)
        
        # Remove push games
        non_push_mask = y_train != 2
        X_train_clean = X_train[non_push_mask]
        y_train_clean = y_train[non_push_mask]
        
        if len(X_train_clean) < 50:  # Need minimum data
            continue
            
        # Retrain model every N games
        if i % retrain_frequency == 0 or i == min_training_size:
            print(f"  Retraining model at game {i} (training on {len(X_train_clean)} games)")
            
            # Scale features
            X_train_scaled = scaler.fit_transform(X_train_clean)
            
            # Retrain model
            model.fit(X_train_scaled, y_train_clean)
        
        # Make prediction on current game
        X_current = current_game[feature_cols].fillna(0).values.reshape(1, -1)
        X_current_scaled = scaler.transform(X_current)
        
        # Predict
        pred = model.predict(X_current_scaled)[0]
        pred_proba = model.predict_proba(X_current_scaled)[0]
        
        # Store results
        predictions.append(pred)
        probabilities.append(pred_proba)
        actuals.append(current_game['id_spread'])
        game_info.append({
            'game_date': current_game['game_date'],
            'season': current_game['season'],
            'home_team': current_game['home_team_abbr'],
            'away_team': current_game['away_team_abbr'],
            'spread': current_game['spread'],
            'actual_spread': current_game['id_spread']
        })
        
        # Progress update
        if i % 100 == 0:
            print(f"  Processed {i} games...")
    
    return predictions, probabilities, actuals, game_info

def calculate_betting_performance(predictions, probabilities, actuals, game_info, confidence_threshold=0.6):
    """Calculate betting-specific performance metrics"""
    print(f"📊 Calculating betting performance (confidence threshold: {confidence_threshold})...")
    
    # Convert to numpy arrays
    predictions = np.array(predictions)
    probabilities = np.array(probabilities)
    actuals = np.array(actuals)
    
    # Filter by confidence threshold
    max_probs = np.max(probabilities, axis=1)
    high_confidence_mask = max_probs >= confidence_threshold
    
    if not np.any(high_confidence_mask):
        print("⚠️ No predictions meet confidence threshold")
        return None
    
    # Filter data
    pred_filtered = predictions[high_confidence_mask]
    actual_filtered = actuals[high_confidence_mask]
    prob_filtered = probabilities[high_confidence_mask]
    info_filtered = [game_info[i] for i in range(len(game_info)) if high_confidence_mask[i]]
    
    # Calculate basic metrics
    accuracy = accuracy_score(actual_filtered, pred_filtered)
    total_bets = len(pred_filtered)
    correct_bets = sum(actual_filtered == pred_filtered)
    win_rate = correct_bets / total_bets if total_bets > 0 else 0
    
    # Calculate betting ROI (assuming -110 odds)
    bet_amount = 110
    win_amount = 100
    
    total_wagered = total_bets * bet_amount
    total_won = correct_bets * (bet_amount + win_amount)
    total_lost = (total_bets - correct_bets) * bet_amount
    net_profit = total_won - total_lost
    roi = (net_profit / total_wagered) * 100 if total_wagered > 0 else 0
    
    # Calculate Sharpe ratio
    if total_bets > 1:
        returns = np.where(actual_filtered == pred_filtered, win_amount, -bet_amount)
        sharpe_ratio = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0
    else:
        sharpe_ratio = 0
    
    # Season-by-season breakdown
    season_performance = {}
    for i, info in enumerate(info_filtered):
        season = info['season']
        if season not in season_performance:
            season_performance[season] = {
                'total_bets': 0,
                'correct_bets': 0,
                'roi': 0,
                'games': []
            }
        
        season_performance[season]['total_bets'] += 1
        if actual_filtered[i] == pred_filtered[i]:
            season_performance[season]['correct_bets'] += 1
        season_performance[season]['games'].append(info)
    
    # Calculate ROI for each season
    for season in season_performance:
        season_data = season_performance[season]
        if season_data['total_bets'] > 0:
            season_roi = ((season_data['correct_bets'] * (bet_amount + win_amount) - 
                          (season_data['total_bets'] - season_data['correct_bets']) * bet_amount) / 
                         (season_data['total_bets'] * bet_amount)) * 100
            season_data['roi'] = season_roi
            season_data['win_rate'] = season_data['correct_bets'] / season_data['total_bets']
    
    return {
        'accuracy': accuracy,
        'win_rate': win_rate,
        'total_bets': total_bets,
        'correct_bets': correct_bets,
        'roi': roi,
        'sharpe_ratio': sharpe_ratio,
        'avg_confidence': np.mean(max_probs[high_confidence_mask]),
        'season_performance': season_performance
    }

def run_backtest(season_start='2020-21', season_end='2023-24', confidence_threshold=0.6):
    """Run complete backtest on historical data"""
    print("🎯 Starting NBA Betting Model Backtest")
    print("=" * 50)
    
    # 1. Load model
    model, scaler, metadata = load_model_and_features()
    if model is None:
        return
    
    # 2. Create backtest data
    backtest_df = create_backtest_data(season_start, season_end)
    if backtest_df is None or len(backtest_df) == 0:
        print("❌ No backtest data available")
        return
    
    # 3. Get feature columns
    feature_cols = metadata['feature_columns']
    
    # 4. Run walk-forward validation
    predictions, probabilities, actuals, game_info = walk_forward_validation(
        backtest_df, model, scaler, feature_cols
    )
    
    if len(predictions) == 0:
        print("❌ No predictions generated")
        return
    
    # 5. Calculate performance
    performance = calculate_betting_performance(
        predictions, probabilities, actuals, game_info, confidence_threshold
    )
    
    if performance is None:
        return
    
    # 6. Display results
    print("\n📈 BACKTEST RESULTS")
    print("=" * 50)
    print(f"Period: {season_start} to {season_end}")
    print(f"Confidence Threshold: {confidence_threshold}")
    print(f"Total Games Analyzed: {len(predictions)}")
    print(f"High-Confidence Bets: {performance['total_bets']}")
    print(f"Win Rate: {performance['win_rate']:.3f}")
    print(f"ROI: {performance['roi']:.1f}%")
    print(f"Sharpe Ratio: {performance['sharpe_ratio']:.3f}")
    print(f"Average Confidence: {performance['avg_confidence']:.3f}")
    
    # 7. Season-by-season breakdown
    print(f"\n📊 SEASON-BY-SEASON PERFORMANCE")
    print("-" * 50)
    for season in sorted(performance['season_performance'].keys()):
        season_data = performance['season_performance'][season]
        print(f"{season}: {season_data['correct_bets']}/{season_data['total_bets']} "
              f"({season_data['win_rate']:.3f}) ROI: {season_data['roi']:.1f}%")
    
    # 8. Confidence threshold optimization
    print(f"\n🎯 CONFIDENCE THRESHOLD OPTIMIZATION")
    print("-" * 50)
    thresholds = [0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8]
    
    for threshold in thresholds:
        perf = calculate_betting_performance(
            predictions, probabilities, actuals, game_info, threshold
        )
        if perf:
            print(f"Threshold {threshold:.2f}: {perf['total_bets']} bets, "
                  f"ROI: {perf['roi']:.1f}%, Win Rate: {perf['win_rate']:.3f}")
    
    # 9. Sample predictions
    print(f"\n🎲 SAMPLE PREDICTIONS")
    print("-" * 50)
    sample_indices = np.random.choice(len(predictions), min(5, len(predictions)), replace=False)
    
    for i, idx in enumerate(sample_indices):
        info = game_info[idx]
        pred = predictions[idx]
        actual = actuals[idx]
        conf = np.max(probabilities[idx])
        
        pred_label = "Favorite Covers" if pred == 1 else "Underdog Covers"
        actual_label = "Favorite Covers" if actual == 1 else "Underdog Covers"
        correct = "✓" if pred == actual else "✗"
        
        print(f"Game {i+1}: {info['away_team']} @ {info['home_team']} "
              f"({info['game_date'].strftime('%Y-%m-%d')})")
        print(f"  Spread: {info['spread']}, Predicted: {pred_label}, "
              f"Actual: {actual_label} {correct} (Conf: {conf:.3f})")
    
    return performance

if __name__ == "__main__":
    # Run backtest on recent seasons
    run_backtest(season_start='2020-21', season_end='2023-24', confidence_threshold=0.6)
