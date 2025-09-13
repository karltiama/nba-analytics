"""
Deep Learning Models with Tensors for NBA Betting
Using TensorFlow/Keras for neural network approaches
"""
import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import json
from datetime import datetime

def create_deep_learning_models():
    """Create deep learning models using tensors"""
    
    print("🧠 Creating Deep Learning Models with Tensors...")
    print("=" * 60)
    
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
    
    print(f"After removing push games: {len(X_clean)} games")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X_clean, y_clean, test_size=0.3, random_state=42
    )
    
    print(f"Training set: {len(X_train)} games")
    print(f"Test set: {len(X_test)} games")
    
    # Scale features (important for neural networks)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Convert to tensors
    X_train_tensor = tf.convert_to_tensor(X_train_scaled, dtype=tf.float32)
    X_test_tensor = tf.convert_to_tensor(X_test_scaled, dtype=tf.float32)
    y_train_tensor = tf.convert_to_tensor(y_train.values, dtype=tf.float32)
    y_test_tensor = tf.convert_to_tensor(y_test.values, dtype=tf.float32)
    
    print(f"✅ Converted to tensors:")
    print(f"   X_train shape: {X_train_tensor.shape}")
    print(f"   y_train shape: {y_train_tensor.shape}")
    
    # Define models
    models = {
        'Simple Neural Network': create_simple_nn(len(feature_cols)),
        'Deep Neural Network': create_deep_nn(len(feature_cols)),
        'Wide Neural Network': create_wide_nn(len(feature_cols)),
        'LSTM Network': create_lstm_nn(len(feature_cols)),
        'CNN Network': create_cnn_nn(len(feature_cols))
    }
    
    results = {}
    
    print("\n🎯 Training Deep Learning Models...")
    print("=" * 60)
    
    for name, model in models.items():
        print(f"\nTraining {name}...")
        
        try:
            # Compile model
            model.compile(
                optimizer='adam',
                loss='binary_crossentropy',
                metrics=['accuracy']
            )
            
            # Train model
            history = model.fit(
                X_train_tensor, y_train_tensor,
                epochs=50,
                batch_size=32,
                validation_split=0.2,
                verbose=0
            )
            
            # Make predictions
            y_pred_proba = model.predict(X_test_tensor, verbose=0)
            y_pred = (y_pred_proba > 0.5).astype(int).flatten()
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            
            # Calculate betting metrics
            betting_metrics = calculate_betting_metrics_tensor(y_test, y_pred, y_pred_proba)
            
            results[name] = {
                'model': model,
                'accuracy': accuracy,
                'betting_metrics': betting_metrics,
                'history': history.history
            }
            
            print(f"  ✅ Accuracy: {accuracy:.3f}")
            print(f"  💰 ROI: {betting_metrics['roi']:.1f}%")
            print(f"  🎯 Win Rate: {betting_metrics['win_rate']:.3f}")
            print(f"  📊 High-Confidence Bets: {betting_metrics['total_bets']}")
            
            # Save model
            model_path = f"models/deep_learning_{name.lower().replace(' ', '_')}.h5"
            model.save(model_path)
            print(f"  💾 Saved as {model_path}")
            
        except Exception as e:
            print(f"  ❌ Error training {name}: {e}")
            continue
    
    # Find best model
    if results:
        best_model_name = max(results.keys(), key=lambda k: results[k]['betting_metrics']['roi'])
        best_model = results[best_model_name]
        
        print(f"\n🏆 BEST DEEP LEARNING MODEL: {best_model_name}")
        print(f"   ROI: {best_model['betting_metrics']['roi']:.1f}%")
        print(f"   Win Rate: {best_model['betting_metrics']['win_rate']:.3f}")
        print(f"   Accuracy: {best_model['accuracy']:.3f}")
        print(f"   Total Bets: {best_model['betting_metrics']['total_bets']}")
    
    # Save scaler
    joblib.dump(scaler, 'models/scaler_deep_learning.pkl')
    
    # Display comparison
    print(f"\n📊 DEEP LEARNING MODEL COMPARISON")
    print("=" * 80)
    print(f"{'Model':<25} {'Accuracy':<10} {'Win Rate':<10} {'ROI':<8} {'Bets':<8}")
    print("-" * 80)
    
    for name, result in results.items():
        metrics = result['betting_metrics']
        print(f"{name:<25} {result['accuracy']:<10.3f} {metrics['win_rate']:<10.3f} {metrics['roi']:<8.1f} {metrics['total_bets']:<8}")
    
    print("\n✅ Deep learning training complete!")
    return results

def create_simple_nn(input_dim):
    """Create a simple neural network"""
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(64, activation='relu', input_shape=(input_dim,)),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])
    return model

def create_deep_nn(input_dim):
    """Create a deep neural network"""
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(256, activation='relu', input_shape=(input_dim,)),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])
    return model

def create_wide_nn(input_dim):
    """Create a wide neural network"""
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(512, activation='relu', input_shape=(input_dim,)),
        tf.keras.layers.Dropout(0.4),
        tf.keras.layers.Dense(256, activation='relu'),
        tf.keras.layers.Dropout(0.4),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])
    return model

def create_lstm_nn(input_dim):
    """Create an LSTM network (for sequence data)"""
    model = tf.keras.Sequential([
        tf.keras.layers.Reshape((input_dim, 1), input_shape=(input_dim,)),
        tf.keras.layers.LSTM(64, return_sequences=True),
        tf.keras.layers.LSTM(32),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])
    return model

def create_cnn_nn(input_dim):
    """Create a CNN network (for spatial data)"""
    model = tf.keras.Sequential([
        tf.keras.layers.Reshape((input_dim, 1), input_shape=(input_dim,)),
        tf.keras.layers.Conv1D(64, 3, activation='relu'),
        tf.keras.layers.MaxPooling1D(2),
        tf.keras.layers.Conv1D(32, 3, activation='relu'),
        tf.keras.layers.GlobalMaxPooling1D(),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])
    return model

def calculate_betting_metrics_tensor(y_true, y_pred, y_proba, confidence_threshold=0.6):
    """Calculate betting metrics for tensor models"""
    
    # Get confidence scores
    confidence_scores = y_proba.flatten()
    
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
    create_deep_learning_models()

