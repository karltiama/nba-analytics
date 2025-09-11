# NBA Analytics Scripts

This directory contains all the Python scripts for machine learning model training and backtesting.

## Scripts Overview

### Model Training
- **`train_all_models.py`** - Trains all 10 ML models and saves them individually
- **`advanced_ml_models.py`** - Trains advanced models optimized for betting ROI
- **`create_ml_model.py`** - Creates basic ML models for comparison

### Data Processing
- **`create_ml_features_sample.py`** - Generates ML features from database data

### Model Testing
- **`backtest_any_model.py`** - Backtests any trained model with detailed results
- **`simple_backtest.py`** - Simple time-based backtest for model validation

## Usage

### Training Models
```bash
# Train all models
python scripts/train_all_models.py

# Train advanced models only
python scripts/advanced_ml_models.py

# Train basic models only
python scripts/create_ml_model.py
```

### Generating Features
```bash
# Generate ML features (default: 10,000 games)
python scripts/create_ml_features_sample.py

# Generate with custom sample size
python scripts/create_ml_features_sample.py 5000
```

### Running Backtests
```bash
# Backtest specific model
python scripts/backtest_any_model.py "Logistic Regression"
python scripts/backtest_any_model.py "Random Forest"
python scripts/backtest_any_model.py "XGBoost"

# Simple backtest
python scripts/simple_backtest.py advanced
python scripts/simple_backtest.py basic
```

## Model Files

All trained models and scalers are stored in the `../models/` directory:
- `model_*.pkl` - Trained model files
- `scaler_*.pkl` - Feature scaler files
- `model_metadata.json` - Model metadata and performance

## Available Models

1. **Logistic Regression** - Best ROI (49.9%)
2. **Random Forest** - Balanced performance (42.4% ROI)
3. **Decision Tree** - Simple, interpretable (41.2% ROI)
4. **Extra Trees** - Ensemble method (35.9% ROI)
5. **XGBoost** - Gradient boosting (25.9% ROI)
6. **Gradient Boosting** - Many bets (24.2% ROI)
7. **SVM** - Complex patterns (16.7% ROI)
8. **Naive Bayes** - Many bets, low ROI (13.8% ROI)
9. **Neural Network** - Overfitting issues (11.6% ROI)
10. **K-Nearest Neighbors** - Simple baseline (10.7% ROI)

## Dependencies

Make sure you have the required Python packages installed:
```bash
pip install -r requirements.txt
```

Required packages:
- pandas
- numpy
- scikit-learn
- xgboost
- joblib
- sqlalchemy
- psycopg2
