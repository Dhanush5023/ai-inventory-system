from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ...models.database import get_db, Product
from ...schemas.optimization import OptimizationMetrics, OptimizationResponse
from ...ai.optimization.engine import optimization_engine
from ...core.security import get_current_user_id

router = APIRouter()

@router.get("/metrics", response_model=OptimizationResponse)
def get_all_optimization_metrics(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get optimization metrics (EOQ, Safety Stock) for all products
    """
    products = db.query(Product).all()
    results = []
    
    for product in products:
        metrics = optimization_engine.optimize_product(db, product.id)
        if metrics:
            results.append(OptimizationMetrics(**metrics))
            
    return OptimizationResponse(items=results, count=len(results))

@router.get("/product/{product_id}", response_model=OptimizationMetrics)
def get_product_optimization_metrics(
    product_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get optimization metrics for a specific product
    """
    metrics = optimization_engine.optimize_product(db, product_id)
    if not metrics:
        raise HTTPException(status_code=404, detail="Product not found")
        
    return OptimizationMetrics(**metrics)
