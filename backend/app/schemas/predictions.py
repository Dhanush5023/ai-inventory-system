from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class PredictionBase(BaseModel):
    """Base prediction schema"""
    product_id: int
    target_date: datetime
    predicted_demand: float = Field(..., ge=0)
    confidence_score: Optional[float] = Field(None, ge=0, le=1)
    model_used: Optional[str] = None
    recommended_stock: Optional[int] = Field(None, ge=0)
    
    model_config = ConfigDict(protected_namespaces=())


class PredictionCreate(PredictionBase):
    """Prediction creation schema"""
    pass


class PredictionResponse(PredictionBase):
    """Prediction response schema"""
    id: int
    prediction_date: datetime
    product_name: Optional[str] = None
    product_sku: Optional[str] = None
    current_stock: Optional[int] = None

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class PredictionListResponse(BaseModel):
    """Paginated predictions list response"""
    predictions: list[PredictionResponse]
    total: int
    page: int
    page_size: int


class ForecastRequest(BaseModel):
    """Forecast request schema"""
    product_id: int
    horizon_days: int = Field(default=30, ge=1, le=365)
    model: Optional[str] = Field(None, pattern="^(linear|random_forest|xgboost|arima|lstm|ensemble)$")


class ForecastDataPoint(BaseModel):
    """Single forecast data point"""
    date: datetime
    predicted_demand: float
    confidence_lower: Optional[float] = None
    confidence_upper: Optional[float] = None


class ForecastResponse(BaseModel):
    """Forecast response schema"""
    product_id: int
    product_name: str
    current_stock: int
    minimum_stock: int
    model_used: str
    forecast_start: datetime
    forecast_end: datetime
    forecasts: List[ForecastDataPoint]
    recommended_restock_date: Optional[datetime] = None
    recommended_restock_quantity: Optional[int] = None
    model_metrics: Optional[dict] = None
    
    model_config = ConfigDict(protected_namespaces=())


class ModelPerformance(BaseModel):
    """Model performance metrics"""
    model_name: str
    mae: float  # Mean Absolute Error
    rmse: float  # Root Mean Square Error
    mape: float  # Mean Absolute Percentage Error
    r2_score: float
    training_date: datetime
    test_samples: int
    
    model_config = ConfigDict(protected_namespaces=())


class AllModelsPerformance(BaseModel):
    """Performance comparison of all models"""
    models: List[ModelPerformance]
    best_model: str
    recommendation: str
