from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class AlertBase(BaseModel):
    """Base alert schema"""
    product_id: int
    alert_type: str = Field(..., pattern="^(low_stock|restock_needed|out_of_stock|overstock)$")
    message: str = Field(..., min_length=1)
    severity: str = Field(default="medium", pattern="^(low|medium|high|critical)$")
    recommended_quantity: Optional[int] = Field(None, ge=0)


class AlertCreate(AlertBase):
    """Alert creation schema"""
    pass


class AlertUpdate(BaseModel):
    """Alert update schema"""
    is_read: Optional[bool] = None
    is_resolved: Optional[bool] = None


class AlertResponse(AlertBase):
    """Alert response schema"""
    id: int
    is_read: bool
    is_resolved: bool
    created_at: datetime
    resolved_at: Optional[datetime]
    product_name: Optional[str] = None
    product_sku: Optional[str] = None
    current_stock: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class AlertListResponse(BaseModel):
    """Paginated alerts list response"""
    alerts: list[AlertResponse]
    total: int
    unread_count: int
    critical_count: int
    page: int
    page_size: int


class AlertFilter(BaseModel):
    """Alert filtering parameters"""
    alert_type: Optional[str] = None
    severity: Optional[str] = None
    is_read: Optional[bool] = None
    is_resolved: Optional[bool] = None
    product_id: Optional[int] = None


class AlertStats(BaseModel):
    """Alert statistics"""
    total_alerts: int
    unread_alerts: int
    critical_alerts: int
    low_stock_alerts: int
    out_of_stock_alerts: int
    restock_needed_alerts: int


class AlertSummary(BaseModel):
    """Alert summary statistics"""
    total_alerts: int
    unread_alerts: int
    unresolved_alerts: int
    critical_alerts: int
    high_alerts: int
