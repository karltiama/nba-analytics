import pandas as pd
import numpy as np
import joblib
import json
from sklearn.metrics import accuracy_score
import warnings
warnings.filterwarnings('ignore')

def simple_backtest(model_type='advanced'):
    """Simple backtest using existing ML features data"""
    print(f"Simple NBA Betting Model Backtest - {model_type.upper()} Model")
    print("=" * 50)
    
    try:
        # 1. Determine file names based on model type
        def get_model_files(model_type):
            if model_type == 'basic':
                return {
                    'model_file': 'best_ml_model.pkl',
                    'scaler_file': 'feature_scaler.pkl',
                    'metadata_file': 'model_metadata.json'
                }
            else:  # advanced or xgboost
                return {
                    'model_file': 'best_advanced_model.pkl',
                    'scaler_file': 'feature_scaler_advanced.pkl',
                    'metadata_file': 'model_metadata.json'
                }
        
        files = get_model_files(model_type)
        
        # Load model and metadata
        print(f"Loading {model_type} model and data...")
        model = joblib.load(files['model_file'])
        scaler = joblib.load(files['scaler_file'])
        
        with open(files['metadata_file'], 'r') as f:
            metadata = json.load(f)
        
        # 2. Load features data
        df = pd.read_csv('ml_features_sample.csv')
        df['game_date'] = pd.to_datetime(df['game_date'])
        
        print(f"Loaded {len(df)} games")
        print(f"Seasons: {sorted(df['season'].unique())}")
        
        # 3. Prepare features
        feature_cols = metadata['feature_columns']
        X = df[feature_cols].fillna(0)
        y = df['id_spread'].fillna(0)
        
        # Remove push games
        non_push_mask = y != 2
        X_clean = X[non_push_mask]
        y_clean = y[non_push_mask]
        df_clean = df[non_push_mask].reset_index(drop=True)
        
        print(f"After removing push games: {len(X_clean)} games")
        
        # 4. Time-based split (use first 70% for training, last 30% for testing)
        split_idx = int(len(X_clean) * 0.7)
        
        X_train = X_clean.iloc[:split_idx]
        X_test = X_clean.iloc[split_idx:]
        y_train = y_clean.iloc[:split_idx]
        y_test = y_clean.iloc[split_idx:]
        df_test = df_clean.iloc[split_idx:].reset_index(drop=True)
        
        print(f"Training set: {len(X_train)} games")
        print(f"Test set: {len(X_test)} games")
        
        # 5. Scale features and train model
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        model.fit(X_train_scaled, y_train)
        
        # 6. Make predictions
        y_pred = model.predict(X_test_scaled)
        y_pred_proba = model.predict_proba(X_test_scaled)
        
        # 7. Calculate performance metrics
        accuracy = accuracy_score(y_test, y_pred)
        
        # 8. Calculate betting performance
        confidence_threshold = 0.6
        max_probs = np.max(y_pred_proba, axis=1)
        high_confidence_mask = max_probs >= confidence_threshold
        
        if np.any(high_confidence_mask):
            y_test_filtered = y_test[high_confidence_mask]
            y_pred_filtered = y_pred[high_confidence_mask]
            df_test_filtered = df_test[high_confidence_mask]
            
            # Betting metrics
            total_bets = len(y_test_filtered)
            correct_bets = sum(y_test_filtered == y_pred_filtered)
            win_rate = correct_bets / total_bets
            
            # ROI calculation (-110 odds)
            bet_amount = 110
            win_amount = 100
            total_wagered = total_bets * bet_amount
            total_won = correct_bets * (bet_amount + win_amount)
            total_lost = (total_bets - correct_bets) * bet_amount
            net_profit = total_won - total_lost
            roi = (net_profit / total_wagered) * 100
            
            # 9. Display results
            print(f"\nBACKTEST RESULTS")
            print("=" * 50)
            print(f"Test Period: {df_test['game_date'].min().strftime('%Y-%m-%d')} to {df_test['game_date'].max().strftime('%Y-%m-%d')}")
            print(f"Total Games in Test Set: {len(y_test)}")
            print(f"High-Confidence Bets: {total_bets}")
            print(f"Overall Accuracy: {accuracy:.3f}")
            print(f"Win Rate (High-Confidence): {win_rate:.3f}")
            print(f"ROI: {roi:.1f}%")
            print(f"Average Confidence: {np.mean(max_probs[high_confidence_mask]):.3f}")
            
            # 10. Season breakdown
            print(f"\nSEASON BREAKDOWN")
            print("-" * 50)
            try:
                for season in sorted(df_test_filtered['season'].unique()):
                    season_mask = df_test_filtered['season'] == season
                    season_data = df_test_filtered[season_mask]
                    
                    # Get corresponding y_test and y_pred for this season
                    season_indices = df_test_filtered[season_mask].index
                    season_y_test = y_test_filtered[season_indices]
                    season_y_pred = y_pred_filtered[season_indices]
                    
                    season_accuracy = accuracy_score(season_y_test, season_y_pred)
                    season_bets = len(season_data)
                    season_correct = sum(season_y_test == season_y_pred)
                    season_win_rate = season_correct / season_bets if season_bets > 0 else 0
                    
                    print(f"{season}: {season_correct}/{season_bets} ({season_win_rate:.3f}) - {season_bets} bets")
            except Exception as e:
                print(f"Season breakdown error: {e}")
                print("Skipping season breakdown...")
            
            # 11. Sample predictions
            print(f"\nSAMPLE PREDICTIONS")
            print("-" * 50)
            sample_indices = np.random.choice(len(df_test_filtered), min(5, len(df_test_filtered)), replace=False)
            
            for i, idx in enumerate(sample_indices):
                game = df_test_filtered.iloc[idx]
                pred = y_pred_filtered[idx]
                actual = y_test_filtered.iloc[idx]
                conf = max_probs[high_confidence_mask][idx]
                
                pred_label = "Favorite Covers" if pred == 1 else "Underdog Covers"
                actual_label = "Favorite Covers" if actual == 1 else "Underdog Covers"
                correct = "CORRECT" if pred == actual else "WRONG"
                
                print(f"Game {i+1}: {game['away_team_abbr']} @ {game['home_team_abbr']} "
                      f"({game['game_date'].strftime('%Y-%m-%d')})")
                print(f"  Spread: {game['spread']}, Predicted: {pred_label}, "
                      f"Actual: {actual_label} {correct} (Conf: {conf:.3f})")
            
            # 12. Confidence threshold analysis
            print(f"\nCONFIDENCE THRESHOLD ANALYSIS")
            print("-" * 50)
            thresholds = [0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8]
            
            for threshold in thresholds:
                mask = max_probs >= threshold
                if np.any(mask):
                    filtered_y_test = y_test[mask]
                    filtered_y_pred = y_pred[mask]
                    filtered_bets = len(filtered_y_test)
                    filtered_correct = sum(filtered_y_test == filtered_y_pred)
                    filtered_win_rate = filtered_correct / filtered_bets if filtered_bets > 0 else 0
                    
                    # Calculate ROI for this threshold
                    filtered_roi = ((filtered_correct * (bet_amount + win_amount) - 
                                   (filtered_bets - filtered_correct) * bet_amount) / 
                                  (filtered_bets * bet_amount)) * 100 if filtered_bets > 0 else 0
                    
                    print(f"Threshold {threshold:.2f}: {filtered_bets} bets, "
                          f"Win Rate: {filtered_win_rate:.3f}, ROI: {filtered_roi:.1f}%")
            
            # Create comprehensive results dictionary
            results = {
                'accuracy': float(accuracy),
                'win_rate': float(win_rate),
                'roi': float(roi),
                'total_bets': int(total_bets),
                'correct_bets': int(correct_bets),
                'avg_confidence': float(np.mean(max_probs[high_confidence_mask])),
                'season_performance': {},
                'sample_predictions': []
            }
            
            # Add season performance
            try:
                for season in sorted(df_test_filtered['season'].unique()):
                    season_mask = df_test_filtered['season'] == season
                    season_data = df_test_filtered[season_mask]
                    season_indices = df_test_filtered[season_mask].index
                    season_y_test = y_test_filtered[season_indices]
                    season_y_pred = y_pred_filtered[season_indices]
                    
                    season_bets = len(season_data)
                    season_correct = sum(season_y_test == season_y_pred)
                    season_win_rate = season_correct / season_bets if season_bets > 0 else 0
                    
                    # Calculate ROI for this season
                    season_roi = ((season_correct * (bet_amount + win_amount) - 
                                  (season_bets - season_correct) * bet_amount) / 
                                 (season_bets * bet_amount)) * 100 if season_bets > 0 else 0
                    
                    results['season_performance'][season] = {
                        'total_bets': int(season_bets),
                        'correct_bets': int(season_correct),
                        'win_rate': float(season_win_rate),
                        'roi': float(season_roi)
                    }
            except Exception as e:
                print(f"Season performance error: {e}")
            
            # Add sample predictions
            try:
                sample_indices = np.random.choice(len(df_test_filtered), min(5, len(df_test_filtered)), replace=False)
                for i, idx in enumerate(sample_indices):
                    game = df_test_filtered.iloc[idx]
                    pred = y_pred_filtered[idx]
                    actual = y_test_filtered.iloc[idx]
                    conf = max_probs[high_confidence_mask][idx]
                    
                    pred_label = "Favorite Covers" if pred == 1 else "Underdog Covers"
                    actual_label = "Favorite Covers" if actual == 1 else "Underdog Covers"
                    correct = pred == actual
                    
                    results['sample_predictions'].append({
                        'game': f"{game['away_team_abbr']} @ {game['home_team_abbr']}",
                        'date': game['game_date'].strftime('%Y-%m-%d'),
                        'spread': float(game['spread']),
                        'total': float(game['total']),
                        'predicted': pred_label,
                        'actual': actual_label,
                        'correct': bool(correct),
                        'confidence': float(conf),
                        'home_team': {
                            'abbr': game['home_team_abbr'],
                            'win_rate': float(game['home_win_rate']),
                            'points_for': float(game['home_points_for']),
                            'points_against': float(game['home_points_against']),
                            'point_differential': float(game['home_point_differential']),
                            'recent_form_5': float(game['home_recent_form_5']),
                            'rest_days': int(game['home_rest_days'])
                        },
                        'away_team': {
                            'abbr': game['away_team_abbr'],
                            'win_rate': float(game['away_win_rate']),
                            'points_for': float(game['away_points_for']),
                            'points_against': float(game['away_points_against']),
                            'point_differential': float(game['away_point_differential']),
                            'recent_form_5': float(game['away_recent_form_5']),
                            'rest_days': int(game['away_rest_days'])
                        },
                        'matchup': {
                            'win_rate_difference': float(game['win_rate_difference']),
                            'point_differential_difference': float(game['point_differential_difference']),
                            'recent_form_difference': float(game['recent_form_difference']),
                            'rest_days_difference': int(game['rest_days_difference']),
                            'h2h_games': int(game['h2h_games']),
                            'h2h_home_wins': int(game['h2h_home_wins']),
                            'h2h_away_wins': int(game['h2h_away_wins'])
                        },
                        'context': {
                            'season_progress': float(game['season_progress']),
                            'is_playoffs': bool(game['is_playoffs']),
                            'is_regular_season': bool(game['is_regular_season']),
                            'is_home_favorite': bool(game['is_home_favorite']),
                            'favorite_spread': float(game['favorite_spread'])
                        }
                    })
            except Exception as e:
                print(f"Sample predictions error: {e}")
            
            # Print JSON result for API consumption
            print("\n" + "="*50)
            print("JSON_RESULT_START")
            print(json.dumps(results))
            print("JSON_RESULT_END")
            print("="*50)
            
            return results
        else:
            print("WARNING: No predictions meet confidence threshold")
            return None
            
    except Exception as e:
        print(f"ERROR: Backtest failed: {e}")
        return None

if __name__ == "__main__":
    import sys
    model_type = sys.argv[1] if len(sys.argv) > 1 else 'advanced'
    simple_backtest(model_type)
