from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime


class SupplierBase(BaseModel):
    """Base supplier schema"""
    name: str = Field(..., min_length=1, max_length=255)
    contact_person: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    rating: float = Field(default=5.0, ge=0, le=5)
    is_active: bool = True


class SupplierCreate(SupplierBase):
    """Supplier creation schema"""
    pass


class SupplierUpdate(BaseModel):
    """Supplier update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    contact_person: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    rating: Optional[float] = Field(None, ge=0, le=5)
    is_active: Optional[bool] = None


class SupplierResponse(SupplierBase):
    """Supplier response schema"""
    id: int
    created_at: datetime
    product_count: int
    total_orders: int
    average_delivery_time: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class SupplierListResponse(BaseModel):
    """Paginated supplier list response"""
    suppliers: list[SupplierResponse]
    total: int
    page: int
    page_size: int


class SupplierPerformance(BaseModel):
    """Supplier performance metrics"""
    supplier_id: int
    supplier_name: str
    total_orders: int
    completed_orders: int
    cancelled_orders: int
    average_delivery_days: float
    on_time_delivery_rate: float
    rating: float
