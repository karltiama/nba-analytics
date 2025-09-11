# NBA Betting Analytics

A comprehensive NBA betting prediction system using machine learning to analyze historical data and identify profitable betting opportunities.

## 🏀 Features

- **ML Model Testing Dashboard** - Test and compare 10 different machine learning models
- **Real-time Backtesting** - Validate model performance on historical data
- **Data Quality Dashboard** - Explore and verify NBA data integrity
- **Interactive Tables** - Browse games, teams, and player statistics
- **Performance Analytics** - Track ROI, win rates, and betting metrics

## 🚀 Quick Start

### 1. Install Dependencies
```bash
# Frontend dependencies
npm install

# Python dependencies
pip install -r requirements.txt
```

### 2. Set up Database
```bash
# Generate Prisma client
npm run db:generate

# Push schema to database
npm run db:push
```

### 3. Generate ML Features
```bash
# Create ML features dataset (10,000 games)
python scripts/create_ml_features_sample.py
```

### 4. Train Models
```bash
# Train all 10 ML models
python scripts/train_all_models.py
```

### 5. Start Development Server
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to see the dashboard.

## 📁 Project Structure

```
├── app/                    # Next.js frontend
│   ├── api/               # API routes
│   ├── backtest-dashboard/ # Model testing interface
│   ├── data-tables/       # Data exploration
│   └── predictions/       # Prediction interface
├── components/            # React components
│   └── ui/               # shadcn/ui components
├── scripts/              # Python ML scripts
│   ├── train_all_models.py
│   ├── backtest_any_model.py
│   └── create_ml_features_sample.py
├── models/               # Trained ML models
│   ├── model_*.pkl
│   └── scaler_*.pkl
├── data/                 # Raw CSV data
└── data_import/          # Database import scripts
```

## 🤖 Available Models

| Model | ROI | Win Rate | Best For |
|-------|-----|----------|----------|
| **Logistic Regression** | **49.9%** | **78.5%** | High precision betting |
| **Random Forest** | 42.4% | 74.6% | Balanced performance |
| **Decision Tree** | 41.2% | 73.9% | Interpretable results |
| **Extra Trees** | 35.9% | 71.2% | Ensemble methods |
| **XGBoost** | 25.9% | 66.0% | Gradient boosting |
| **Gradient Boosting** | 24.2% | 65.1% | Many betting opportunities |
| **SVM** | 16.7% | 61.2% | Complex patterns |
| **Naive Bayes** | 13.8% | 59.6% | Baseline comparison |
| **Neural Network** | 11.6% | 58.4% | Deep learning |
| **K-Nearest Neighbors** | 10.7% | 58.0% | Simple baseline |

## 🎯 Usage

### Model Testing
1. Navigate to `/backtest-dashboard`
2. Select a model from the dropdown
3. Click "Run Backtest" to see performance metrics
4. Compare models using the performance table

### Data Exploration
1. Go to `/data-tables` to explore raw data
2. Use filters and sorting to analyze specific datasets
3. Verify data quality and completeness

### Running Backtests
```bash
# Test specific model
python scripts/backtest_any_model.py "Logistic Regression"

# Test all models
python scripts/train_all_models.py
```

## 🛠️ Tech Stack

- **Frontend**: Next.js 15, React, TypeScript, Tailwind CSS
- **Backend**: Next.js API routes, Prisma ORM
- **ML**: Python, scikit-learn, XGBoost, pandas
- **Database**: Supabase PostgreSQL
- **UI Components**: shadcn/ui, Radix UI
- **Charts**: Recharts

## 📊 Performance

The best performing model (Logistic Regression) achieves:
- **49.9% ROI** on high-confidence bets
- **78.5% win rate** with 0.6+ confidence threshold
- **600 total bets** from 2,515 test games
- **57.4% overall accuracy**

## 🔧 Development

### Adding New Models
1. Add model to `scripts/train_all_models.py`
2. Update model mapping in `app/api/backtest/route.ts`
3. Test using the dashboard interface

### Database Schema
The system uses a normalized database schema with tables for:
- `games` - NBA game results and betting lines
- `teams` - Team information and metadata
- `players` - Player statistics and career data
- `betting_odds` - Historical and current betting lines

## 📝 License

This project is for educational and research purposes.

