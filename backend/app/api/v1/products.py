from flask import Blueprint, request, jsonify
from typing import Optional, List
from ...models.database import get_db
from ...schemas.products import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse,
    StockAdjustment,
)
from ...services.product_service import ProductService
from ...core.security import login_required
from ...core.config import settings

bp = Blueprint("products", __name__)


@bp.route("", methods=["GET"])
@login_required
def get_products():
    """Get products with filtering and pagination"""
    db = get_db()
    
    # Extract query parameters
    try:
        skip = int(request.args.get("skip", 0))
        limit = int(request.args.get("limit", 20))
        query = request.args.get("query")
        category = request.args.get("category")
        low_stock_only = request.args.get("low_stock_only", "false").lower() == "true"
    except ValueError:
        return jsonify({"detail": "Invalid query parameters"}), 400

    products, total = ProductService.get_products(
        db, 
        skip=skip, 
        limit=limit, 
        category=category, 
        search=query, 
        low_stock_only=low_stock_only
    )

    # Enrich products with computed fields (Optimized: No AI in list)
    enriched_products = [
        ProductService.enrich_product_response(product, db, include_ai=False, include_forecast=False) 
        for product in products
    ]

    page = (skip // limit) + 1
    response_data = ProductListResponse(
        products=enriched_products,
        total=total,
        page=page,
        page_size=limit
    )
    return jsonify(response_data.model_dump())


@bp.route("/categories", methods=["GET"])
@login_required
def get_categories():
    """Get all product categories"""
    db = get_db()
    return jsonify(ProductService.get_categories(db))


@bp.route("/<int:product_id>", methods=["GET"])
@login_required
def get_product(product_id: int):
    """Get product by ID"""
    db = get_db()
    product = ProductService.get_product(db, product_id)
    if not product:
        return jsonify({"detail": "Product not found"}), 404
    enriched = ProductService.enrich_product_response(product, db, include_ai=True, include_forecast=True)
    return jsonify(ProductResponse.model_validate(enriched).model_dump())


@bp.route("", methods=["POST"])
@login_required
def create_product():
    """Create a new product"""
    db = get_db()
    try:
        product_data = ProductCreate(**request.json)
    except Exception as e:
        return jsonify({"detail": str(e)}), 400
        
    product = ProductService.create_product(db, product_data)
    enriched = ProductService.enrich_product_response(product, db, include_ai=True, include_forecast=True)
    return jsonify(ProductResponse.model_validate(enriched).model_dump()), 201


@bp.route("/<int:product_id>", methods=["PUT"])
@login_required
def update_product(product_id: int):
    """Update product"""
    db = get_db()
    try:
        product_data = ProductUpdate(**request.json)
    except Exception as e:
        return jsonify({"detail": str(e)}), 400
        
    product = ProductService.update_product(db, product_id, product_data)
    if not product:
        return jsonify({"detail": "Product not found"}), 404
        
    enriched = ProductService.enrich_product_response(product, db, include_ai=True, include_forecast=True)
    return jsonify(ProductResponse.model_validate(enriched).model_dump())


@bp.route("/<int:product_id>", methods=["DELETE"])
@login_required
def delete_product(product_id: int):
    """Delete product"""
    db = get_db()
    result = ProductService.delete_product(db, product_id)
    return jsonify(result)


@bp.route("/stock/adjust", methods=["POST"])
@login_required
def adjust_stock():
    """Adjust product stock"""
    db = get_db()
    try:
        adjustment_data = StockAdjustment(**request.json)
    except Exception as e:
        return jsonify({"detail": str(e)}), 400
        
    product = ProductService.adjust_stock(
        db, 
        adjustment_data.product_id, 
        adjustment_data.quantity, 
        adjustment_data.reason
    )
    if not product:
        return jsonify({"detail": "Product not found"}), 404
        
    enriched = ProductService.enrich_product_response(product, db, include_ai=False, include_forecast=False)
    return jsonify(ProductResponse.model_validate(enriched).model_dump())
