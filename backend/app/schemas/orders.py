from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class OrderItemBase(BaseModel):
    """Base order item schema"""
    product_id: int
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)


class OrderItemCreate(OrderItemBase):
    """Order item creation schema"""
    pass


class OrderItemResponse(OrderItemBase):
    """Order item response schema"""
    id: int
    order_id: int
    total_price: float
    product_name: Optional[str] = None
    product_sku: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class OrderBase(BaseModel):
    """Base order schema"""
    supplier_id: int
    expected_delivery: Optional[datetime] = None
    notes: Optional[str] = None


class OrderCreate(OrderBase):
    """Order creation schema"""
    items: List[OrderItemCreate] = Field(..., min_length=1)


class OrderUpdate(BaseModel):
    """Order update schema"""
    status: Optional[str] = Field(None, pattern="^(pending|approved|shipped|received|cancelled)$")
    expected_delivery: Optional[datetime] = None
    received_date: Optional[datetime] = None
    notes: Optional[str] = None


class OrderResponse(OrderBase):
    """Order response schema"""
    id: int
    order_number: str
    user_id: Optional[int]
    status: str
    total_amount: float
    order_date: datetime
    received_date: Optional[datetime]
    supplier_name: Optional[str] = None
    username: Optional[str] = None
    items: List[OrderItemResponse] = []

    model_config = ConfigDict(from_attributes=True)


class OrderListResponse(BaseModel):
    """Paginated order list response"""
    orders: list[OrderResponse]
    total: int
    page: int
    page_size: int


class OrderFilter(BaseModel):
    """Order filtering parameters"""
    status: Optional[str] = None
    supplier_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class OrderStatusUpdate(BaseModel):
    """Order status update schema"""
    status: str = Field(..., pattern="^(pending|approved|shipped|received|cancelled)$")


class ReceiveOrderItem(BaseModel):
    """Receive order item schema"""
    order_item_id: int
    received_quantity: int = Field(..., gt=0)


class ReceiveOrder(BaseModel):
    """Receive order schema"""
    items: List[ReceiveOrderItem]
    notes: Optional[str] = None
