"""
Train and save all ML models separately for comparison
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, ExtraTreesClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
import xgboost as xgb
import joblib
import json

def train_all_models():
    """Train all available ML models and save them separately"""
    
    print("🚀 Training ALL ML models for NBA betting predictions...")
    
    # Load data
    print("📊 Loading sample features...")
    df = pd.read_csv('ml_features_sample.csv')
    print(f"Loaded {len(df)} games with {len(df.columns)} features")
    
    # Prepare features
    exclude_cols = ['game_id', 'game_date', 'season', 'season_type', 'home_team_abbr', 'away_team_abbr',
                   'id_spread', 'id_total', 'moneyline_home', 'moneyline_away']
    
    feature_cols = [col for col in df.columns if col not in exclude_cols]
    print(f"Using {len(feature_cols)} features")
    
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
    
    print(f"Training set: {len(X_train)} games")
    print(f"Test set: {len(X_test)} games")
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Define ALL models
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
        ),
        'Extra Trees': ExtraTreesClassifier(n_estimators=200, max_depth=10, random_state=42),
        'SVM': SVC(probability=True, random_state=42),
        'Neural Network': MLPClassifier(hidden_layer_sizes=(100, 50), max_iter=500, random_state=42),
        'Naive Bayes': GaussianNB(),
        'Decision Tree': DecisionTreeClassifier(max_depth=10, random_state=42),
        'K-Nearest Neighbors': KNeighborsClassifier(n_neighbors=5)
    }
    
    results = {}
    
    print("\n🎯 Training all models...")
    
    for name, model in models.items():
        print(f"\nTraining {name}...")
        
        try:
            # Train model
            if name in ['SVM', 'Neural Network', 'Naive Bayes', 'K-Nearest Neighbors']:
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_test_scaled)
                y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
            else:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                y_pred_proba = model.predict_proba(X_test)[:, 1]
            
            # Calculate metrics
            accuracy = (y_pred == y_test).mean()
            
            # Calculate ROI for high-confidence bets (threshold 0.6)
            high_conf_mask = y_pred_proba >= 0.6
            if high_conf_mask.sum() > 0:
                high_conf_correct = (y_pred[high_conf_mask] == y_test[high_conf_mask]).sum()
                high_conf_total = high_conf_mask.sum()
                win_rate = high_conf_correct / high_conf_total
                
                # Simple ROI calculation (assuming -110 odds)
                wins = high_conf_correct
                losses = high_conf_total - high_conf_correct
                roi = ((wins * 0.909) - (losses * 1.0)) / high_conf_total * 100
            else:
                win_rate = 0
                roi = 0
                high_conf_total = 0
            
            results[name] = {
                'accuracy': accuracy,
                'win_rate': win_rate,
                'roi': roi,
                'total_bets': high_conf_total,
                'model': model
            }
            
            print(f"  Accuracy: {accuracy:.3f}")
            print(f"  Win Rate (0.6+ conf): {win_rate:.3f}")
            print(f"  ROI: {roi:.1f}%")
            print(f"  High-Confidence Bets: {high_conf_total}")
            
            # Save individual model
            model_filename = f"models/model_{name.lower().replace(' ', '_')}.pkl"
            scaler_filename = f"models/scaler_{name.lower().replace(' ', '_')}.pkl"
            
            joblib.dump(model, model_filename)
            joblib.dump(scaler, scaler_filename)
            
            print(f"  💾 Saved as {model_filename}")
            
        except Exception as e:
            print(f"  ❌ Error training {name}: {str(e)}")
            results[name] = {'error': str(e)}
    
    # Print summary
    print("\n📊 MODEL COMPARISON SUMMARY")
    print("=" * 80)
    print(f"{'Model':<20} {'Accuracy':<10} {'Win Rate':<10} {'ROI':<10} {'Bets':<8}")
    print("-" * 80)
    
    for name, result in results.items():
        if 'error' not in result:
            print(f"{name:<20} {result['accuracy']:<10.3f} {result['win_rate']:<10.3f} {result['roi']:<10.1f} {result['total_bets']:<8}")
        else:
            print(f"{name:<20} ERROR: {result['error']}")
    
    # Find best model
    valid_results = {k: v for k, v in results.items() if 'error' not in v and v['total_bets'] > 0}
    if valid_results:
        best_model = max(valid_results.keys(), key=lambda k: valid_results[k]['roi'])
        print(f"\n🏆 Best Model by ROI: {best_model}")
        print(f"   ROI: {valid_results[best_model]['roi']:.1f}%")
        print(f"   Win Rate: {valid_results[best_model]['win_rate']:.3f}")
        print(f"   Total Bets: {valid_results[best_model]['total_bets']}")
    
    print(f"\n✅ All models trained and saved!")
    print("Available models:")
    for name in models.keys():
        print(f"  - {name}")

if __name__ == "__main__":
    train_all_models()
