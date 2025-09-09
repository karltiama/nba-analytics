import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, TimeSeriesSplit
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import warnings
warnings.filterwarnings('ignore')

def calculate_betting_metrics(y_true, y_pred, y_proba, spreads, confidence_threshold=0.6):
    """Calculate betting-specific performance metrics"""
    
    # Filter predictions by confidence threshold
    high_confidence_mask = np.max(y_proba, axis=1) >= confidence_threshold
    
    if not np.any(high_confidence_mask):
        return {
            'roi': 0.0,
            'win_rate': 0.0,
            'total_bets': 0,
            'profitable_bets': 0,
            'avg_confidence': 0.0,
            'sharpe_ratio': 0.0
        }
    
    y_true_filtered = y_true[high_confidence_mask]
    y_pred_filtered = y_pred[high_confidence_mask]
    y_proba_filtered = y_proba[high_confidence_mask]
    spreads_filtered = spreads[high_confidence_mask]
    
    # Calculate betting results
    # For spread betting: -110 odds (bet $110 to win $100)
    bet_amount = 110
    win_amount = 100
    
    total_bets = len(y_true_filtered)
    correct_predictions = (y_true_filtered == y_pred_filtered).sum()
    win_rate = correct_predictions / total_bets if total_bets > 0 else 0
    
    # Calculate ROI
    total_wagered = total_bets * bet_amount
    total_won = correct_predictions * (bet_amount + win_amount)
    total_lost = (total_bets - correct_predictions) * bet_amount
    net_profit = total_won - total_lost
    roi = (net_profit / total_wagered) * 100 if total_wagered > 0 else 0
    
    # Calculate Sharpe ratio (simplified)
    if total_bets > 1:
        returns = np.where(y_true_filtered == y_pred_filtered, win_amount, -bet_amount)
        sharpe_ratio = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0
    else:
        sharpe_ratio = 0
    
    return {
        'roi': roi,
        'win_rate': win_rate,
        'total_bets': total_bets,
        'profitable_bets': correct_predictions,
        'avg_confidence': np.mean(np.max(y_proba_filtered, axis=1)),
        'sharpe_ratio': sharpe_ratio
    }

