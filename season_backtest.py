import pandas as pd
import numpy as np
import joblib
import json
from sklearn.metrics import accuracy_score
import warnings
warnings.filterwarnings('ignore')

def test_on_specific_season(target_season='2023-24', confidence_threshold=0.6):
    """Test model on a specific season using all previous seasons for training"""
    print(f"🎯 Testing on {target_season} Season")
    print("=" * 50)
    
    try:
        # 1. Load model and metadata
        print("📊 Loading model and data...")
        model = joblib.load('best_advanced_model.pkl')
        scaler = joblib.load('feature_scaler_advanced.pkl')
        
        with open('model_metadata.json', 'r') as f:
            metadata = json.load(f)
        
        # 2. Load features data
        df = pd.read_csv('ml_features_sample.csv')
        df['game_date'] = pd.to_datetime(df['game_date'])
        
        print(f"Loaded {len(df)} games")
        print(f"Available seasons: {sorted(df['season'].unique())}")
        
        # 3. Split data by season
        train_seasons = [s for s in df['season'].unique() if s < target_season]
        test_season = target_season
        
        if not train_seasons:
            print(f"❌ No training seasons available before {target_season}")
            return None
            
        if test_season not in df['season'].unique():
            print(f"❌ Test season {target_season} not found in data")
            return None
        
        # 4. Prepare training and test data
        train_df = df[df['season'].isin(train_seasons)]
        test_df = df[df['season'] == test_season]
        
        print(f"Training on seasons: {train_seasons}")
        print(f"Testing on season: {test_season}")
        print(f"Training games: {len(train_df)}")
        print(f"Test games: {len(test_df)}")
        
        # 5. Prepare features
        feature_cols = metadata['feature_columns']
        
        X_train = train_df[feature_cols].fillna(0)
        y_train = train_df['id_spread'].fillna(0)
        X_test = test_df[feature_cols].fillna(0)
        y_test = test_df['id_spread'].fillna(0)
        
        # Remove push games
        train_mask = y_train != 2
        test_mask = y_test != 2
        
        X_train_clean = X_train[train_mask]
        y_train_clean = y_train[train_mask]
        X_test_clean = X_test[test_mask]
        y_test_clean = y_test[test_mask]
        test_df_clean = test_df[test_mask].reset_index(drop=True)
        
        print(f"Training games (no pushes): {len(X_train_clean)}")
        print(f"Test games (no pushes): {len(X_test_clean)}")
        
        # 6. Train model on historical data
        print("🤖 Training model on historical data...")
        X_train_scaled = scaler.fit_transform(X_train_clean)
        X_test_scaled = scaler.transform(X_test_clean)
        
        model.fit(X_train_scaled, y_train_clean)
        
        # 7. Make predictions
        print("🔮 Making predictions...")
        y_pred = model.predict(X_test_scaled)
        y_pred_proba = model.predict_proba(X_test_scaled)
        
        # 8. Calculate performance
        accuracy = accuracy_score(y_test_clean, y_pred)
        
        # 9. Calculate betting performance
        max_probs = np.max(y_pred_proba, axis=1)
        high_confidence_mask = max_probs >= confidence_threshold
        
        if not np.any(high_confidence_mask):
            print(f"⚠️ No predictions meet confidence threshold {confidence_threshold}")
            return None
        
        y_test_filtered = y_test_clean[high_confidence_mask]
        y_pred_filtered = y_pred[high_confidence_mask]
        test_df_filtered = test_df_clean[high_confidence_mask]
        
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
        
        # 10. Display results
        print(f"\n📈 {target_season} SEASON RESULTS")
        print("=" * 50)
        print(f"Test Period: {test_df_filtered['game_date'].min().strftime('%Y-%m-%d')} to {test_df_filtered['game_date'].max().strftime('%Y-%m-%d')}")
        print(f"Total Games in Season: {len(test_df_clean)}")
        print(f"High-Confidence Bets: {total_bets}")
        print(f"Overall Accuracy: {accuracy:.3f}")
        print(f"Win Rate (High-Confidence): {win_rate:.3f}")
        print(f"ROI: {roi:.1f}%")
        print(f"Average Confidence: {np.mean(max_probs[high_confidence_mask]):.3f}")
        
        # 11. Monthly breakdown
        print(f"\n📊 MONTHLY BREAKDOWN")
        print("-" * 50)
        test_df_filtered['month'] = test_df_filtered['game_date'].dt.month
        for month in sorted(test_df_filtered['month'].unique()):
            month_data = test_df_filtered[test_df_filtered['month'] == month]
            month_y_test = y_test_filtered[test_df_filtered['month'] == month]
            month_y_pred = y_pred_filtered[test_df_filtered['month'] == month]
            
            month_accuracy = accuracy_score(month_y_test, month_y_pred)
            month_bets = len(month_data)
            month_correct = sum(month_y_test == month_y_pred)
            month_win_rate = month_correct / month_bets if month_bets > 0 else 0
            
            month_name = pd.to_datetime(f"2024-{month:02d}-01").strftime('%B')
            print(f"{month_name}: {month_correct}/{month_bets} ({month_win_rate:.3f}) - {month_bets} bets")
        
        # 12. Sample predictions
        print(f"\n🎲 SAMPLE PREDICTIONS")
        print("-" * 50)
        sample_indices = np.random.choice(len(test_df_filtered), min(5, len(test_df_filtered)), replace=False)
        
        for i, idx in enumerate(sample_indices):
            game = test_df_filtered.iloc[idx]
            pred = y_pred_filtered[idx]
            actual = y_test_filtered.iloc[idx]
            conf = max_probs[high_confidence_mask][idx]
            
            pred_label = "Favorite Covers" if pred == 1 else "Underdog Covers"
            actual_label = "Favorite Covers" if actual == 1 else "Underdog Covers"
            correct = "✓" if pred == actual else "✗"
            
            print(f"Game {i+1}: {game['away_team_abbr']} @ {game['home_team_abbr']} "
                  f"({game['game_date'].strftime('%Y-%m-%d')})")
            print(f"  Spread: {game['spread']}, Predicted: {pred_label}, "
                  f"Actual: {actual_label} {correct} (Conf: {conf:.3f})")
        
        return {
            'season': target_season,
            'accuracy': accuracy,
            'win_rate': win_rate,
            'roi': roi,
            'total_bets': total_bets,
            'correct_bets': correct_bets
        }
        
    except Exception as e:
        print(f"❌ Season backtest failed: {e}")
        return None

