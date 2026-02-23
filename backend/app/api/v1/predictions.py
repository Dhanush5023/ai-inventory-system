from flask import Blueprint, request, jsonify
from datetime import datetime
from typing import List
from ...models.database import get_db, Product
from ...schemas.predictions import ForecastRequest, ForecastResponse, ForecastDataPoint
from ...ai.forecasting.prediction_service import PredictionService
from ...core.security import login_required

bp = Blueprint("predictions", __name__)
prediction_service = PredictionService()


@bp.route("/forecast", methods=["POST"])
@login_required
def forecast_demand():
    """
    Generate demand forecast for a product using ML models
    """
    db = get_db()
    try:
        forecast_request = ForecastRequest(**request.json)
    except Exception as e:
        return jsonify({"detail": str(e)}), 400
        
    product = db.query(Product).filter(Product.id == forecast_request.product_id).first()
    if not product:
        return jsonify({"detail": "Product not found"}), 404

    # Generate predictions
    predictions = prediction_service.generate_predictions(
        db, 
        forecast_request.product_id, 
        forecast_request.horizon_days
    )

    # Convert to response format
    forecast_points = []
    model_used = predictions[0].model_used if predictions else "insufficient_data"
    
    recommended_restock_date = None
    recommended_restock_quantity = 0
    
    for pred in predictions:
        point = ForecastDataPoint(
            date=pred.target_date,
            predicted_demand=pred.predicted_demand,
            confidence_lower=pred.predicted_demand * (1 - (100 - pred.confidence_score)/100),
            confidence_upper=pred.predicted_demand * (1 + (100 - pred.confidence_score)/100),
        )
        forecast_points.append(point)
        
        if pred.recommended_stock > 0 and recommended_restock_quantity == 0:
            recommended_restock_date = pred.target_date
            recommended_restock_quantity = pred.recommended_stock

    metrics = prediction_service.model_metrics.get(model_used, {})

    response_data = ForecastResponse(
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
    return jsonify(response_data.model_dump())


@bp.route("/retrain", methods=["POST"])
@login_required
def retrain_models():
    """Trigger model retraining manually"""
    from ...ai.forecasting.scheduler import ml_scheduler
    ml_scheduler.weekly_retrain_job()
    return jsonify({"message": "Model retraining started"})


@bp.route("/product/<int:product_id>", methods=["GET"])
@login_required
def get_product_forecast(product_id: int):
    """Get stored forecast for a product"""
    db = get_db()
    days = int(request.args.get("days", 30))
    forecast_data = prediction_service.get_product_forecast(db, product_id, days)
    
    results = [
        ForecastDataPoint(
            date=datetime.strptime(d['date'], '%Y-%m-%d'),
            predicted_demand=d['predicted_demand'],
            confidence_lower=d['predicted_demand'] * 0.8,
            confidence_upper=d['predicted_demand'] * 1.2
        ).model_dump()
        for d in forecast_data
    ]
    return jsonify(results)
