from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from ...models.database import get_db, Product
from ...schemas.predictions import ForecastRequest, ForecastResponse, ForecastDataPoint
from ...ai.forecasting.prediction_service import PredictionService
from ...core.security import get_current_user_id

router = APIRouter()
prediction_service = PredictionService()


@router.post("/forecast", response_model=ForecastResponse)
def forecast_demand(
    request: ForecastRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Generate demand forecast for a product using ML models
    """
    product = db.query(Product).filter(Product.id == request.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # Generate predictions
    predictions = prediction_service.generate_predictions(
        db, 
        request.product_id, 
        request.horizon_days
    )

    if not predictions:
        # Fallback if no predictions generated (e.g. insufficient data)
        # return a default response or error
        # For now, let's return a basic response or let the service handle it
        pass

    # Convert to response format
    forecast_points = []
    
    # Get model used from first prediction if available
    model_used = predictions[0].model_used if predictions else "insufficient_data"
    
    # Calculate recommended restock
    # Use the logic from the service or the last prediction
    recommended_restock_date = None
    recommended_restock_quantity = 0
    
    for pred in predictions:
        point = ForecastDataPoint(
            date=pred.target_date,
            predicted_demand=pred.predicted_demand,
            confidence_lower=pred.predicted_demand * (1 - (100 - pred.confidence_score)/100), # Approximated
            confidence_upper=pred.predicted_demand * (1 + (100 - pred.confidence_score)/100), # Approximated
        )
        forecast_points.append(point)
        
        # Simple logic to find first date where simple prediction stock < min_stock
        # This is better handled by the alert service, but for forecast response:
        # We can just sum up demand? 
        # Actually the Prediction model has `recommended_stock`.
        if pred.recommended_stock > 0 and recommended_restock_quantity == 0:
            recommended_restock_date = pred.target_date
            recommended_restock_quantity = pred.recommended_stock

    # Get metrics
    metrics = prediction_service.model_metrics.get(model_used, {})

    return ForecastResponse(
        product_id=product.id,
        product_name=product.name,
        current_stock=product.current_stock,
        minimum_stock=product.minimum_stock,
        model_used=model_used,
        forecast_start=datetime.utcnow(),
        forecast_end=predictions[-1].target_date if predictions else datetime.utcnow(),
        forecasts=forecast_points,
        recommended_restock_date=recommended_restock_date,
        recommended_restock_quantity=recommended_restock_quantity,
        model_metrics=metrics,
    )


@router.post("/retrain")
def retrain_models(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Trigger model retraining manually"""
    # Verify admin here if needed
    from ...ai.forecasting.scheduler import ml_scheduler
    ml_scheduler.weekly_retrain_job()
    return {"message": "Model retraining started"}


@router.get("/product/{product_id}", response_model=List[ForecastDataPoint])
def get_product_forecast(
    product_id: int,
    days: int = 30,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get stored forecast for a product"""
    forecast_data = prediction_service.get_product_forecast(db, product_id, days)
    
    return [
        ForecastDataPoint(
            date=datetime.strptime(d['date'], '%Y-%m-%d'),
            predicted_demand=d['predicted_demand'],
            confidence_lower=d['predicted_demand'] * 0.8, # Placeholder confidence interval
            confidence_upper=d['predicted_demand'] * 1.2
        )
        for d in forecast_data
    ]
