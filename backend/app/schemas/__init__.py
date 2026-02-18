"""
Pydantic schemas for API request/response validation
"""

from .auth import (
    UserLogin,
    UserRegister,
    Token,
    TokenRefresh,
)

from .users import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse,
    PasswordChange,
)

from .products import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse,
    ProductSearchParams,
    BulkProductImport,
    StockAdjustment,
)

from .sales import (
    SaleCreate,
    SaleUpdate,
    SaleResponse,
    SaleListResponse,
    SalesAnalytics,
    SalesFilter,
)

from .suppliers import (
    SupplierCreate,
    SupplierUpdate,
    SupplierResponse,
    SupplierListResponse,
    SupplierPerformance,
)

from .orders import (
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    OrderListResponse,
    OrderFilter,
    OrderStatusUpdate,
    ReceiveOrder,
)

from .predictions import (
    PredictionResponse,
    PredictionListResponse,
    ForecastRequest,
    ForecastResponse,
    ModelPerformance,
    AllModelsPerformance,
)

from .alerts import (
    AlertCreate,
    AlertUpdate,
    AlertResponse,
    AlertListResponse,
    AlertFilter,
    AlertStats,
)

from .analytics import (
    DashboardOverview,
    AnalyticsDashboard,
    DateRangeFilter,
    SalesMetrics,
    InventoryMetrics,
    FinancialMetrics,
)

__all__ = [
    # Auth
    "UserLogin",
    "UserRegister",
    "Token",
    "TokenRefresh",
    # Users
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserListResponse",
    "PasswordChange",
    # Products
    "ProductCreate",
    "ProductUpdate",
    "ProductResponse",
    "ProductListResponse",
    "ProductSearchParams",
    "BulkProductImport",
    "StockAdjustment",
    # Sales
    "SaleCreate",
    "SaleUpdate",
    "SaleResponse",
    "SaleListResponse",
    "SalesAnalytics",
    "SalesFilter",
    # Suppliers
    "SupplierCreate",
    "SupplierUpdate",
    "SupplierResponse",
    "SupplierListResponse",
    "SupplierPerformance",
    # Orders
    "OrderCreate",
    "OrderUpdate",
    "OrderResponse",
    "OrderListResponse",
    "OrderFilter",
    "OrderStatusUpdate",
    "ReceiveOrder",
    # Predictions
    "PredictionResponse",
    "PredictionListResponse",
    "ForecastRequest",
    "ForecastResponse",
    "ModelPerformance",
    "AllModelsPerformance",
    # Alerts
    "AlertCreate",
    "AlertUpdate",
    "AlertResponse",
    "AlertListResponse",
    "AlertFilter",
    "AlertStats",
    # Analytics
    "DashboardOverview",
    "AnalyticsDashboard",
    "DateRangeFilter",
    "SalesMetrics",
    "InventoryMetrics",
    "FinancialMetrics",
]