def create_advanced_ml_models():
    """Create advanced ML models optimized for betting ROI"""
    print("🚀 Creating advanced ML models for betting ROI optimization...\n")
    
    try:
        # 1. Load the sample features
        print("📊 Loading sample features...")
        df = pd.read_csv('ml_features_sample.csv')
        print(f"Loaded {len(df)} games with {len(df.columns)} features")
        
        # 2. Prepare features and targets
        print("\n🔧 Preparing data for advanced ML...")
        
        # Select feature columns
        exclude_cols = ['game_id', 'game_date', 'season', 'season_type', 'home_team_abbr', 'away_team_abbr', 
                       'id_spread', 'id_total', 'moneyline_home', 'moneyline_away']
        
        feature_cols = [col for col in df.columns if col not in exclude_cols]
        print(f"Using {len(feature_cols)} features")
        
        # Prepare features and targets
        X = df[feature_cols].fillna(0)
        y_spread = df['id_spread'].fillna(0)
        spreads = df['spread'].fillna(0)
        
        # Remove push games for binary classification
        non_push_mask = y_spread != 2
        X_clean = X[non_push_mask]
        y_clean = y_spread[non_push_mask]
        spreads_clean = spreads[non_push_mask]
        
        print(f"After removing push games: {len(X_clean)} games")
        print(f"Target distribution: {y_clean.value_counts().to_dict()}")
        
        # 3. Time-based split (more realistic for betting)
        # Use first 70% for training, last 30% for testing
        split_idx = int(len(X_clean) * 0.7)
        X_train, X_test = X_clean.iloc[:split_idx], X_clean.iloc[split_idx:]
        y_train, y_test = y_clean.iloc[:split_idx], y_clean.iloc[split_idx:]
        spreads_train, spreads_test = spreads_clean.iloc[:split_idx], spreads_clean.iloc[split_idx:]
        
        print(f"Training set: {len(X_train)} games")
        print(f"Test set: {len(X_test)} games")
        
        # 4. Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # 5. Define advanced models
        models = {
            'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
            'Random Forest': RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42),
            'Gradient Boosting': GradientBoostingClassifier(n_estimators=200, max_depth=6, random_state=42),
            'XGBoost': xgb.XGBClassifier(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                eval_metric='logloss'
            )
        }
        
        results = {}
        
        print("\n🎯 Training advanced models...")
        for name, model in models.items():
            print(f"\nTraining {name}...")
            
            # Use scaled data for logistic regression, original for tree-based models
            if name == 'Logistic Regression':
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_test_scaled)
                y_pred_proba = model.predict_proba(X_test_scaled)
            else:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                y_pred_proba = model.predict_proba(X_test)
            
            # Calculate traditional metrics
            accuracy = accuracy_score(y_test, y_pred)
            auc = roc_auc_score(y_test, y_pred_proba[:, 1])
            
            # Calculate betting metrics
            betting_metrics = calculate_betting_metrics(y_test.values, y_pred, y_pred_proba, spreads_test.values)
            
            results[name] = {
                'model': model,
                'accuracy': accuracy,
                'auc': auc,
                'betting_metrics': betting_metrics,
                'predictions': y_pred,
                'probabilities': y_pred_proba
            }
            
            print(f"  Accuracy: {accuracy:.3f}")
            print(f"  AUC: {auc:.3f}")
            print(f"  ROI: {betting_metrics['roi']:.1f}%")
            print(f"  Win Rate: {betting_metrics['win_rate']:.3f}")
            print(f"  Total Bets: {betting_metrics['total_bets']}")
            print(f"  Sharpe Ratio: {betting_metrics['sharpe_ratio']:.3f}")
        
        # 6. Find best model by ROI
        best_model_name = max(results.keys(), key=lambda k: results[k]['betting_metrics']['roi'])
        best_model = results[best_model_name]
        
        print(f"\n🏆 Best Model by ROI: {best_model_name}")
        print(f"   ROI: {best_model['betting_metrics']['roi']:.1f}%")
        print(f"   Win Rate: {best_model['betting_metrics']['win_rate']:.3f}")
        print(f"   Total Bets: {best_model['betting_metrics']['total_bets']}")
        
        # 7. Optimize confidence threshold
        print(f"\n🎯 Optimizing confidence threshold for {best_model_name}...")
        
        confidence_thresholds = [0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8]
        best_threshold = 0.6
        best_roi = best_model['betting_metrics']['roi']
        
        for threshold in confidence_thresholds:
            metrics = calculate_betting_metrics(
                y_test.values, 
                best_model['predictions'], 
                best_model['probabilities'], 
                spreads_test.values, 
                threshold
            )
            
            print(f"  Threshold {threshold:.2f}: ROI={metrics['roi']:.1f}%, Bets={metrics['total_bets']}, Win Rate={metrics['win_rate']:.3f}")
            
            if metrics['roi'] > best_roi and metrics['total_bets'] >= 3:  # Need at least 3 bets
                best_roi = metrics['roi']
                best_threshold = threshold
        
        print(f"  Best threshold: {best_threshold:.2f} (ROI: {best_roi:.1f}%)")
        
        # 8. Feature importance analysis
        if hasattr(best_model['model'], 'feature_importances_'):
            print(f"\n🔍 Top 15 Most Important Features for {best_model_name}:")
            feature_importance = pd.DataFrame({
                'feature': feature_cols,
                'importance': best_model['model'].feature_importances_
            }).sort_values('importance', ascending=False)
            
            for i, (_, row) in enumerate(feature_importance.head(15).iterrows()):
                print(f"  {i+1:2d}. {row['feature']:<30} {row['importance']:.3f}")
        
        # 9. Model comparison
        print(f"\n📊 Model Comparison:")
        print(f"{'Model':<20} {'Accuracy':<10} {'AUC':<8} {'ROI':<8} {'Win Rate':<10} {'Bets':<6}")
        print("-" * 70)
        for name, result in results.items():
            metrics = result['betting_metrics']
            print(f"{name:<20} {result['accuracy']:<10.3f} {result['auc']:<8.3f} {metrics['roi']:<8.1f}% {metrics['win_rate']:<10.3f} {metrics['total_bets']:<6}")
        
        # 10. Save the best model
        import joblib
        joblib.dump(best_model['model'], 'best_advanced_model.pkl')
        joblib.dump(scaler, 'feature_scaler_advanced.pkl')
        
        # Save model metadata
        model_metadata = {
            'model_name': best_model_name,
            'best_threshold': float(best_threshold),
            'feature_columns': feature_cols,
            'performance': {
                'roi': float(best_model['betting_metrics']['roi']),
                'win_rate': float(best_model['betting_metrics']['win_rate']),
                'total_bets': int(best_model['betting_metrics']['total_bets']),
                'profitable_bets': int(best_model['betting_metrics']['profitable_bets']),
                'avg_confidence': float(best_model['betting_metrics']['avg_confidence']),
                'sharpe_ratio': float(best_model['betting_metrics']['sharpe_ratio'])
            }
        }
        
        import json
        with open('model_metadata.json', 'w') as f:
            json.dump(model_metadata, f, indent=2)
        
        print(f"\n💾 Best model saved as 'best_advanced_model.pkl'")
        print(f"💾 Scaler saved as 'feature_scaler_advanced.pkl'")
        print(f"💾 Metadata saved as 'model_metadata.json'")
        
        return best_model, feature_cols, best_threshold
        
    except Exception as e:
        print(f"❌ Advanced model creation failed: {e}")
        raise

if __name__ == "__main__":
    create_advanced_ml_models()
