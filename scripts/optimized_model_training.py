"""
Optimized ML model training with improved hyperparameters and convergence
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV, TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, ExtraTreesClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import xgboost as xgb
import joblib
import json
from datetime import datetime

def optimized_model_training():
    """Train models with optimized hyperparameters and proper validation"""
    
    print("🚀 OPTIMIZED ML Model Training for NBA Betting Predictions...")
    print("=" * 70)
    
    # Load data
    print("📊 Loading features...")
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
    
    # Time-based split (more realistic for betting)
    split_idx = int(len(X_clean) * 0.7)
    X_train, X_test = X_clean.iloc[:split_idx], X_clean.iloc[split_idx:]
    y_train, y_test = y_clean.iloc[:split_idx], y_clean.iloc[split_idx:]
    
    print(f"Training set: {len(X_train)} games")
    print(f"Test set: {len(X_test)} games")
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Define optimized models with better hyperparameters
    models = {
        'Logistic Regression': LogisticRegression(
            random_state=42, 
            max_iter=5000,  # Increased iterations
            C=0.1,  # Regularization
            solver='lbfgs'
        ),
        'Random Forest': RandomForestClassifier(
            n_estimators=300,  # More trees
            max_depth=15,  # Deeper trees
            min_samples_split=10,
            min_samples_leaf=5,
            random_state=42,
            n_jobs=-1
        ),
        'Gradient Boosting': GradientBoostingClassifier(
            n_estimators=300,  # More estimators
            max_depth=8,  # Deeper
            learning_rate=0.05,  # Lower learning rate
            subsample=0.8,
            random_state=42
        ),
        'XGBoost': xgb.XGBClassifier(
            n_estimators=300,
            max_depth=8,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_alpha=0.1,  # L1 regularization
            reg_lambda=0.1,  # L2 regularization
            random_state=42,
            eval_metric='logloss',
            n_jobs=-1
        ),
        'Extra Trees': ExtraTreesClassifier(
            n_estimators=300,
            max_depth=15,
            min_samples_split=10,
            min_samples_leaf=5,
            random_state=42,
            n_jobs=-1
        ),
        'SVM': SVC(
            probability=True, 
            random_state=42,
            C=1.0,
            gamma='scale',
            kernel='rbf'
        ),
        'Neural Network': MLPClassifier(
            hidden_layer_sizes=(200, 100, 50),  # Deeper network
            max_iter=2000,  # More iterations
            learning_rate_init=0.001,
            alpha=0.01,  # L2 regularization
            random_state=42,
            early_stopping=True,
            validation_fraction=0.1
        ),
        'Naive Bayes': GaussianNB(),
        'Decision Tree': DecisionTreeClassifier(
            max_depth=15,
            min_samples_split=10,
            min_samples_leaf=5,
            random_state=42
        ),
        'K-Nearest Neighbors': KNeighborsClassifier(
            n_neighbors=7,  # Optimized k
            weights='distance',
            algorithm='auto'
        )
    }
    
    results = {}
    
    print("\n🎯 Training optimized models...")
    print("=" * 70)
    
    for name, model in models.items():
        print(f"\nTraining {name}...")
        
        try:
            # Use scaled data for models that need it
            if name in ['Logistic Regression', 'SVM', 'Neural Network', 'K-Nearest Neighbors']:
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_test_scaled)
                y_pred_proba = model.predict_proba(X_test_scaled)
            else:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                y_pred_proba = model.predict_proba(X_test)
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            
            # Calculate betting metrics
            betting_metrics = calculate_betting_metrics(y_test, y_pred, y_pred_proba, df_clean.iloc[split_idx:])
            
            results[name] = {
                'model': model,
                'accuracy': accuracy,
                'predictions': y_pred,
                'probabilities': y_pred_proba,
                'betting_metrics': betting_metrics
            }
            
            print(f"  ✅ Accuracy: {accuracy:.3f}")
            print(f"  💰 ROI: {betting_metrics['roi']:.1f}%")
            print(f"  🎯 Win Rate: {betting_metrics['win_rate']:.3f}")
            print(f"  📊 High-Confidence Bets: {betting_metrics['total_bets']}")
            
            # Save model and scaler
            model_filename = f"models/model_{name.lower().replace(' ', '_')}.pkl"
            scaler_filename = f"models/scaler_{name.lower().replace(' ', '_')}.pkl"
            
            joblib.dump(model, model_filename)
            joblib.dump(scaler, scaler_filename)
            
            print(f"  💾 Saved as {model_filename}")
            
        except Exception as e:
            print(f"  ❌ Error training {name}: {e}")
            continue
    
    # Find best model
    if results:
        best_model_name = max(results.keys(), key=lambda k: results[k]['betting_metrics']['roi'])
        best_model = results[best_model_name]
        
        print(f"\n🏆 BEST MODEL: {best_model_name}")
        print(f"   ROI: {best_model['betting_metrics']['roi']:.1f}%")
        print(f"   Win Rate: {best_model['betting_metrics']['win_rate']:.3f}")
        print(f"   Accuracy: {best_model['accuracy']:.3f}")
        print(f"   Total Bets: {best_model['betting_metrics']['total_bets']}")
        
        # Save best model as primary model
        joblib.dump(best_model['model'], 'best_optimized_model.pkl')
        joblib.dump(scaler, 'feature_scaler_optimized.pkl')
        
        # Save metadata
        metadata = {
            'model_name': best_model_name,
            'best_threshold': 0.6,
            'feature_columns': feature_cols,
            'performance': {
                'roi': float(best_model['betting_metrics']['roi']),
                'win_rate': float(best_model['betting_metrics']['win_rate']),
                'total_bets': int(best_model['betting_metrics']['total_bets']),
                'profitable_bets': int(best_model['betting_metrics']['profitable_bets']),
                'avg_confidence': float(best_model['betting_metrics']['avg_confidence'])
            },
            'training_date': datetime.now().isoformat(),
            'training_games': int(len(X_train)),
            'test_games': int(len(X_test))
        }
        
        with open('model_metadata_optimized.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\n💾 Best model saved as 'best_optimized_model.pkl'")
        print(f"📊 Metadata saved as 'model_metadata_optimized.json'")
    
    # Display comparison table
    print(f"\n📊 OPTIMIZED MODEL COMPARISON")
    print("=" * 80)
    print(f"{'Model':<20} {'Accuracy':<10} {'Win Rate':<10} {'ROI':<8} {'Bets':<8}")
    print("-" * 80)
    
    for name, result in results.items():
        metrics = result['betting_metrics']
        print(f"{name:<20} {result['accuracy']:<10.3f} {metrics['win_rate']:<10.3f} {metrics['roi']:<8.1f} {metrics['total_bets']:<8}")
    
    print("\n✅ Optimized training complete!")
    return results

def calculate_betting_metrics(y_true, y_pred, y_proba, df_test, confidence_threshold=0.6):
    """Calculate betting-specific metrics"""
    
    # Get confidence scores
    confidence_scores = np.max(y_proba, axis=1)
    
    # Filter high-confidence predictions
    high_conf_mask = confidence_scores >= confidence_threshold
    
    if not np.any(high_conf_mask):
        return {
            'roi': 0.0,
            'win_rate': 0.0,
            'total_bets': 0,
            'profitable_bets': 0,
            'avg_confidence': 0.0
        }
    
    # Get high-confidence predictions and actuals
    y_true_high = y_true[high_conf_mask]
    y_pred_high = y_pred[high_conf_mask]
    confidence_high = confidence_scores[high_conf_mask]
    
    # Calculate win rate
    wins = np.sum(y_true_high == y_pred_high)
    win_rate = wins / len(y_true_high) if len(y_true_high) > 0 else 0
    
    # Calculate ROI (simplified - assumes 1:1 betting)
    total_bets = len(y_true_high)
    profitable_bets = wins
    roi = ((profitable_bets * 2) - total_bets) / total_bets * 100 if total_bets > 0 else 0
    
    return {
        'roi': roi,
        'win_rate': win_rate,
        'total_bets': total_bets,
        'profitable_bets': profitable_bets,
        'avg_confidence': np.mean(confidence_high)
    }

if __name__ == "__main__":
    optimized_model_training()
