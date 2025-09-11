import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

def create_ml_model():
    """Create and test ML models for NBA betting predictions"""
    print("🤖 Creating ML models for NBA betting predictions...\n")
    
    try:
        # 1. Load the sample features
        print("📊 Loading sample features...")
        df = pd.read_csv('ml_features_sample.csv')
        print(f"Loaded {len(df)} games with {len(df.columns)} features")
        
        # 2. Prepare features and targets
        print("\n🔧 Preparing data for ML...")
        
        # Select feature columns (exclude non-numeric and target columns)
        exclude_cols = ['game_id', 'game_date', 'season', 'season_type', 'home_team_abbr', 'away_team_abbr', 
                       'id_spread', 'id_total', 'moneyline_home', 'moneyline_away']
        
        feature_cols = [col for col in df.columns if col not in exclude_cols]
        print(f"Using {len(feature_cols)} features: {feature_cols[:10]}...")
        
        # Prepare features and targets
        X = df[feature_cols].fillna(0)  # Fill NaN values with 0
        y_spread = df['id_spread'].fillna(0)  # 0=underdog covers, 1=favorite covers, 2=push
        
        # Remove push games (id_spread = 2) for binary classification
        non_push_mask = y_spread != 2
        X_clean = X[non_push_mask]
        y_clean = y_spread[non_push_mask]
        
        print(f"After removing push games: {len(X_clean)} games")
        print(f"Target distribution: {y_clean.value_counts().to_dict()}")
        
        # 3. Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_clean, y_clean, test_size=0.3, random_state=42, stratify=y_clean
        )
        
        print(f"Training set: {len(X_train)} games")
        print(f"Test set: {len(X_test)} games")
        
        # 4. Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # 5. Train multiple models
        models = {
            'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
            'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42)
        }
        
        results = {}
        
        print("\n🎯 Training models...")
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
            
            # Calculate accuracy
            accuracy = accuracy_score(y_test, y_pred)
            results[name] = {
                'model': model,
                'accuracy': accuracy,
                'predictions': y_pred,
                'probabilities': y_pred_proba
            }
            
            print(f"  Accuracy: {accuracy:.3f}")
            
            # Cross-validation
            if name == 'Logistic Regression':
                cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
            else:
                cv_scores = cross_val_score(model, X_train, y_train, cv=5)
            
            print(f"  CV Score: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
        
        # 6. Find best model
        best_model_name = max(results.keys(), key=lambda k: results[k]['accuracy'])
        best_model = results[best_model_name]
        
        print(f"\n🏆 Best Model: {best_model_name}")
        print(f"   Accuracy: {best_model['accuracy']:.3f}")
        
        # 7. Detailed evaluation
        print(f"\n📊 Detailed Evaluation for {best_model_name}:")
        print("\nClassification Report:")
        print(classification_report(y_test, best_model['predictions'], 
                                  target_names=['Underdog Covers', 'Favorite Covers']))
        
        print("\nConfusion Matrix:")
        cm = confusion_matrix(y_test, best_model['predictions'])
        print(cm)
        
        # 8. Feature importance (for tree-based models)
        if hasattr(best_model['model'], 'feature_importances_'):
            print(f"\n🔍 Top 10 Most Important Features:")
            feature_importance = pd.DataFrame({
                'feature': feature_cols,
                'importance': best_model['model'].feature_importances_
            }).sort_values('importance', ascending=False)
            
            for i, (_, row) in enumerate(feature_importance.head(10).iterrows()):
                print(f"  {i+1:2d}. {row['feature']:<25} {row['importance']:.3f}")
        
        # 9. Sample predictions
        print(f"\n🎲 Sample Predictions:")
        sample_indices = np.random.choice(len(X_test), 5, replace=False)
        
        for i, idx in enumerate(sample_indices):
            actual = y_test.iloc[idx]
            predicted = best_model['predictions'][idx]
            confidence = best_model['probabilities'][idx].max()
            
            actual_label = "Favorite Covers" if actual == 1 else "Underdog Covers"
            predicted_label = "Favorite Covers" if predicted == 1 else "Underdog Covers"
            
            print(f"  Game {i+1}: Actual={actual_label}, Predicted={predicted_label} (Confidence: {confidence:.3f})")
        
        # 10. Model performance summary
        print(f"\n📈 Model Performance Summary:")
        print(f"  Best Model: {best_model_name}")
        print(f"  Accuracy: {best_model['accuracy']:.3f}")
        print(f"  Baseline (always predict favorite): {y_test.mean():.3f}")
        print(f"  Improvement over baseline: {best_model['accuracy'] - y_test.mean():.3f}")
        
        # 11. Save the best model
        import joblib
        joblib.dump(best_model['model'], 'best_ml_model.pkl')
        joblib.dump(scaler, 'feature_scaler.pkl')
        print(f"\n💾 Model saved as 'best_ml_model.pkl'")
        print(f"💾 Scaler saved as 'feature_scaler.pkl'")
        
        return best_model, feature_cols
        
    except Exception as e:
        print(f"❌ Model creation failed: {e}")
        raise

if __name__ == "__main__":
    create_ml_model()
