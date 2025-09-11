"""
Backtest any of the trained models
"""
import pandas as pd
import numpy as np
import joblib
import json
import sys

def backtest_model(model_name):
    """Backtest a specific model"""
    
    print(f"Simple NBA Betting Model Backtest - {model_name.upper()}")
    print("=" * 50)
    
    try:
        # Load model and scaler
        model_file = f"models/model_{model_name.lower().replace(' ', '_')}.pkl"
        scaler_file = f"models/scaler_{model_name.lower().replace(' ', '_')}.pkl"
        
        print(f"Loading {model_name} model and data...")
        model = joblib.load(model_file)
        scaler = joblib.load(scaler_file)
        
        # Load data
        df = pd.read_csv('ml_features_sample.csv')
        print(f"Loaded {len(df)} games")
        
        # Prepare features
        exclude_cols = ['game_id', 'game_date', 'season', 'season_type', 'home_team_abbr', 'away_team_abbr',
                       'id_spread', 'id_total', 'moneyline_home', 'moneyline_away']
        
        feature_cols = [col for col in df.columns if col not in exclude_cols]
        X = df[feature_cols].fillna(0)
        y = df['id_spread'].fillna(0)
        
        # Remove push games
        non_push_mask = y != 2
        X_clean = X[non_push_mask]
        y_clean = y[non_push_mask]
        df_clean = df[non_push_mask].reset_index(drop=True)
        
        print(f"After removing push games: {len(X_clean)} games")
        
        # Time-based split
        split_idx = int(len(X_clean) * 0.7)
        X_train, X_test = X_clean.iloc[:split_idx], X_clean.iloc[split_idx:]
        y_train, y_test = y_clean.iloc[:split_idx], y_clean.iloc[split_idx:]
        df_test = df_clean.iloc[split_idx:].reset_index(drop=True)
        
        print(f"Training set: {len(X_train)} games")
        print(f"Test set: {len(X_test)} games")
        
        # Scale features
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Make predictions
        if model_name in ['SVM', 'Neural Network', 'Naive Bayes', 'K-Nearest Neighbors']:
            y_pred = model.predict(X_test_scaled)
            y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
        else:
            y_pred = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test)[:, 1]
        
        # Calculate metrics
        accuracy = (y_pred == y_test).mean()
        
        # High-confidence bets (threshold 0.6)
        high_conf_mask = y_pred_proba >= 0.6
        high_conf_correct = (y_pred[high_conf_mask] == y_test[high_conf_mask]).sum()
        high_conf_total = high_conf_mask.sum()
        win_rate = high_conf_correct / high_conf_total if high_conf_total > 0 else 0
        
        # ROI calculation
        wins = high_conf_correct
        losses = high_conf_total - high_conf_correct
        roi = ((wins * 0.909) - (losses * 1.0)) / high_conf_total * 100 if high_conf_total > 0 else 0
        
        avg_confidence = y_pred_proba[high_conf_mask].mean() if high_conf_total > 0 else 0
        
        print(f"\nBACKTEST RESULTS")
        print("=" * 50)
        print(f"Test Period: {df_test['game_date'].min()} to {df_test['game_date'].max()}")
        print(f"Total Games in Test Set: {len(X_test)}")
        print(f"High-Confidence Bets: {high_conf_total}")
        print(f"Overall Accuracy: {accuracy:.3f}")
        print(f"Win Rate (High-Confidence): {win_rate:.3f}")
        print(f"ROI: {roi:.1f}%")
        print(f"Average Confidence: {avg_confidence:.3f}")
        
        # Sample predictions
        print(f"\nSAMPLE PREDICTIONS")
        print("-" * 50)
        sample_indices = np.random.choice(len(y_test), min(5, len(y_test)), replace=False)
        
        for i, idx in enumerate(sample_indices):
            actual = "Favorite Covers" if y_test.iloc[idx] == 1 else "Underdog Covers"
            predicted = "Favorite Covers" if y_pred[idx] == 1 else "Underdog Covers"
            correct = "CORRECT" if y_pred[idx] == y_test.iloc[idx] else "WRONG"
            conf = y_pred_proba[idx]
            
            home_team = df_test.iloc[idx]['home_team_abbr']
            away_team = df_test.iloc[idx]['away_team_abbr']
            spread = df_test.iloc[idx]['spread']
            date = df_test.iloc[idx]['game_date']
            
            print(f"Game {i+1}: {away_team} @ {home_team} ({date})")
            print(f"  Spread: {spread}, Predicted: {predicted}, Actual: {actual} {correct} (Conf: {conf:.3f})")
        
        # Confidence threshold analysis
        print(f"\nCONFIDENCE THRESHOLD ANALYSIS")
        print("-" * 50)
        thresholds = [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80]
        
        for threshold in thresholds:
            mask = y_pred_proba >= threshold
            if mask.sum() > 0:
                correct = (y_pred[mask] == y_test[mask]).sum()
                total = mask.sum()
                win_rate_thresh = correct / total
                wins = correct
                losses = total - correct
                roi_thresh = ((wins * 0.909) - (losses * 1.0)) / total * 100
                print(f"Threshold {threshold}: {total} bets, Win Rate: {win_rate_thresh:.3f}, ROI: {roi_thresh:.1f}%")
        
        result = {
            'model_name': model_name,
            'accuracy': float(accuracy),
            'win_rate': float(win_rate),
            'roi': float(roi),
            'total_bets': int(high_conf_total),
            'correct_bets': int(high_conf_correct),
            'avg_confidence': float(avg_confidence),
            'test_period': f"{df_test['game_date'].min()} to {df_test['game_date'].max()}",
            'total_games': int(len(X_test))
        }
        
        # Print JSON result for API consumption
        import json
        print("\n" + "="*50)
        print("JSON_RESULT_START")
        print(json.dumps(result))
        print("JSON_RESULT_END")
        print("="*50)
        
        return result
        
    except FileNotFoundError as e:
        print(f"ERROR: Could not find model file for '{model_name}'")
        print(f"Available models:")
        print("  - Logistic Regression")
        print("  - Random Forest") 
        print("  - Gradient Boosting")
        print("  - XGBoost")
        print("  - Extra Trees")
        print("  - SVM")
        print("  - Neural Network")
        print("  - Naive Bayes")
        print("  - Decision Tree")
        print("  - K-Nearest Neighbors")
        return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python backtest_any_model.py <model_name>")
        print("Example: python backtest_any_model.py 'Logistic Regression'")
        print("Example: python backtest_any_model.py 'Random Forest'")
        print("Example: python backtest_any_model.py 'XGBoost'")
        sys.exit(1)
    
    model_name = sys.argv[1]
    backtest_model(model_name)
