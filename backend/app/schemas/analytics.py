from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class DashboardKPI(BaseModel):
    """Dashboard KPI card data"""
    label: str
    value: str | int | float
    change_percentage: Optional[float] = None
    trend: Optional[str] = None  # up, down, stable
    icon: Optional[str] = None


class DashboardOverview(BaseModel):
    """Main dashboard overview"""
    kpis: List[DashboardKPI]
    low_stock_count: int
    critical_alerts: int
    pending_orders: int
    recent_sales_count: int


class TimeSeriesDataPoint(BaseModel):
    """Time series data point"""
    date: datetime
    value: float
    label: Optional[str] = None


class CategoryData(BaseModel):
    """Category-based data"""
    category: str
    value: float
    percentage: Optional[float] = None


class TopProduct(BaseModel):
    """Top product data"""
    product_id: int
    product_name: str
    sku: str
    quantity_sold: int
    revenue: float
    profit: float


class InventoryMetrics(BaseModel):
    """Inventory metrics"""
    total_products: int
    total_stock_value: float
    in_stock_products: int
    low_stock_products: int
    out_of_stock_products: int
    out_of_stock_products: int
    inventory_turnover_ratio: float
    stock_by_category: List[CategoryData]


class SalesMetrics(BaseModel):
    """Sales metrics"""
    total_sales: int
    total_revenue: float
    average_order_value: float
    revenue_growth: float
    sales_by_day: List[TimeSeriesDataPoint]
    sales_by_category: List[CategoryData]
    top_products: List[TopProduct]


class FinancialMetrics(BaseModel):
    """Financial metrics"""
    total_revenue: float
    total_cost: float
    gross_profit: float
    profit_margin: float
    revenue_by_month: List[TimeSeriesDataPoint]


class AnalyticsDashboard(BaseModel):
    """Comprehensive analytics dashboard"""
    overview: DashboardOverview
    inventory_metrics: InventoryMetrics
    sales_metrics: SalesMetrics
    financial_metrics: FinancialMetrics
    period_start: datetime
    period_end: datetime


class DateRangeFilter(BaseModel):
    """Date range filter for analytics"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    period: Optional[str] = None  # today, week, month, quarter, year, custom


class RecommendationRequest(BaseModel):
    """Request for product recommendations"""
    cart_product_ids: List[int]