def test_multiple_seasons(seasons=['2021-22', '2022-23', '2023-24'], confidence_threshold=0.6):
    """Test model on multiple seasons"""
    print("🎯 Multi-Season Backtest")
    print("=" * 50)
    
    results = []
    
    for season in seasons:
        print(f"\n{'='*20} {season} {'='*20}")
        result = test_on_specific_season(season, confidence_threshold)
        if result:
            results.append(result)
    
    # Summary
    if results:
        print(f"\n📊 MULTI-SEASON SUMMARY")
        print("=" * 50)
        print(f"{'Season':<10} {'Bets':<6} {'Win Rate':<10} {'ROI':<8} {'Accuracy':<10}")
        print("-" * 50)
        
        total_bets = 0
        total_correct = 0
        total_roi = 0
        
        for result in results:
            print(f"{result['season']:<10} {result['total_bets']:<6} {result['win_rate']:<10.3f} "
                  f"{result['roi']:<8.1f}% {result['accuracy']:<10.3f}")
            total_bets += result['total_bets']
            total_correct += result['correct_bets']
            total_roi += result['roi']
        
        overall_win_rate = total_correct / total_bets if total_bets > 0 else 0
        overall_roi = total_roi / len(results) if results else 0
        
        print("-" * 50)
        print(f"{'Overall':<10} {total_bets:<6} {overall_win_rate:<10.3f} "
              f"{overall_roi:<8.1f}% {'N/A':<10}")
        
        return results
    
    return None

if __name__ == "__main__":
    # Test on specific season
    test_on_specific_season('2023-24', confidence_threshold=0.6)
    
    # Or test multiple seasons
    # test_multiple_seasons(['2021-22', '2022-23', '2023-24'], confidence_threshold=0.6)
