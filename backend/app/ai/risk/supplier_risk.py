import numpy as np
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from ...models.database import Supplier, Order

class SupplierRiskPredictor:
    """Predicts risk of delivery delays and quality issues for suppliers"""
    
    def predict_risk(self, db: Session, supplier_id: int) -> Dict[str, Any]:
        """Calculate risk score for a supplier based on historical performance"""
        supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
        if not supplier:
            return {}
            
        # Get past orders
        orders = db.query(Order).filter(Order.supplier_id == supplier_id).all()
        
        if not orders:
            return {
                "supplier_name": supplier.name,
                "risk_score": 0.2, # Low baseline risk for new suppliers
                "risk_level": "Low",
                "factors": ["No historical data"]
            }
            
        # Calculate delay frequency
        # Note: Current schema doesn't have 'delivery_date' vs 'received_date' explicitly in simple form,
        # but we can infer from status and timestamps if available.
        # For this logic, we'll use a simulated classification based on dummy features.
        
        delay_count = 0
        total_orders = len(orders)
        
        # Simulated logic for "Million Dollar" demo
        # In a real system, we'd compare expected_delivery vs actual_delivery
        base_risk = 0.0
        factors = []
        
        # Factor 1: Performance Rating
        base_risk += (5 - supplier.rating) * 0.15
        if supplier.rating < 3:
            factors.append("Low supplier rating")
            
        # Factor 2: Order Volume
        if total_orders > 50:
            base_risk -= 0.05 # Experienced supplier
            
        # Final Score mapping
        risk_score = max(0.0, min(1.0, base_risk))
        risk_level = "High" if risk_score > 0.6 else "Medium" if risk_score > 0.3 else "Low"
        
        return {
            "supplier_id": supplier.id,
            "supplier_name": supplier.name,
            "risk_score": round(risk_score, 2),
            "risk_level": risk_level,
            "factors": factors or ["Consistent performance"]
        }

    def analyze_all_suppliers(self, db: Session) -> List[Dict[str, Any]]:
        """Analyze risk for all suppliers"""
        suppliers = db.query(Supplier).all()
        results = []
        for supplier in suppliers:
            results.append(self.predict_risk(db, supplier.id))
        
        # Sort by risk score descending
        return sorted(results, key=lambda x: x['risk_score'], reverse=True)

# Global instance
risk_predictor = SupplierRiskPredictor()
