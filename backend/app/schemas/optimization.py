from pydantic import BaseModel
from typing import List

class OptimizationMetrics(BaseModel):
    product_id: int
    product_name: str
    eoq: float
    safety_stock: float
    reorder_point: float
    current_stock: int
    recommendation: str

class OptimizationResponse(BaseModel):
    items: List[OptimizationMetrics]
    count: int
