from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, desc
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
        """Get main dashboard overview with KPIs (Optimized)"""
        now = datetime.utcnow()
        thirty_days_ago = now - timedelta(days=30)
        sixty_days_ago = now - timedelta(days=60)
        seven_days_ago = now - timedelta(days=7)

        # 1. KPI Counts (Single queries)
        total_products = db.query(func.count(Product.id)).scalar() or 0
        low_stock_count = db.query(func.count(Product.id)).filter(Product.current_stock <= Product.minimum_stock).scalar() or 0
        critical_alerts = db.query(func.count(Alert.id)).filter(Alert.severity == "critical", Alert.is_resolved == False).scalar() or 0
        pending_orders = db.query(func.count(Order.id)).filter(Order.status == "pending").scalar() or 0
        recent_sales_count = db.query(func.count(Sale.id)).filter(Sale.sale_date >= seven_days_ago).scalar() or 0

        # 2. Revenue Aggregation (Database-level sums)
        total_revenue = db.query(func.sum(Sale.total_amount)).filter(Sale.sale_date >= thirty_days_ago).scalar() or 0.0
        previous_revenue = db.query(func.sum(Sale.total_amount)).filter(
            Sale.sale_date >= sixty_days_ago, 
            Sale.sale_date < thirty_days_ago
        ).scalar() or 0.0

        revenue_growth = 0.0
        if previous_revenue > 0:
            revenue_growth = ((total_revenue - previous_revenue) / previous_revenue) * 100

        # 3. Stock Value (Database-level sum extension)
        total_stock_value = db.query(func.sum(Product.current_stock * Product.cost_price)).scalar() or 0.0

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
        """Get inventory metrics (Optimized)"""
        # Batch calculations to database
        stats = db.query(
            func.count(Product.id).label('total'),
            func.sum(Product.current_stock * Product.cost_price).label('value'),
            func.sum(Product.current_stock).label('count_units')
        ).first()

        total_products = stats.total or 0
        total_stock_value = stats.value or 0.0
        total_stock_count = stats.count_units or 0

        in_stock_products = db.query(func.count(Product.id)).filter(Product.current_stock > Product.minimum_stock).scalar() or 0
        low_stock_products = db.query(func.count(Product.id)).filter(Product.current_stock > 0, Product.current_stock <= Product.minimum_stock).scalar() or 0
        out_of_stock_products = db.query(func.count(Product.id)).filter(Product.current_stock == 0).scalar() or 0

        # Inventory Turnover (Database-level)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        cogs = db.query(func.sum(Sale.quantity * Product.cost_price)).join(Product).filter(Sale.sale_date >= thirty_days_ago).scalar() or 0.0
        inventory_turnover_ratio = (cogs / total_stock_value * 12) if total_stock_value > 0 else 0.0

        # Stock by category (Optimized aggregation)
        category_query = db.query(
            Product.category,
            func.sum(Product.current_stock).label('val')
        ).group_by(Product.category).order_by(desc('val')).all()
            
        stock_by_category = [
            CategoryData(
                category=cat or "Uncategorized",
                value=val,
                percentage=(val / total_stock_count * 100) if total_stock_count > 0 else 0.0
            )
            for cat, val in category_query
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
        """Get sales metrics (Optimized)"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 1. Broad aggregations
        sales_stats = db.query(
            func.count(Sale.id).label('count'),
            func.sum(Sale.total_amount).label('rev')
        ).filter(Sale.sale_date >= start_date).first()
        
        total_sales_count = sales_stats.count or 0
        total_revenue = sales_stats.rev or 0.0
        average_order_value = total_revenue / total_sales_count if total_sales_count > 0 else 0.0

        # 2. Revenue growth (DB level)
        prev_start = start_date - timedelta(days=days)
        prev_revenue = db.query(func.sum(Sale.total_amount)).filter(
            Sale.sale_date >= prev_start, 
            Sale.sale_date < start_date
        ).scalar() or 0.0
        revenue_growth = ((total_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0.0

        # 3. Sales by category (Direct Group By)
        category_sales_query = db.query(
            Product.category,
            func.sum(Sale.total_amount).label('val')
        ).join(Sale).filter(Sale.sale_date >= start_date).group_by(Product.category).all()
            
        sales_by_category = [
            CategoryData(
                category=cat or "Uncategorized",
                value=val,
                percentage=(val / total_revenue * 100) if total_revenue > 0 else 0.0
            )
            for cat, val in category_sales_query
        ]

        # 4. Top products (Optimized)
        top_prod_query = db.query(
            Sale.product_id,
            Product.name.label('product_name'),
            Product.sku.label('sku'),
            func.sum(Sale.quantity).label('quantity_sold'),
            func.sum(Sale.total_amount).label('revenue'),
            func.sum((Sale.unit_price - Product.cost_price) * Sale.quantity).label('profit')
        ).join(Product).filter(Sale.sale_date >= start_date).group_by(Sale.product_id, Product.name, Product.sku).order_by(desc('revenue')).limit(10).all()

        top_products = [TopProduct(**row._asdict()) for row in top_prod_query]

        # 5. Time series (Date aggregation)
        # Note: SQLite date formatting. In production with Postgres/MySQL use appropriate date trunc.
        sales_by_day_query = db.query(
            func.date(Sale.sale_date).label('day'),
            func.sum(Sale.total_amount).label('val')
        ).filter(Sale.sale_date >= start_date).group_by('day').order_by('day').all()

        sales_by_day = [
            TimeSeriesDataPoint(date=datetime.strptime(row.day, '%Y-%m-%d'), value=row.val)
            for row in sales_by_day_query
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
        """Get financial metrics (Optimized)"""
        start_date = datetime.utcnow() - timedelta(days=months * 30)
        
        # 1. Broad aggregations
        stats = db.query(
            func.sum(Sale.total_amount).label('rev'),
            func.sum(Sale.quantity * Product.cost_price).label('cost')
        ).join(Product).filter(Sale.sale_date >= start_date).first()

        total_revenue = stats.rev or 0.0
        total_cost = stats.cost or 0.0
        gross_profit = total_revenue - total_cost
        profit_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0.0

        # 2. Revenue by month (DB level)
        # SQLite date format. For other DBs use appropriate trunc.
        monthly_query = db.query(
            func.strftime('%Y-%m-01', Sale.sale_date).label('month'),
            func.sum(Sale.total_amount).label('val')
        ).filter(Sale.sale_date >= start_date).group_by('month').order_by('month').all()
            
        revenue_by_month = [
            TimeSeriesDataPoint(date=datetime.strptime(m, '%Y-%m-%d'), value=v)
            for m, v in monthly_query
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
