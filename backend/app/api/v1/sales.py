from flask import Blueprint, request, jsonify
from sqlalchemy import func
from typing import Optional, List
from datetime import datetime
from ...models.database import get_db, Sale
from ...schemas.sales import (
    SaleCreate,
    SaleUpdate,
    SaleResponse,
    SaleListResponse,
    SalesSummary,
    BulkSaleCreate
)
from ...services.sales_service import SalesService
from ...core.security import login_required, get_current_user_id

bp = Blueprint("sales", __name__)


@bp.route("", methods=["GET"])
@login_required
def get_sales():
    """Get sales history with filtering"""
    db = get_db()
    
    try:
        skip = int(request.args.get("skip", 0))
        limit = int(request.args.get("limit", 20))
        product_id = request.args.get("product_id")
        if product_id:
            product_id = int(product_id)
            
        start_date_str = request.args.get("start_date")
        start_date = datetime.fromisoformat(start_date_str) if start_date_str else None
        
        end_date_str = request.args.get("end_date")
        end_date = datetime.fromisoformat(end_date_str) if end_date_str else None
    except ValueError:
        return jsonify({"detail": "Invalid query parameters"}), 400

    sales, total = SalesService.get_sales(
        db,
        skip=skip,
        limit=limit,
        product_id=product_id,
        start_date=start_date,
        end_date=end_date
    )

    # Calculate total revenue
    total_rev_query = db.query(func.sum(Sale.total_amount))
    if product_id:
        total_rev_query = total_rev_query.filter(Sale.product_id == product_id)
    if start_date:
        total_rev_query = total_rev_query.filter(Sale.sale_date >= start_date)
    if end_date:
        total_rev_query = total_rev_query.filter(Sale.sale_date <= end_date)
    
    total_revenue = total_rev_query.scalar() or 0.0

    # Enrich sales
    enriched_sales = []
    for sale in sales:
        enriched_sales.append(SaleResponse(
            id=sale.id,
            product_id=sale.product_id,
            user_id=sale.user_id,
            quantity=sale.quantity,
            unit_price=sale.unit_price,
            total_amount=sale.total_amount,
            sale_date=sale.sale_date,
            notes=sale.notes,
            product_name=sale.product.name if sale.product else "Unknown",
            username=sale.user.username if sale.user else "System"
        ))
    
    page = (skip // limit) + 1
    response_data = SaleListResponse(
        sales=enriched_sales,
        total=total,
        page=page,
        page_size=limit,
        total_revenue=total_revenue
    )
    return jsonify(response_data.model_dump())


@bp.route("/<int:sale_id>", methods=["GET"])
@login_required
def get_sale(sale_id: int):
    """Get sale details"""
    db = get_db()
    sale = SalesService.get_sale(db, sale_id)
    if not sale:
        return jsonify({"detail": "Sale not found"}), 404
    return jsonify(SaleResponse.model_validate(sale).model_dump())


@bp.route("", methods=["POST"])
@login_required
def create_sale():
    """Record a new sale"""
    db = get_db()
    user_id = get_current_user_id()
    try:
        sale_data = SaleCreate(**request.json)
    except Exception as e:
        return jsonify({"detail": str(e)}), 400
        
    sale = SalesService.create_sale(db, sale_data, user_id)
    return jsonify(SaleResponse.model_validate(sale).model_dump()), 201


@bp.route("/bulk", methods=["POST"])
@login_required
def create_bulk_sales():
    """Record multiple sales (POS transaction)"""
    db = get_db()
    user_id = get_current_user_id()
    try:
        bulk_data = BulkSaleCreate(**request.json)
    except Exception as e:
        return jsonify({"detail": str(e)}), 400
        
    sales = SalesService.create_bulk_sales(db, bulk_data.items, user_id)
    
    enriched = []
    for s in sales:
        enriched.append(SaleResponse(
            id=s.id,
            product_id=s.product_id,
            user_id=s.user_id,
            quantity=s.quantity,
            unit_price=s.unit_price,
            total_amount=s.total_amount,
            sale_date=s.sale_date,
            notes=s.notes,
            product_name=s.product.name if s.product else "Unknown",
            username=s.user.username if s.user else "System"
        ).model_dump())
    
    return jsonify(enriched), 201


@bp.route("/<int:sale_id>", methods=["PUT"])
@login_required
def update_sale(sale_id: int):
    """Update sale record"""
    db = get_db()
    try:
        sale_data = SaleUpdate(**request.json)
    except Exception as e:
        return jsonify({"detail": str(e)}), 400
        
    sale = SalesService.update_sale(db, sale_id, sale_data)
    if not sale:
        return jsonify({"detail": "Sale not found"}), 404
    return jsonify(SaleResponse.model_validate(sale).model_dump())


@bp.route("/<int:sale_id>", methods=["DELETE"])
@login_required
def delete_sale(sale_id: int):
    """Delete sale record (restores stock)"""
    db = get_db()
    result = SalesService.delete_sale(db, sale_id)
    return jsonify(result)


@bp.route("/stats/summary", methods=["GET"])
@login_required
def get_sales_summary():
    """Get sales summary statistics"""
    db = get_db()
    days = int(request.args.get("days", 30))
    summary = SalesService.get_sales_summary(db, days)
    return jsonify(SalesSummary.model_validate(summary).model_dump())


@bp.route("/stats/top-products", methods=["GET"])
@login_required
def get_top_products():
    """Get top selling products"""
    db = get_db()
    limit = int(request.args.get("limit", 10))
    days = int(request.args.get("days", 30))
    return jsonify(SalesService.get_top_products(db, limit, days))


@bp.route("/stats/daily", methods=["GET"])
@login_required
def get_daily_sales():
    """Get daily sales trend"""
    db = get_db()
    days = int(request.args.get("days", 30))
    return jsonify(SalesService.get_sales_by_date(db, days))


@bp.route("/stats/by-category", methods=["GET"])
@login_required
def get_category_sales():
    """Get sales distribution by category"""
    db = get_db()
    days = int(request.args.get("days", 30))
    return jsonify(SalesService.get_sales_by_category(db, days))
