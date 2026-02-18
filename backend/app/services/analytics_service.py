from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from datetime import datetime, timedelta

from ..models.database import Product, Sale, Order, Alert, Supplier
from ..schemas.analytics import (
    DashboardKPI,
    DashboardOverview,
    TimeSeriesDataPoint,
    CategoryData,
    TopProduct,
    InventoryMetrics,
    SalesMetrics,
    FinancialMetrics,
    AnalyticsDashboard,
)


class AnalyticsService:
    """Analytics and dashboard metrics service"""

    @staticmethod
    def get_dashboard_overview(db: Session) -> DashboardOverview:
        """Get main dashboard overview with KPIs"""
        total_products = db.query(Product).count()
        low_stock_count = db.query(Product).filter(Product.current_stock <= Product.minimum_stock).count()
        critical_alerts = db.query(Alert).filter(Alert.severity == "critical", Alert.is_resolved == False).count()
        pending_orders = db.query(Order).filter(Order.status == "pending").count()

        # Recent sales count (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_sales_count = db.query(Sale).filter(Sale.sale_date >= seven_days_ago).count()

        # Simple revenue calculation (30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        sales = db.query(Sale).filter(Sale.sale_date >= thirty_days_ago).all()
        total_revenue = sum(s.total_amount for s in sales)

        # Previous 30-day revenue for trend
        sixty_days_ago = datetime.utcnow() - timedelta(days=60)
        previous_sales = db.query(Sale).filter(Sale.sale_date >= sixty_days_ago, Sale.sale_date < thirty_days_ago).all()
        previous_revenue = sum(s.total_amount for s in previous_sales)

        revenue_growth = 0.0
        if previous_revenue > 0:
            revenue_growth = ((total_revenue - previous_revenue) / previous_revenue) * 100

        # Total stock value
        all_products = db.query(Product).all()
        total_stock_value = sum(p.current_stock * p.cost_price for p in all_products)

        kpis = [
            DashboardKPI(label="Total Products", value=total_products, icon="package"),
            DashboardKPI(
                label="Total Revenue (30d)",
                value=f"₹{total_revenue:,.2f}",
                change_percentage=round(revenue_growth, 2),
                trend="up" if revenue_growth > 0 else "down",
                icon="dollar"
            ),
            DashboardKPI(label="Low Stock Items", value=low_stock_count, icon="alert"),
            DashboardKPI(label="Stock Value", value=f"₹{total_stock_value:,.2f}", icon="trending-up"),
        ]

        return DashboardOverview(
            kpis=kpis,
            low_stock_count=low_stock_count,
            critical_alerts=critical_alerts,
            pending_orders=pending_orders,
            recent_sales_count=recent_sales_count,
        )

    @staticmethod
    def get_inventory_metrics(db: Session) -> InventoryMetrics:
        """Get inventory metrics"""
        products = db.query(Product).all()
        
        total_products = len(products)
        total_stock_value = sum(p.current_stock * p.cost_price for p in products)
        in_stock_products = len([p for p in products if p.current_stock > p.minimum_stock])
        low_stock_products = len([p for p in products if 0 < p.current_stock <= p.minimum_stock])
        out_of_stock_products = len([p for p in products if p.current_stock == 0])

        # Inventory Turnover (Simple approximation: COGS / Avg Inventory)
        # Using 30-day COGS normalized to annual
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        sales = db.query(Sale).join(Product).filter(Sale.sale_date >= thirty_days_ago).all()
        cogs = sum(s.quantity * s.product.cost_price for s in sales if s.product)
        inventory_turnover_ratio = (cogs / total_stock_value * 12) if total_stock_value > 0 else 0.0

        # Stock by category
        categories = {}
        total_stock_count = sum(p.current_stock for p in products)
        for p in products:
            categories[p.category] = categories.get(p.category, 0) + p.current_stock
            
        stock_by_category = [
            CategoryData(
                category=cat or "Uncategorized",
                value=val,
                percentage=(val / total_stock_count * 100) if total_stock_count > 0 else 0.0
            )
            for cat, val in sorted(categories.items(), key=lambda x: x[1], reverse=True)
        ]

        return InventoryMetrics(
            total_products=total_products,
            total_stock_value=total_stock_value,
            in_stock_products=in_stock_products,
            low_stock_products=low_stock_products,
            out_of_stock_products=out_of_stock_products,
            inventory_turnover_ratio=round(inventory_turnover_ratio, 2),
            stock_by_category=stock_by_category,
        )

    @staticmethod
    def get_sales_metrics(db: Session, days: int = 30) -> SalesMetrics:
        """Get sales metrics"""
        start_date = datetime.utcnow() - timedelta(days=days)
        sales = db.query(Sale).options(joinedload(Sale.product)).filter(Sale.sale_date >= start_date).all()
        
        total_sales_count = len(sales)
        total_revenue = sum(s.total_amount for s in sales)
        average_order_value = total_revenue / total_sales_count if total_sales_count > 0 else 0.0

        # Revenue growth
        previous_period_start = start_date - timedelta(days=days)
        previous_sales = db.query(Sale).filter(Sale.sale_date >= previous_period_start, Sale.sale_date < start_date).all()
        previous_revenue = sum(s.total_amount for s in previous_sales)
        revenue_growth = ((total_revenue - previous_revenue) / previous_revenue * 100) if previous_revenue > 0 else 0.0

        # Sales by day
        sales_by_day_dict = {}
        for s in sales:
            date_key = s.sale_date.strftime('%Y-%m-%d')
            sales_by_day_dict[date_key] = sales_by_day_dict.get(date_key, 0) + s.total_amount
            
        sales_by_day = [
            TimeSeriesDataPoint(date=datetime.strptime(d, '%Y-%m-%d'), value=v)
            for d, v in sorted(sales_by_day_dict.items())
        ]

        # Sales by category
        category_sales = {}
        for s in sales:
            cat = s.product.category if s.product else "Uncategorized"
            category_sales[cat] = category_sales.get(cat, 0) + s.total_amount
            
        sales_by_category = [
            CategoryData(
                category=cat or "Uncategorized",
                value=val,
                percentage=(val / total_revenue * 100) if total_revenue > 0 else 0.0
            )
            for cat, val in sorted(category_sales.items(), key=lambda x: x[1], reverse=True)
        ]

        # Top products
        product_sales = {}
        for s in sales:
            if s.product_id not in product_sales:
                product_sales[s.product_id] = {
                    "product_name": s.product.name if s.product else "Unknown",
                    "sku": s.product.sku if s.product else "N/A",
                    "quantity_sold": 0,
                    "revenue": 0,
                    "profit": 0
                }
            
            stats = product_sales[s.product_id]
            stats["quantity_sold"] += s.quantity
            stats["revenue"] += s.total_amount
            if s.product:
                stats["profit"] += (s.unit_price - s.product.cost_price) * s.quantity
                
        top_products = [
            TopProduct(product_id=pid, **stats)
            for pid, stats in sorted(product_sales.items(), key=lambda x: x[1]["revenue"], reverse=True)[:10]
        ]

        return SalesMetrics(
            total_sales=total_sales_count,
            total_revenue=total_revenue,
            average_order_value=average_order_value,
            revenue_growth=revenue_growth,
            sales_by_day=sales_by_day,
            sales_by_category=sales_by_category,
            top_products=top_products,
        )

    @staticmethod
    def get_financial_metrics(db: Session, months: int = 6) -> FinancialMetrics:
        """Get financial metrics"""
        start_date = datetime.utcnow() - timedelta(days=months * 30)
        sales = db.query(Sale).options(joinedload(Sale.product)).filter(Sale.sale_date >= start_date).all()

        total_revenue = sum(s.total_amount for s in sales)
        total_cost = sum(s.quantity * s.product.cost_price for s in sales if s.product)
        gross_profit = total_revenue - total_cost
        profit_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0.0

        # Revenue by month
        monthly_revenue = {}
        for s in sales:
            month_key = s.sale_date.strftime('%Y-%m-01')
            monthly_revenue[month_key] = monthly_revenue.get(month_key, 0) + s.total_amount
            
        revenue_by_month = [
            TimeSeriesDataPoint(date=datetime.strptime(m, '%Y-%m-%d'), value=v)
            for m, v in sorted(monthly_revenue.items())
        ]

        return FinancialMetrics(
            total_revenue=total_revenue,
            total_cost=total_cost,
            gross_profit=gross_profit,
            profit_margin=round(profit_margin, 2),
            revenue_by_month=revenue_by_month,
        )

    @staticmethod
    def get_analytics_dashboard(
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> AnalyticsDashboard:
        """Get comprehensive analytics dashboard"""
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()

        days_diff = (end_date - start_date).days or 30

        overview = AnalyticsService.get_dashboard_overview(db)
        inventory_metrics = AnalyticsService.get_inventory_metrics(db)
        sales_metrics = AnalyticsService.get_sales_metrics(db, days=days_diff)
        financial_metrics = AnalyticsService.get_financial_metrics(db, months=6)

        return AnalyticsDashboard(
            overview=overview,
            inventory_metrics=inventory_metrics,
            sales_metrics=sales_metrics,
            financial_metrics=financial_metrics,
            period_start=start_date,
            period_end=end_date,
        )

    @staticmethod
    def get_recommendations(db: Session, product_ids: List[int]) -> List[dict]:
        """Simple content-based recommendation"""
        # Avoid circular import at top level
        from .product_service import ProductService
        
        # 1. Get categories of input products
        if not product_ids:
            # Return top selling products (simple heuristic: first 4 available)
            products = db.query(Product).filter(Product.current_stock > 0).limit(4).all()
        else:
            current_products = db.query(Product).filter(Product.id.in_(product_ids)).all()
            categories = {p.category for p in current_products if p.category}
            
            # 2. Find other products in these categories, distinct from input
            query = db.query(Product).filter(
                Product.category.in_(categories),
                Product.id.notin_(product_ids),
                Product.current_stock > 0
            )
            products = query.limit(4).all()
            
            # Fallback if no category matches found
            if not products:
                 products = db.query(Product).filter(
                     Product.id.notin_(product_ids),
                     Product.current_stock > 0
                ).limit(4).all()

        # Enrich
        return [ProductService.enrich_product_response(p, db) for p in products]
