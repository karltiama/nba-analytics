import pandas as pd
import numpy as np
import joblib
import json
from sklearn.metrics import accuracy_score
import warnings
warnings.filterwarnings('ignore')

def debug_backtest():
    """Debug the backtest to see what's happening with the data"""
    print("DEBUG: NBA Betting Model Backtest")
    print("=" * 50)
    
    try:
        # 1. Check if files exist
        import os
        files_to_check = [
            'best_advanced_model.pkl',
            'feature_scaler_advanced.pkl', 
            'model_metadata.json',
            'ml_features_sample.csv'
        ]
        
        print("Checking required files:")
        for file in files_to_check:
            exists = os.path.exists(file)
            size = os.path.getsize(file) if exists else 0
            print(f"  {file}: {'EXISTS' if exists else 'MISSING'} ({size} bytes)")
        
        # 2. Load and analyze the features data
        print(f"\nAnalyzing features data:")
        df = pd.read_csv('ml_features_sample.csv')
        print(f"  Total rows: {len(df)}")
        print(f"  Columns: {len(df.columns)}")
        print(f"  Seasons: {sorted(df['season'].unique())}")
        
        # 3. Check for missing values
        print(f"\nData quality:")
        print(f"  Missing values in key columns:")
        key_cols = ['id_spread', 'spread', 'home_team_abbr', 'away_team_abbr']
        for col in key_cols:
            if col in df.columns:
                missing = df[col].isnull().sum()
                print(f"    {col}: {missing} missing")
        
        # 4. Analyze the target variable
        print(f"\nTarget variable analysis:")
        if 'id_spread' in df.columns:
            target_counts = df['id_spread'].value_counts()
            print(f"  id_spread distribution:")
            for value, count in target_counts.items():
                print(f"    {value}: {count} games")
            
            # Remove push games
            non_push_mask = df['id_spread'] != 2
            df_clean = df[non_push_mask]
            print(f"  After removing push games: {len(df_clean)} games")
        
        # 5. Check confidence threshold impact
        print(f"\nConfidence threshold analysis:")
        if 'best_advanced_model.pkl' in files_to_check and os.path.exists('best_advanced_model.pkl'):
            try:
                model = joblib.load('best_advanced_model.pkl')
                scaler = joblib.load('feature_scaler_advanced.pkl')
                
                with open('model_metadata.json', 'r') as f:
                    metadata = json.load(f)
                
                feature_cols = metadata['feature_columns']
                X = df[feature_cols].fillna(0)
                y = df['id_spread'].fillna(0)
                
                # Remove push games
                non_push_mask = y != 2
                X_clean = X[non_push_mask]
                y_clean = y[non_push_mask]
                df_clean = df[non_push_mask].reset_index(drop=True)
                
                # Time-based split
                split_idx = int(len(X_clean) * 0.7)
                X_test = X_clean.iloc[split_idx:]
                y_test = y_clean.iloc[split_idx:]
                df_test = df_clean.iloc[split_idx:].reset_index(drop=True)
                
                # Make predictions
                X_test_scaled = scaler.transform(X_test)
                y_pred = model.predict(X_test_scaled)
                y_pred_proba = model.predict_proba(X_test_scaled)
                
                print(f"  Test set size: {len(X_test)} games")
                print(f"  Prediction probabilities shape: {y_pred_proba.shape}")
                
                # Check confidence distribution
                max_probs = np.max(y_pred_proba, axis=1)
                print(f"  Confidence score distribution:")
                print(f"    Min: {max_probs.min():.3f}")
                print(f"    Max: {max_probs.max():.3f}")
                print(f"    Mean: {max_probs.mean():.3f}")
                print(f"    Median: {np.median(max_probs):.3f}")
                
                # Test different confidence thresholds
                thresholds = [0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8]
                print(f"\n  Confidence threshold impact:")
                for threshold in thresholds:
                    mask = max_probs >= threshold
                    count = mask.sum()
                    print(f"    {threshold:.2f}: {count} games ({count/len(max_probs)*100:.1f}%)")
                
            except Exception as e:
                print(f"  Error loading model: {e}")
        else:
            print("  Model files not found - cannot test confidence thresholds")
        
        # 6. Recommendations
        print(f"\nRECOMMENDATIONS:")
        if len(df) < 100:
            print("  - Need more data: Current dataset has only {} games".format(len(df)))
            print("  - Run: python create_ml_features_sample.py")
            print("  - Check database connection and data availability")
        
        if 'id_spread' in df.columns:
            push_games = (df['id_spread'] == 2).sum()
            if push_games > len(df) * 0.1:
                print(f"  - High push rate: {push_games} push games ({push_games/len(df)*100:.1f}%)")
                print("  - Consider adjusting spread calculation")
        
        print("  - Try lower confidence threshold (0.5) for more bets")
        print("  - Check if model is overfitting (confidence scores too high)")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_backtest()
