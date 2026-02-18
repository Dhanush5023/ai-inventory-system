from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class ProductBase(BaseModel):
    """Base product schema"""
    name: str = Field(..., min_length=1, max_length=255)
    sku: str = Field(..., min_length=1, max_length=100)
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    unit_price: float = Field(..., gt=0)
    cost_price: float = Field(..., gt=0)
    current_stock: int = Field(default=0, ge=0)
    minimum_stock: int = Field(default=10, ge=0)
    maximum_stock: int = Field(default=1000, ge=0)
    unit: str = Field(default="pcs", max_length=50)
    supplier_id: Optional[int] = None


class ProductCreate(ProductBase):
    """Product creation schema"""
    pass


class ProductUpdate(BaseModel):
    """Product update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    sku: Optional[str] = Field(None, min_length=1, max_length=100)
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    unit_price: Optional[float] = Field(None, gt=0)
    cost_price: Optional[float] = Field(None, gt=0)
    current_stock: Optional[int] = Field(None, ge=0)
    minimum_stock: Optional[int] = Field(None, ge=0)
    maximum_stock: Optional[int] = Field(None, ge=0)
    unit: Optional[str] = Field(None, max_length=50)
    supplier_id: Optional[int] = None


class ProductResponse(ProductBase):
    """Product response schema"""
    id: int
    created_at: datetime
    updated_at: datetime
    supplier_name: Optional[str] = None
    stock_status: str  # in_stock, low_stock, out_of_stock
    profit_margin: float
    ai_insights: Optional[dict] = None
    demand_forecast: Optional[list] = None
    pending_orders: Optional[list] = None

    model_config = ConfigDict(from_attributes=True)


class ProductListResponse(BaseModel):
    """Paginated product list response"""
    products: list[ProductResponse]
    total: int
    page: int
    page_size: int


class ProductSearchParams(BaseModel):
    """Product search parameters"""
    query: Optional[str] = None
    category: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    in_stock_only: bool = False
    low_stock_only: bool = False


class BulkProductImport(BaseModel):
    """Bulk product import schema"""
    products: list[ProductCreate]


class StockAdjustment(BaseModel):
    """Stock adjustment schema"""
    product_id: int
    quantity: int  # Can be positive or negative
    reason: str = Field(..., min_length=1)
