"""
Automated Model Retraining Pipeline
Handles scheduled retraining and model updates
"""
import pandas as pd
import numpy as np
import joblib
import json
import os
import shutil
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from dotenv import load_dotenv
import subprocess
import sys

load_dotenv()

class RetrainingPipeline:
    def __init__(self):
        self.backup_dir = 'model_backups'
        self.retraining_log = 'retraining_log.json'
        self.performance_thresholds = {
            'min_roi': 15.0,  # Minimum ROI to trigger retraining
            'min_win_rate': 0.50,  # Minimum win rate
            'max_accuracy_drop': 0.10,  # Maximum accuracy drop
            'retraining_frequency_days': 7  # Retrain every 7 days
        }
    
    def get_database_connection(self):
        """Get database connection"""
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL not found in environment variables")
        
        if database_url.startswith('postgresql://'):
            database_url = database_url.replace('postgresql://', 'postgresql+psycopg2://')
        
        return create_engine(database_url)
    
    def create_backup(self, model_name):
        """Create backup of current model"""
        try:
            if not os.path.exists(self.backup_dir):
                os.makedirs(self.backup_dir)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(self.backup_dir, f"{model_name}_{timestamp}")
            os.makedirs(backup_path, exist_ok=True)
            
            # Backup model files
            model_files = [
                f'models/model_{model_name.lower().replace(" ", "_")}.pkl',
                f'models/scaler_{model_name.lower().replace(" ", "_")}.pkl',
                'model_metadata_optimized.json'
            ]
            
            for file_path in model_files:
                if os.path.exists(file_path):
                    filename = os.path.basename(file_path)
                    shutil.copy2(file_path, os.path.join(backup_path, filename))
            
            print(f"💾 Backup created: {backup_path}")
            return backup_path
            
        except Exception as e:
            print(f"❌ Error creating backup: {e}")
            return None
    
    def load_retraining_log(self):
        """Load retraining log"""
        try:
            if os.path.exists(self.retraining_log):
                with open(self.retraining_log, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"❌ Error loading retraining log: {e}")
            return []
    
    def save_retraining_log(self, log_data):
        """Save retraining log"""
        try:
            with open(self.retraining_log, 'w') as f:
                json.dump(log_data, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving retraining log: {e}")
    
    def should_retrain(self, model_name):
        """Check if model should be retrained"""
        try:
            log_data = self.load_retraining_log()
            
            # Check if model was retrained recently
            model_logs = [log for log in log_data if log.get('model_name') == model_name]
            if model_logs:
                last_retrain = max(model_logs, key=lambda x: x['timestamp'])
                last_retrain_date = datetime.fromisoformat(last_retrain['timestamp'])
                
                if datetime.now() - last_retrain_date < timedelta(days=self.performance_thresholds['retraining_frequency_days']):
                    print(f"⏰ {model_name} was retrained recently, skipping...")
                    return False, "Retrained recently"
            
            # Check model performance
            performance = self.check_model_performance(model_name)
            if not performance:
                return True, "No performance data available"
            
            # Check if performance is below thresholds
            if performance['roi'] < self.performance_thresholds['min_roi']:
                return True, f"ROI too low: {performance['roi']:.1f}%"
            
            if performance['win_rate'] < self.performance_thresholds['min_win_rate']:
                return True, f"Win rate too low: {performance['win_rate']:.3f}"
            
            return False, "Performance is acceptable"
            
        except Exception as e:
            print(f"❌ Error checking retraining need: {e}")
            return True, f"Error: {e}"
    
    def check_model_performance(self, model_name):
        """Check current model performance"""
        try:
            # Load monitoring results
            if os.path.exists('model_monitoring_results.json'):
                with open('model_monitoring_results.json', 'r') as f:
                    monitoring_data = json.load(f)
                
                # Get latest performance for this model
                model_data = [d for d in monitoring_data if d.get('model_name') == model_name]
                if model_data:
                    latest = max(model_data, key=lambda x: x['timestamp'])
                    return {
                        'roi': latest.get('roi', 0),
                        'win_rate': latest.get('win_rate', 0),
                        'accuracy': latest.get('accuracy', 0),
                        'total_bets': latest.get('total_bets', 0)
                    }
            
            return None
            
        except Exception as e:
            print(f"❌ Error checking performance: {e}")
            return None
    
    def retrain_model(self, model_name):
        """Retrain a specific model"""
        try:
            print(f"🔄 Retraining {model_name}...")
            
            # Create backup
            backup_path = self.create_backup(model_name)
            if not backup_path:
                print("❌ Failed to create backup, aborting retraining")
                return False
            
            # Run retraining script
            print("📊 Running retraining script...")
            result = subprocess.run([
                sys.executable, 'scripts/optimized_model_training.py'
            ], capture_output=True, text=True, cwd=os.getcwd())
            
            if result.returncode != 0:
                print(f"❌ Retraining failed: {result.stderr}")
                return False
            
            print("✅ Retraining completed successfully")
            
            # Log retraining
            log_data = self.load_retraining_log()
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'model_name': model_name,
                'backup_path': backup_path,
                'status': 'success',
                'reason': 'Scheduled retraining'
            }
            log_data.append(log_entry)
            self.save_retraining_log(log_data)
            
            return True
            
        except Exception as e:
            print(f"❌ Error retraining {model_name}: {e}")
            
            # Log failure
            log_data = self.load_retraining_log()
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'model_name': model_name,
                'status': 'failed',
                'error': str(e)
            }
            log_data.append(log_entry)
            self.save_retraining_log(log_data)
            
            return False
    
    def retrain_all_models(self):
        """Retrain all models that need it"""
        print("🚀 Starting Automated Retraining Pipeline")
        print("=" * 50)
        
        # Get available models
        model_files = [f for f in os.listdir('models') if f.startswith('model_') and f.endswith('.pkl')]
        model_names = [f.replace('model_', '').replace('.pkl', '').replace('_', ' ').title() for f in model_files]
        
        retrained_models = []
        skipped_models = []
        
        for model_name in model_names:
            print(f"\n🔍 Checking {model_name}...")
            
            should_retrain, reason = self.should_retrain(model_name)
            
            if should_retrain:
                print(f"  📈 Reason: {reason}")
                if self.retrain_model(model_name):
                    retrained_models.append(model_name)
                else:
                    print(f"  ❌ Failed to retrain {model_name}")
            else:
                print(f"  ⏭️  Skipping: {reason}")
                skipped_models.append(model_name)
        
        # Summary
        print(f"\n📊 RETRAINING SUMMARY")
        print("=" * 30)
        print(f"✅ Retrained: {len(retrained_models)} models")
        print(f"⏭️  Skipped: {len(skipped_models)} models")
        
        if retrained_models:
            print(f"\n🔄 Retrained Models:")
            for model in retrained_models:
                print(f"  - {model}")
        
        if skipped_models:
            print(f"\n⏭️  Skipped Models:")
            for model in skipped_models:
                print(f"  - {model}")
        
        return retrained_models, skipped_models
    
    def schedule_retraining(self):
        """Schedule retraining (can be called by cron job)"""
        try:
            print(f"⏰ Scheduled retraining at {datetime.now().isoformat()}")
            
            # Check if we should retrain based on schedule
            log_data = self.load_retraining_log()
            
            # Check if any model was retrained in the last 24 hours
            recent_retrains = []
            for log_entry in log_data:
                if log_entry.get('status') == 'success':
                    retrain_time = datetime.fromisoformat(log_entry['timestamp'])
                    if datetime.now() - retrain_time < timedelta(hours=24):
                        recent_retrains.append(log_entry['model_name'])
            
            if recent_retrains:
                print(f"⏭️  Recent retrains found, skipping scheduled retraining")
                return
            
            # Run retraining
            retrained, skipped = self.retrain_all_models()
            
            # Send notification (placeholder)
            if retrained:
                print(f"📧 Notification: {len(retrained)} models retrained")
            
        except Exception as e:
            print(f"❌ Error in scheduled retraining: {e}")
    
    def rollback_model(self, model_name, backup_timestamp=None):
        """Rollback model to previous version"""
        try:
            log_data = self.load_retraining_log()
            
            # Find backup
            model_logs = [log for log in log_data if log.get('model_name') == model_name and log.get('status') == 'success']
            
            if not model_logs:
                print(f"❌ No successful retraining found for {model_name}")
                return False
            
            # Use latest backup if no timestamp specified
            if not backup_timestamp:
                backup_log = max(model_logs, key=lambda x: x['timestamp'])
            else:
                backup_log = next((log for log in model_logs if backup_timestamp in log['timestamp']), None)
                if not backup_log:
                    print(f"❌ No backup found for timestamp {backup_timestamp}")
                    return False
            
            backup_path = backup_log['backup_path']
            
            if not os.path.exists(backup_path):
                print(f"❌ Backup path not found: {backup_path}")
                return False
            
            # Restore files
            model_files = [
                f'model_{model_name.lower().replace(" ", "_")}.pkl',
                f'scaler_{model_name.lower().replace(" ", "_")}.pkl',
                'model_metadata_optimized.json'
            ]
            
            for filename in model_files:
                backup_file = os.path.join(backup_path, filename)
                if os.path.exists(backup_file):
                    target_file = os.path.join('models', filename)
                    shutil.copy2(backup_file, target_file)
                    print(f"  ✅ Restored {filename}")
            
            print(f"🔄 Rollback completed for {model_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error rolling back {model_name}: {e}")
            return False

def main():
    """Main retraining function"""
    pipeline = RetrainingPipeline()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'retrain':
            pipeline.retrain_all_models()
        elif command == 'schedule':
            pipeline.schedule_retraining()
        elif command == 'rollback' and len(sys.argv) > 2:
            model_name = sys.argv[2]
            backup_timestamp = sys.argv[3] if len(sys.argv) > 3 else None
            pipeline.rollback_model(model_name, backup_timestamp)
        else:
            print("Usage: python retraining_pipeline.py [retrain|schedule|rollback <model_name> [timestamp]]")
    else:
        # Default: check and retrain if needed
        pipeline.retrain_all_models()

if __name__ == "__main__":
    main()
