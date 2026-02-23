from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import List, Dict
from ..models.database import Sale, Product, Alert, Order, Supplier
from ..schemas.market_intelligence import (
    MarketBrief, BusinessInsight, ProactiveOptimization, MarketIntelligenceResponse
)

class AIMarketService:
    @staticmethod
    def get_market_intelligence(db: Session) -> MarketIntelligenceResponse:
        """Generate high-end business intelligence and executive summaries from LIVE data"""
        
        now = datetime.utcnow()
        thirty_days_ago = now - timedelta(days=30)
        seven_days_ago = now - timedelta(days=7)

        # ── 1. Core Aggregates ─────────────────────────────────────────────
        total_revenue_30d = db.query(func.sum(Sale.total_amount)).filter(
            Sale.sale_date >= thirty_days_ago
        ).scalar() or 0.0

        total_sales_7d = db.query(func.count(Sale.id)).filter(
            Sale.sale_date >= seven_days_ago
        ).scalar() or 0

        total_products = db.query(func.count(Product.id)).scalar() or 0
        low_stock_count = db.query(func.count(Product.id)).filter(
            Product.current_stock <= Product.minimum_stock
        ).scalar() or 0
        out_of_stock_count = db.query(func.count(Product.id)).filter(
            Product.current_stock == 0
        ).scalar() or 0
        unresolved_alerts = db.query(func.count(Alert.id)).filter(
            Alert.is_resolved == False
        ).scalar() or 0
        pending_orders = db.query(func.count(Order.id)).filter(
            Order.status == "pending"
        ).scalar() or 0

        # ── 2. Top selling category ────────────────────────────────────────
        top_category_row = db.query(
            Product.category,
            func.sum(Sale.total_amount).label('cat_revenue')
        ).join(Sale, Sale.product_id == Product.id).filter(
            Sale.sale_date >= thirty_days_ago
        ).group_by(Product.category).order_by(desc('cat_revenue')).first()

        top_category = top_category_row.category if top_category_row else "General"
        top_cat_revenue = top_category_row.cat_revenue if top_category_row else 0.0

        # ── 3. Top selling product in last 7 days ──────────────────────────
        top_product_row = db.query(
            Product.name,
            func.sum(Sale.quantity).label('units_sold')
        ).join(Sale, Sale.product_id == Product.id).filter(
            Sale.sale_date >= seven_days_ago
        ).group_by(Product.id, Product.name).order_by(desc('units_sold')).first()

        top_product_name = top_product_row.name if top_product_row else "N/A"
        top_product_units = int(top_product_row.units_sold) if top_product_row else 0

        # ── 4. Highest stock-out risk product ─────────────────────────────
        high_risk_product = db.query(Product).filter(
            Product.current_stock == 0
        ).first()
        if not high_risk_product:
            high_risk_product = db.query(Product).filter(
                Product.current_stock <= Product.minimum_stock
            ).order_by(Product.current_stock.asc()).first()

        # ── 5. ROI Score (computed) ─────────────────────────────────────────
        total_cost = db.query(
            func.sum(Sale.quantity * Product.cost_price)
        ).join(Product, Product.id == Sale.product_id).filter(
            Sale.sale_date >= thirty_days_ago
        ).scalar() or 0.0

        gross_profit = total_revenue_30d - total_cost
        roi_score = round(min(9.9, max(1.0, (gross_profit / max(total_cost, 1)) * 10)), 1) if total_cost > 0 else 7.5

        # ── 6. Top efficiency driver ────────────────────────────────────────
        if pending_orders > 5:
            top_efficiency_gain = "Purchase Order Automation"
        elif low_stock_count > 10:
            top_efficiency_gain = "Automated Restocking"
        elif out_of_stock_count > 0:
            top_efficiency_gain = "Stock-out Prevention"
        else:
            top_efficiency_gain = "Demand Forecasting"

        # ── 7. Build Headline & Summary ────────────────────────────────────
        headline = f"{top_category} is your highest-revenue category with ₹{top_cat_revenue:,.0f} in the last 30 days."
        if total_revenue_30d > 0:
            summary = (
                f"Total revenue: ₹{total_revenue_30d:,.2f} over 30 days. "
                f"{total_sales_7d} transactions processed this week. "
                f"{low_stock_count} products are low on stock and {out_of_stock_count} are completely out. "
                f"{pending_orders} purchase orders are pending approval."
            )
        else:
            summary = (
                f"No sales recorded in the last 30 days. "
                f"Inventory: {total_products} products, {low_stock_count} low stock, {out_of_stock_count} out of stock. "
                f"{pending_orders} pending orders awaiting action."
            )

        brief = MarketBrief(
            summary=summary,
            headline_insight=headline,
            roi_score=roi_score,
            top_efficiency_gain=top_efficiency_gain
        )

        # ── 8. Business Insights (real data) ──────────────────────────────
        insights = []

        # Revenue insight
        if total_revenue_30d > 0:
            insights.append(BusinessInsight(
                title="Revenue Performance",
                description=f"₹{total_revenue_30d:,.2f} generated in the last 30 days. "
                             f"Top product: '{top_product_name}' with {top_product_units} units sold this week.",
                impact_level="High",
                category="Revenue"
            ))
        else:
            insights.append(BusinessInsight(
                title="Revenue Alert",
                description="No sales recorded in the last 30 days. Consider running a promotional campaign or checking if the sales recording pipeline is active.",
                impact_level="High",
                category="Revenue"
            ))

        # Efficiency insight
        if pending_orders > 0:
            insights.append(BusinessInsight(
                title="Orders Pending Approval",
                description=f"{pending_orders} purchase order(s) are awaiting approval. "
                             "Approving them promptly will prevent supplier delays and restocking gaps.",
                impact_level="Medium",
                category="Efficiency"
            ))
        else:
            insights.append(BusinessInsight(
                title="Order Pipeline Clear",
                description="All purchase orders are processed. Supply chain is operating without backlogs.",
                impact_level="Medium",
                category="Efficiency"
            ))

        # Risk insight
        if out_of_stock_count > 0:
            risk_name = high_risk_product.name if high_risk_product else "multiple products"
            insights.append(BusinessInsight(
                title="Stock-out Risk",
                description=f"{out_of_stock_count} product(s) are currently out of stock. "
                             f"Highest urgency: '{risk_name}'. Raise purchase orders immediately to avoid lost sales.",
                impact_level="High",
                category="Risk"
            ))
        elif low_stock_count > 0:
            risk_name = high_risk_product.name if high_risk_product else "several products"
            insights.append(BusinessInsight(
                title="Low Stock Warning",
                description=f"{low_stock_count} product(s) are below minimum stock threshold. "
                             f"'{risk_name}' needs replenishment soon.",
                impact_level="Medium",
                category="Risk"
            ))
        else:
            insights.append(BusinessInsight(
                title="Inventory Healthy",
                description="All products are above their minimum stock thresholds. Inventory levels are optimal.",
                impact_level="Low",
                category="Risk"
            ))

        # ── 9. Proactive Optimizations (real data) ────────────────────────
        optimizations = []
        low_stock_products = db.query(Product).filter(
            Product.current_stock <= Product.minimum_stock,
            Product.current_stock > 0
        ).order_by(Product.current_stock.asc()).limit(2).all()

        for i, p in enumerate(low_stock_products):
            reorder_qty = p.maximum_stock - p.current_stock
            savings = round(reorder_qty * p.cost_price * 0.05, 2)  # estimated 5% bulk discount
            optimizations.append(ProactiveOptimization(
                id=f"OPT-{i+1:03d}",
                action=f"Reorder '{p.name}': current stock {p.current_stock}, minimum is {p.minimum_stock}. Order {reorder_qty} units.",
                potential_savings=savings,
                urgency="Immediate" if p.current_stock == 0 else "Scheduled"
            ))

        if not optimizations:
            optimizations.append(ProactiveOptimization(
                id="OPT-001",
                action="Inventory is well-stocked. Focus on demand forecasting to pre-position fast-moving products.",
                potential_savings=0.0,
                urgency="Scheduled"
            ))

        return MarketIntelligenceResponse(
            brief=brief,
            insights=insights,
            optimizations=optimizations
        )
