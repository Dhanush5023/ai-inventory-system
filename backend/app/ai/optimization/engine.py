import numpy as np
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from ...models.database import Product, Sale, Prediction
from ...core.config import settings

class OptimizationEngine:
    """Enterprise-grade inventory optimization using EOQ and Safety Stock formulas"""
    
    def calculate_eoq(self, annual_demand: float, order_cost: float, holding_cost_per_unit: float) -> float:
        """
        Economic Order Quantity (EOQ) Formula:
        EOQ = sqrt((2 * D * S) / H)
        D = Annual Demand, S = Order/Setup Cost, H = Holding/Carrying Cost per unit
        """
        if holding_cost_per_unit <= 0:
            return annual_demand / 12  # Fallback to monthly demand
            
        eoq = np.sqrt((2 * annual_demand * order_cost) / holding_cost_per_unit)
        return float(eoq)

    def calculate_safety_stock(self, demand_sd: float, lead_time_days: int, service_level_z: float = 1.645) -> float:
        """
        Safety Stock Formula:
        SS = Z * sqrt(Lead Time) * SD_demand
        Z = Service level factor (1.645 for 95%)
        """
        ss = service_level_z * np.sqrt(lead_time_days) * demand_sd
        return float(ss)

    def optimize_product(self, db: Session, product_id: int) -> Dict[str, Any]:
        """Generate optimization metrics for a specific product"""
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return {}

        # Get historical demand variance
        sales = db.query(Sale).filter(Sale.product_id == product_id).order_by(Sale.sale_date.desc()).limit(90).all()
        if len(sales) < 10:
            avg_daily_demand = product.minimum_stock / 7
            demand_sd = avg_daily_demand * 0.2
        else:
            daily_quantities = [s.quantity for s in sales]
            avg_daily_demand = np.mean(daily_quantities)
            demand_sd = np.std(daily_quantities)

        annual_demand = avg_daily_demand * 365
        
        # Assumptions for enterprise logic (can be made configurable)
        order_cost = getattr(settings, 'ORDER_COST', 50.0)
        holding_cost_pct = getattr(settings, 'HOLDING_COST_PCT', 0.2)
        holding_cost_unit = product.cost_price * holding_cost_pct
        lead_time = 7 # days

        eoq = self.calculate_eoq(annual_demand, order_cost, holding_cost_unit)
        safety_stock = self.calculate_safety_stock(demand_sd, lead_time)
        reorder_point = (avg_daily_demand * lead_time) + safety_stock

        return {
            "product_id": product.id,
            "product_name": product.name,
            "eoq": round(eoq, 2),
            "safety_stock": round(safety_stock, 2),
            "reorder_point": round(reorder_point, 2),
            "current_stock": product.current_stock,
            "recommendation": "Restock Now" if product.current_stock <= reorder_point else "Stock OK"
        }

# Global instance
optimization_engine = OptimizationEngine()
