"""
Model Performance Monitoring System
Tracks model performance over time and detects degradation
"""
import pandas as pd
import numpy as np
import joblib
import json
from datetime import datetime, timedelta
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

class ModelMonitor:
    def __init__(self):
        self.monitoring_data = []
        self.performance_thresholds = {
            'min_roi': 20.0,  # Minimum acceptable ROI
            'min_win_rate': 0.55,  # Minimum acceptable win rate
            'max_accuracy_drop': 0.05,  # Maximum acceptable accuracy drop
            'min_bets_per_week': 10  # Minimum bets per week
        }
    
    def get_database_connection(self):
        """Get database connection"""
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL not found in environment variables")
        
        if database_url.startswith('postgresql://'):
            database_url = database_url.replace('postgresql://', 'postgresql+psycopg2://')
        
        return create_engine(database_url)
    
    def load_model_metadata(self, model_path='model_metadata_optimized.json'):
        """Load model metadata"""
        try:
            with open(model_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Model metadata not found: {model_path}")
            return None
    
    def get_recent_games(self, days=7):
        """Get recent games for monitoring"""
        try:
            engine = self.get_database_connection()
            
            # Get games from last N days
            query = """
            SELECT 
                g.id,
                g."gameDate",
                g.season,
                g."seasonType",
                g."homeTeamId",
                g."awayTeamId",
                g."homeScore",
                g."awayScore",
                g.spread,
                g.total,
                g."whosFavored",
                g."idSpread",
                ht.abbreviation as home_team_abbr,
                at.abbreviation as away_team_abbr
            FROM games g
            JOIN teams ht ON g."homeTeamId" = ht.id
            JOIN teams at ON g."awayTeamId" = at.id
            WHERE g."gameDate" >= %(start_date)s
            AND g."homeScore" IS NOT NULL
            AND g."awayScore" IS NOT NULL
            AND g.spread IS NOT NULL
            ORDER BY g."gameDate" DESC
            """
            
            start_date = datetime.now() - timedelta(days=days)
            
            df = pd.read_sql(query, engine, params={'start_date': start_date})
            return df
            
        except Exception as e:
            print(f"❌ Error fetching recent games: {e}")
            return pd.DataFrame()
    
    def calculate_model_performance(self, model_name, recent_games):
        """Calculate current model performance"""
        try:
            # Load model and scaler
            model = joblib.load(f'models/model_{model_name.lower().replace(" ", "_")}.pkl')
            scaler = joblib.load(f'models/scaler_{model_name.lower().replace(" ", "_")}.pkl')
            
            if recent_games.empty:
                return None
            
            # Generate features (simplified version)
            features = self.generate_monitoring_features(recent_games)
            
            if features is None or features.empty:
                return None
            
            # Prepare features for prediction
            feature_cols = [col for col in features.columns if col not in ['game_id', 'game_date', 'id_spread']]
            X = features[feature_cols].fillna(0)
            y_true = features['id_spread'].fillna(0)
            
            # Remove push games
            non_push_mask = y_true != 2
            X_clean = X[non_push_mask]
            y_true_clean = y_true[non_push_mask]
            
            if len(X_clean) == 0:
                return None
            
            # Scale features
            X_scaled = scaler.transform(X_clean)
            
            # Make predictions
            y_pred = model.predict(X_scaled)
            y_proba = model.predict_proba(X_scaled)
            
            # Calculate metrics
            accuracy = np.mean(y_true_clean == y_pred)
            confidence_scores = np.max(y_proba, axis=1)
            
            # High-confidence predictions
            high_conf_mask = confidence_scores >= 0.6
            if np.any(high_conf_mask):
                y_true_high = y_true_clean[high_conf_mask]
                y_pred_high = y_pred[high_conf_mask]
                
                win_rate = np.mean(y_true_high == y_pred_high)
                total_bets = len(y_true_high)
                profitable_bets = np.sum(y_true_high == y_pred_high)
                roi = ((profitable_bets * 2) - total_bets) / total_bets * 100 if total_bets > 0 else 0
            else:
                win_rate = 0
                total_bets = 0
                profitable_bets = 0
                roi = 0
            
            return {
                'model_name': model_name,
                'timestamp': datetime.now().isoformat(),
                'total_games': len(recent_games),
                'accuracy': float(accuracy),
                'win_rate': float(win_rate),
                'roi': float(roi),
                'total_bets': int(total_bets),
                'profitable_bets': int(profitable_bets),
                'avg_confidence': float(np.mean(confidence_scores)) if len(confidence_scores) > 0 else 0
            }
            
        except Exception as e:
            print(f"❌ Error calculating performance for {model_name}: {e}")
            return None
    
    def generate_monitoring_features(self, games_df):
        """Generate simplified features for monitoring"""
        try:
            features_list = []
            
            for _, game in games_df.iterrows():
                # Simplified feature generation for monitoring
                features = {
                    'game_id': game['id'],
                    'game_date': game['gameDate'],
                    'spread': game['spread'] or 0,
                    'total': game['total'] or 0,
                    'is_playoffs': game['seasonType'] == 'Playoffs',
                    'is_regular_season': game['seasonType'] == 'Regular Season',
                    'spread_magnitude': abs(game['spread'] or 0),
                    'is_home_favorite': game['whosFavored'] == 'home',
                    'is_away_favorite': game['whosFavored'] == 'away',
                    'id_spread': game['idSpread']
                }
                
                # Add more features as needed for monitoring
                features_list.append(features)
            
            return pd.DataFrame(features_list)
            
        except Exception as e:
            print(f"❌ Error generating monitoring features: {e}")
            return None
    
    def check_model_health(self, performance_data):
        """Check if model performance meets thresholds"""
        if not performance_data:
            return False, "No performance data available"
        
        issues = []
        
        # Check ROI
        if performance_data['roi'] < self.performance_thresholds['min_roi']:
            issues.append(f"ROI too low: {performance_data['roi']:.1f}% < {self.performance_thresholds['min_roi']}%")
        
        # Check win rate
        if performance_data['win_rate'] < self.performance_thresholds['min_win_rate']:
            issues.append(f"Win rate too low: {performance_data['win_rate']:.3f} < {self.performance_thresholds['min_win_rate']}")
        
        # Check bet frequency
        if performance_data['total_bets'] < self.performance_thresholds['min_bets_per_week']:
            issues.append(f"Too few bets: {performance_data['total_bets']} < {self.performance_thresholds['min_bets_per_week']}")
        
        is_healthy = len(issues) == 0
        message = "Model is healthy" if is_healthy else "; ".join(issues)
        
        return is_healthy, message
    
    def monitor_all_models(self, days=7):
        """Monitor all available models"""
        print(f"🔍 Monitoring models for last {days} days...")
        
        # Get recent games
        recent_games = self.get_recent_games(days)
        
        if recent_games.empty:
            print("❌ No recent games found for monitoring")
            return
        
        print(f"📊 Found {len(recent_games)} recent games")
        
        # Available models
        model_files = [f for f in os.listdir('models') if f.startswith('model_') and f.endswith('.pkl')]
        model_names = [f.replace('model_', '').replace('.pkl', '').replace('_', ' ').title() for f in model_files]
        
        monitoring_results = []
        
        for model_name in model_names:
            print(f"\n🔍 Monitoring {model_name}...")
            
            performance = self.calculate_model_performance(model_name, recent_games)
            
            if performance:
                is_healthy, health_message = self.check_model_health(performance)
                performance['is_healthy'] = is_healthy
                performance['health_message'] = health_message
                
                monitoring_results.append(performance)
                
                status = "✅" if is_healthy else "❌"
                print(f"  {status} {health_message}")
                print(f"  📊 ROI: {performance['roi']:.1f}%, Win Rate: {performance['win_rate']:.3f}, Bets: {performance['total_bets']}")
            else:
                print(f"  ❌ Failed to calculate performance")
        
        # Save monitoring results
        self.save_monitoring_results(monitoring_results)
        
        return monitoring_results
    
    def save_monitoring_results(self, results):
        """Save monitoring results to file"""
        try:
            monitoring_file = 'model_monitoring_results.json'
            
            # Load existing results
            if os.path.exists(monitoring_file):
                with open(monitoring_file, 'r') as f:
                    all_results = json.load(f)
            else:
                all_results = []
            
            # Add new results
            all_results.extend(results)
            
            # Keep only last 30 days of results
            cutoff_date = datetime.now() - timedelta(days=30)
            all_results = [r for r in all_results if datetime.fromisoformat(r['timestamp']) > cutoff_date]
            
            # Save updated results
            with open(monitoring_file, 'w') as f:
                json.dump(all_results, f, indent=2)
            
            print(f"💾 Monitoring results saved to {monitoring_file}")
            
        except Exception as e:
            print(f"❌ Error saving monitoring results: {e}")
    
    def generate_monitoring_report(self):
        """Generate a monitoring report"""
        try:
            with open('model_monitoring_results.json', 'r') as f:
                results = json.load(f)
            
            if not results:
                print("❌ No monitoring data available")
                return
            
            print("\n📊 MODEL MONITORING REPORT")
            print("=" * 60)
            
            # Group by model
            model_stats = {}
            for result in results:
                model = result['model_name']
                if model not in model_stats:
                    model_stats[model] = []
                model_stats[model].append(result)
            
            for model, data in model_stats.items():
                if not data:
                    continue
                
                # Calculate averages
                avg_roi = np.mean([d['roi'] for d in data])
                avg_win_rate = np.mean([d['win_rate'] for d in data])
                avg_accuracy = np.mean([d['accuracy'] for d in data])
                total_bets = sum([d['total_bets'] for d in data])
                healthy_checks = sum([1 for d in data if d.get('is_healthy', False)])
                total_checks = len(data)
                
                health_percentage = (healthy_checks / total_checks * 100) if total_checks > 0 else 0
                
                print(f"\n🤖 {model}")
                print(f"  📈 Avg ROI: {avg_roi:.1f}%")
                print(f"  🎯 Avg Win Rate: {avg_win_rate:.3f}")
                print(f"  📊 Avg Accuracy: {avg_accuracy:.3f}")
                print(f"  💰 Total Bets: {total_bets}")
                print(f"  ✅ Health: {health_percentage:.1f}% ({healthy_checks}/{total_checks})")
                
                # Recent performance
                recent_data = data[-1] if data else None
                if recent_data:
                    status = "✅" if recent_data.get('is_healthy', False) else "❌"
                    print(f"  🔍 Latest: {status} {recent_data.get('health_message', 'Unknown')}")
            
        except FileNotFoundError:
            print("❌ No monitoring data found. Run monitoring first.")
        except Exception as e:
            print(f"❌ Error generating report: {e}")

def main():
    """Main monitoring function"""
    monitor = ModelMonitor()
    
    print("🚀 NBA Betting Model Monitoring System")
    print("=" * 50)
    
    # Monitor all models
    results = monitor.monitor_all_models(days=7)
    
    # Generate report
    monitor.generate_monitoring_report()
    
    print("\n✅ Monitoring complete!")

if __name__ == "__main__":
    main()
