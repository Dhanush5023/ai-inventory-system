"""
Automated Scheduler for ML Predictions and Model Retraining
"""

import schedule
import time
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import Callable
import threading
import pandas as pd

from ...models.database import Sale, get_db, Alert, Product
from .prediction_service import PredictionService
from .model_trainer import DemandPredictor
from ...services.alert_service import AlertService


class MLScheduler:
    """Scheduler for automated ML tasks"""
    
    def __init__(self):
        self.prediction_service = PredictionService()
        self.predictor = DemandPredictor()
        self.is_running = False
        self.thread = None
    
    def daily_prediction_job(self):
        """Generate daily predictions for all products"""
        print(f"\n[{datetime.now()}] Running daily prediction job...")
        
        db = next(get_db())
        try:
            stats = self.prediction_service.generate_all_predictions(db, days_ahead=30)
            print(f"  ✓ Generated {stats['predictions_generated']} predictions")
            print(f"  ✓ Covered {stats['products_with_predictions']}/{stats['total_products']} products")
            
            # Generate alerts based on predictions
            alert_service = AlertService()
            alert_stats = alert_service.check_all_products(db)
            print(f"  ✓ Generated {alert_stats['alerts_generated']} alerts")
            
        except Exception as e:
            print(f"  ✗ Error in daily prediction job: {e}")
        finally:
            db.close()
    
    def weekly_retrain_job(self):
        """Retrain models weekly with latest data"""
        print(f"\n[{datetime.now()}] Running weekly model retraining job...")
        
        db = next(get_db())
        try:
            # Get all sales data
            query = db.query(Sale).order_by(Sale.sale_date.asc())
            
            sales_data = []
            for sale in query:
                sales_data.append({
                    'sale_date': sale.sale_date,
                    'quantity': sale.quantity,
                    'product_id': sale.product_id,
                    'unit_price': sale.unit_price
                })
            
            if len(sales_data) < 100:
                print("  ! Insufficient data for retraining (need at least 100 records)")
                return
            
            df = pd.DataFrame(sales_data)
            
            # Train models
            print("  → Training models...")
            metrics = self.predictor.train_all_models(df)
            
            print("  ✓ Model retraining complete!")
            for model_name, model_metrics in metrics.items():
                print(f"    - {model_name}: {model_metrics['accuracy']:.2f}% accuracy")
            
            # Reload models in prediction service
            self.prediction_service.predictor.load_models()
            self.prediction_service.model_metrics = metrics
            
        except Exception as e:
            print(f"  ✗ Error in weekly retrain job: {e}")
        finally:
            db.close()
    
    def hourly_alert_check(self):
        """Check for low stock alerts hourly"""
        print(f"\n[{datetime.now()}] Running hourly alert check...")
        
        db = next(get_db())
        try:
            alert_service = AlertService()
            stats = alert_service.check_all_products(db)
            
            if stats['alerts_generated'] > 0:
                print(f"  ⚠ Generated {stats['alerts_generated']} new alerts")
            else:
                print(f"  ✓ No new alerts needed")
            
        except Exception as e:
            print(f"  ✗ Error in hourly alert check: {e}")
        finally:
            db.close()
    
    def setup_schedule(self):
        """Setup all scheduled jobs"""
        # Daily predictions at 2 AM
        schedule.every().day.at("02:00").do(self.daily_prediction_job)
        
        # Weekly retraining on Sunday at 3 AM
        schedule.every().sunday.at("03:00").do(self.weekly_retrain_job)
        
        # Hourly alert checks
        schedule.every().hour.do(self.hourly_alert_check)
        
        # For testing: run jobs every minute (comment out in production)
        # schedule.every(1).minutes.do(self.daily_prediction_job)
        # schedule.every(5).minutes.do(self.hourly_alert_check)
        
        print("✓ Scheduler configured:")
        print("  - Daily predictions: 2:00 AM")
        print("  - Weekly retraining: Sunday 3:00 AM")
        print("  - Hourly alert checks")
    
    def run(self):
        """Run scheduler in background thread"""
        self.setup_schedule()
        self.is_running = True
        
        # Run pending jobs
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def start(self):
        """Start scheduler in background thread"""
        if self.thread and self.thread.is_alive():
            print("Scheduler is already running")
            return
        
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()
        print("✓ ML Scheduler started")
    
    def stop(self):
        """Stop scheduler"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("✓ ML Scheduler stopped")


# Global scheduler instance
ml_scheduler = MLScheduler()


def start_scheduler():
    """Start the ML scheduler"""
    ml_scheduler.start()


def stop_scheduler():
    """Stop  the ML scheduler"""
    ml_scheduler.stop()
