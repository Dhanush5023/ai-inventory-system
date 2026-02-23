from flask import Blueprint, request, jsonify
from ...models.database import get_db, Product
from ...schemas.optimization import OptimizationMetrics, OptimizationResponse
from ...ai.optimization.engine import optimization_engine
from ...core.security import login_required

bp = Blueprint("optimization", __name__)

@bp.route("/metrics", methods=["GET"])
@login_required
def get_all_optimization_metrics():
    """
    Get optimization metrics (EOQ, Safety Stock) for all products
    """
    db = get_db()
    products = db.query(Product).all()
    results = []
    
    for product in products:
        metrics = optimization_engine.optimize_product(db, product.id)
        if metrics:
            results.append(OptimizationMetrics(**metrics).model_dump())
            
    return jsonify(OptimizationResponse(items=results, count=len(results)).model_dump())

@bp.route("/product/<int:product_id>", methods=["GET"])
@login_required
def get_product_optimization_metrics(product_id: int):
    """
    Get optimization metrics for a specific product
    """
    db = get_db()
    metrics = optimization_engine.optimize_product(db, product_id)
    if not metrics:
        return jsonify({"detail": "Product not found"}), 404
        
    return jsonify(OptimizationMetrics(**metrics).model_dump())
