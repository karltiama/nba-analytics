"""
Comprehensive Model Management Dashboard
Provides overview of all models, performance, and management tools
"""
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
import joblib

class ModelManagementDashboard:
    def __init__(self):
        self.models_dir = 'models'
        self.monitoring_file = 'model_monitoring_results.json'
        self.retraining_log = 'retraining_log.json'
    
    def get_model_summary(self):
        """Get summary of all available models"""
        try:
            model_files = [f for f in os.listdir(self.models_dir) if f.startswith('model_') and f.endswith('.pkl')]
            model_names = [f.replace('model_', '').replace('.pkl', '').replace('_', ' ').title() for f in model_files]
            
            summary = []
            for model_name in model_names:
                model_info = {
                    'name': model_name,
                    'file': f'model_{model_name.lower().replace(" ", "_")}.pkl',
                    'scaler_file': f'scaler_{model_name.lower().replace(" ", "_")}.pkl',
                    'exists': os.path.exists(os.path.join(self.models_dir, f'model_{model_name.lower().replace(" ", "_")}.pkl')),
                    'scaler_exists': os.path.exists(os.path.join(self.models_dir, f'scaler_{model_name.lower().replace(" ", "_")}.pkl')),
                    'size_mb': self.get_file_size(f'model_{model_name.lower().replace(" ", "_")}.pkl'),
                    'last_modified': self.get_file_modified_time(f'model_{model_name.lower().replace(" ", "_")}.pkl')
                }
                summary.append(model_info)
            
            return summary
            
        except Exception as e:
            print(f"❌ Error getting model summary: {e}")
            return []
    
    def get_file_size(self, filename):
        """Get file size in MB"""
        try:
            filepath = os.path.join(self.models_dir, filename)
            if os.path.exists(filepath):
                size_bytes = os.path.getsize(filepath)
                return round(size_bytes / (1024 * 1024), 2)
            return 0
        except:
            return 0
    
    def get_file_modified_time(self, filename):
        """Get file modification time"""
        try:
            filepath = os.path.join(self.models_dir, filename)
            if os.path.exists(filepath):
                timestamp = os.path.getmtime(filepath)
                return datetime.fromtimestamp(timestamp).isoformat()
            return None
        except:
            return None
    
    def get_performance_summary(self):
        """Get performance summary from monitoring data"""
        try:
            if not os.path.exists(self.monitoring_file):
                return {}
            
            with open(self.monitoring_file, 'r') as f:
                monitoring_data = json.load(f)
            
            if not monitoring_data:
                return {}
            
            # Group by model
            model_performance = {}
            for entry in monitoring_data:
                model = entry.get('model_name', 'Unknown')
                if model not in model_performance:
                    model_performance[model] = []
                model_performance[model].append(entry)
            
            # Calculate summary stats
            summary = {}
            for model, data in model_performance.items():
                if not data:
                    continue
                
                # Get latest performance
                latest = max(data, key=lambda x: x['timestamp'])
                
                # Calculate averages
                avg_roi = np.mean([d.get('roi', 0) for d in data])
                avg_win_rate = np.mean([d.get('win_rate', 0) for d in data])
                avg_accuracy = np.mean([d.get('accuracy', 0) for d in data])
                total_bets = sum([d.get('total_bets', 0) for d in data])
                
                # Health status
                healthy_checks = sum([1 for d in data if d.get('is_healthy', False)])
                health_percentage = (healthy_checks / len(data) * 100) if data else 0
                
                summary[model] = {
                    'latest': latest,
                    'avg_roi': round(avg_roi, 1),
                    'avg_win_rate': round(avg_win_rate, 3),
                    'avg_accuracy': round(avg_accuracy, 3),
                    'total_bets': total_bets,
                    'health_percentage': round(health_percentage, 1),
                    'data_points': len(data)
                }
            
            return summary
            
        except Exception as e:
            print(f"❌ Error getting performance summary: {e}")
            return {}
    
    def get_retraining_summary(self):
        """Get retraining summary"""
        try:
            if not os.path.exists(self.retraining_log):
                return []
            
            with open(self.retraining_log, 'r') as f:
                log_data = json.load(f)
            
            # Get last 10 retraining events
            recent_logs = sorted(log_data, key=lambda x: x['timestamp'], reverse=True)[:10]
            
            return recent_logs
            
        except Exception as e:
            print(f"❌ Error getting retraining summary: {e}")
            return []
    
    def display_dashboard(self):
        """Display comprehensive dashboard"""
        print("🏀 NBA BETTING MODEL MANAGEMENT DASHBOARD")
        print("=" * 60)
        print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Model Summary
        print("📊 MODEL SUMMARY")
        print("-" * 40)
        model_summary = self.get_model_summary()
        
        if model_summary:
            print(f"{'Model':<20} {'Status':<8} {'Size (MB)':<10} {'Last Modified':<20}")
            print("-" * 70)
            
            for model in model_summary:
                status = "✅" if model['exists'] and model['scaler_exists'] else "❌"
                size = f"{model['size_mb']:.1f}" if model['size_mb'] > 0 else "N/A"
                modified = model['last_modified'][:16] if model['last_modified'] else "N/A"
                
                print(f"{model['name']:<20} {status:<8} {size:<10} {modified:<20}")
        else:
            print("❌ No models found")
        
        print()
        
        # Performance Summary
        print("📈 PERFORMANCE SUMMARY")
        print("-" * 40)
        performance_summary = self.get_performance_summary()
        
        if performance_summary:
            print(f"{'Model':<20} {'Avg ROI':<10} {'Win Rate':<10} {'Accuracy':<10} {'Health':<10}")
            print("-" * 70)
            
            for model, perf in performance_summary.items():
                roi = f"{perf['avg_roi']:.1f}%"
                win_rate = f"{perf['avg_win_rate']:.3f}"
                accuracy = f"{perf['avg_accuracy']:.3f}"
                health = f"{perf['health_percentage']:.1f}%"
                
                print(f"{model:<20} {roi:<10} {win_rate:<10} {accuracy:<10} {health:<10}")
        else:
            print("❌ No performance data available")
        
        print()
        
        # Retraining Summary
        print("🔄 RETRAINING SUMMARY")
        print("-" * 40)
        retraining_summary = self.get_retraining_summary()
        
        if retraining_summary:
            print(f"{'Date':<20} {'Model':<20} {'Status':<10} {'Reason':<20}")
            print("-" * 70)
            
            for log in retraining_summary:
                date = log['timestamp'][:16]
                model = log.get('model_name', 'Unknown')
                status = log.get('status', 'Unknown')
                reason = log.get('reason', log.get('error', 'Unknown'))[:20]
                
                print(f"{date:<20} {model:<20} {status:<10} {reason:<20}")
        else:
            print("❌ No retraining data available")
        
        print()
        
        # Recommendations
        print("💡 RECOMMENDATIONS")
        print("-" * 40)
        self.display_recommendations()
    
    def display_recommendations(self):
        """Display recommendations based on current state"""
        recommendations = []
        
        # Check model health
        performance_summary = self.get_performance_summary()
        
        for model, perf in performance_summary.items():
            if perf['avg_roi'] < 20:
                recommendations.append(f"⚠️  {model}: Low ROI ({perf['avg_roi']:.1f}%) - Consider retraining")
            
            if perf['health_percentage'] < 70:
                recommendations.append(f"⚠️  {model}: Poor health ({perf['health_percentage']:.1f}%) - Monitor closely")
            
            if perf['total_bets'] < 50:
                recommendations.append(f"⚠️  {model}: Low betting activity ({perf['total_bets']} bets) - Check confidence thresholds")
        
        # Check for missing models
        model_summary = self.get_model_summary()
        missing_models = [m for m in model_summary if not m['exists'] or not m['scaler_exists']]
        
        if missing_models:
            recommendations.append(f"❌ Missing models: {', '.join([m['name'] for m in missing_models])}")
        
        # Check retraining frequency
        retraining_summary = self.get_retraining_summary()
        if retraining_summary:
            last_retrain = retraining_summary[0]
            last_retrain_date = datetime.fromisoformat(last_retrain['timestamp'])
            days_since_retrain = (datetime.now() - last_retrain_date).days
            
            if days_since_retrain > 7:
                recommendations.append(f"⏰ Last retraining was {days_since_retrain} days ago - Consider retraining")
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec}")
        else:
            print("✅ All models are performing well!")
    
    def export_report(self, filename=None):
        """Export dashboard report to file"""
        try:
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'model_dashboard_report_{timestamp}.txt'
            
            # Redirect print output to file
            import sys
            from io import StringIO
            
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            
            self.display_dashboard()
            
            report_content = sys.stdout.getvalue()
            sys.stdout = old_stdout
            
            # Save to file
            with open(filename, 'w') as f:
                f.write(report_content)
            
            print(f"📄 Dashboard report exported to: {filename}")
            
        except Exception as e:
            print(f"❌ Error exporting report: {e}")

def main():
    """Main dashboard function"""
    dashboard = ModelManagementDashboard()
    
    # Check command line arguments
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'export':
        dashboard.export_report()
    else:
        dashboard.display_dashboard()

if __name__ == "__main__":
    main()
