from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class SaleBase(BaseModel):
    """Base sale schema"""
    product_id: int
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)
    sale_date: Optional[datetime] = None
    notes: Optional[str] = None


class SaleCreate(SaleBase):
    """Sale creation schema"""
    pass


class BulkSaleCreate(BaseModel):
    """Bulk sale creation schema"""
    items: list[SaleCreate]


class SaleUpdate(BaseModel):
    """Sale update schema"""
    quantity: Optional[int] = Field(None, gt=0)
    unit_price: Optional[float] = Field(None, gt=0)
    notes: Optional[str] = None


class SaleResponse(SaleBase):
    """Sale response schema"""
    id: int
    user_id: Optional[int]
    total_amount: float
    sale_date: datetime
    product_name: Optional[str] = None
    username: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class SaleListResponse(BaseModel):
    """Paginated sales list response"""
    sales: list[SaleResponse]
    total: int
    page: int
    page_size: int
    total_revenue: float


class SalesSummary(BaseModel):
    """Sales summary statistics"""
    total_revenue: float
    total_quantity: int
    total_transactions: int
    period_days: int


class SalesAnalytics(BaseModel):
    """Sales analytics response"""
    total_sales: int
    total_revenue: float
    average_order_value: float
    top_products: list[dict]
    sales_by_date: list[dict]
    sales_by_category: list[dict]


class SalesFilter(BaseModel):
    """Sales filtering parameters"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    product_id: Optional[int] = None
    user_id: Optional[int] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
