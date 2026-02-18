from sklearn.ensemble import IsolationForest
import pandas as pd
import numpy as np
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from ...models.database import Sale, Product

class AnomalyDetector:
    """Detects fraud, theft, or errors in sales and inventory data"""
    
    def __init__(self):
        self.model = IsolationForest(contamination=0.05, random_state=42)
        
    def detect_sales_anomalies(self, db: Session) -> List[Dict[str, Any]]:
        """Identify anomalous sales records using Isolation Forest"""
        sales = db.query(Sale).order_by(Sale.sale_date.desc()).limit(1000).all()
        if len(sales) < 50:
            return []
            
        data = [[s.quantity, s.unit_price, s.total_amount] for s in sales]
        df = pd.DataFrame(data, columns=['quantity', 'unit_price', 'total_amount'])
        
        # Fit and predict (-1 for anomaly, 1 for normal)
        self.model.fit(df)
        predictions = self.model.predict(df)
        
        anomalies = []
        for i, pred in enumerate(predictions):
            if pred == -1:
                sale = sales[i]
                anomalies.append({
                    "sale_id": sale.id,
                    "product_id": sale.product_id,
                    "date": sale.sale_date,
                    "quantity": sale.quantity,
                    "reason": "Unusual volume or price relationship detected"
                })
                
        return anomalies

# Global instance
anomaly_detector = AnomalyDetector()
