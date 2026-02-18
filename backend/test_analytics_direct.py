from app.models.database import SessionLocal
from app.services.analytics_service import AnalyticsService
import time
import json
from datetime import datetime

def test_speed():
    db = SessionLocal()
    try:
        print("Benchmarking AnalyticsService.get_analytics_dashboard...")
        start = time.time()
        res = AnalyticsService.get_analytics_dashboard(db)
        end = time.time()
        print(f"Completed in {(end-start)*1000:.2f}ms")
        
        # Check one of the KPIs
        print(f"Total Products: {res.overview.kpis[0].value}")
        print(f"Revenue by month count: {len(res.financial_metrics.revenue_by_month)}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_speed()
