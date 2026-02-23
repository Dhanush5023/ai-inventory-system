from flask import Blueprint, request, jsonify
from typing import Optional
from datetime import datetime
from ...models.database import get_db
from ...schemas.orders import (
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    OrderListResponse,
    OrderFilter,
    OrderStatusUpdate,
    ReceiveOrder,
    OrderItemResponse,
)
from ...services.order_service import OrderService
from ...core.security import login_required, get_current_user_id

bp = Blueprint("orders", __name__)


def enrich_order(order):
    """Helper to enrich order response"""
    items = [
        OrderItemResponse(
            id=item.id,
            order_id=item.order_id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            total_price=item.total_price,
            product_name=item.product.name if item.product else None,
            product_sku=item.product.sku if item.product else None,
        )
        for item in order.items
    ]

    return OrderResponse(
        id=order.id,
        order_number=order.order_number,
        supplier_id=order.supplier_id,
        user_id=order.user_id,
        status=order.status,
        total_amount=order.total_amount,
        order_date=order.order_date,
        expected_delivery=order.expected_delivery,
        received_date=order.received_date,
        notes=order.notes,
        supplier_name=order.supplier.name if order.supplier else None,
        username=order.user.username if order.user else None,
        items=items,
    )


@bp.route("", methods=["GET"])
@login_required
def get_orders():
    """Get orders with filtering and pagination"""
    db = get_db()
    
    try:
        skip = int(request.args.get("skip", 0))
        limit = int(request.args.get("limit", 20))
        status_filter = request.args.get("status")
        supplier_id = request.args.get("supplier_id")
        if supplier_id:
            supplier_id = int(supplier_id)
            
        start_date_str = request.args.get("start_date")
        start_date = datetime.fromisoformat(start_date_str) if start_date_str else None
        
        end_date_str = request.args.get("end_date")
        end_date = datetime.fromisoformat(end_date_str) if end_date_str else None
    except ValueError:
        return jsonify({"detail": "Invalid query parameters"}), 400

    filters = OrderFilter(
        status=status_filter,
        supplier_id=supplier_id,
        start_date=start_date,
        end_date=end_date,
    )

    orders, total = OrderService.get_orders(db, skip, limit, filters)

    orders_response = [enrich_order(order).model_dump() for order in orders]

    page = (skip // limit) + 1
    response_data = OrderListResponse(
        orders=orders_response,
        total=total,
        page=page,
        page_size=limit
    )
    return jsonify(response_data.model_dump())


@bp.route("/<int:order_id>", methods=["GET"])
@login_required
def get_order(order_id: int):
    """Get order by ID"""
    db = get_db()
    order = OrderService.get_order(db, order_id)
    if not order:
        return jsonify({"detail": "Order not found"}), 404
    return jsonify(enrich_order(order).model_dump())


@bp.route("", methods=["POST"])
@login_required
def create_order():
    """Create a new purchase order"""
    db = get_db()
    user_id = get_current_user_id()
    try:
        order_data = OrderCreate(**request.json)
    except Exception as e:
        return jsonify({"detail": str(e)}), 400
        
    order = OrderService.create_order(db, order_data, user_id)
    return jsonify(enrich_order(order).model_dump()), 201


@bp.route("/<int:order_id>", methods=["PUT"])
@login_required
def update_order(order_id: int):
    """Update order"""
    db = get_db()
    try:
        order_data = OrderUpdate(**request.json)
    except Exception as e:
        return jsonify({"detail": str(e)}), 400
        
    order = OrderService.update_order(db, order_id, order_data)
    if not order:
        return jsonify({"detail": "Order not found"}), 404
    return jsonify(enrich_order(order).model_dump())


@bp.route("/<int:order_id>/status", methods=["PATCH"])
@login_required
def update_order_status(order_id: int):
    """Update order status"""
    db = get_db()
    try:
        status_update = OrderStatusUpdate(**request.json)
    except Exception as e:
        return jsonify({"detail": str(e)}), 400
        
    order = OrderService.update_order_status(db, order_id, status_update.status)
    if not order:
        return jsonify({"detail": "Order not found"}), 404
    return jsonify(enrich_order(order).model_dump())


@bp.route("/<int:order_id>/receive", methods=["POST"])
@login_required
def receive_order(order_id: int):
    """Receive order and update inventory"""
    db = get_db()
    try:
        receive_data = ReceiveOrder(**request.json)
    except Exception as e:
        return jsonify({"detail": str(e)}), 400
        
    order = OrderService.receive_order(db, order_id, receive_data)
    if not order:
        return jsonify({"detail": "Order not found"}), 404
    return jsonify(enrich_order(order).model_dump())


@bp.route("/<int:order_id>", methods=["DELETE"])
@login_required
def delete_order(order_id: int):
    """Delete order (only pending)"""
    db = get_db()
    OrderService.delete_order(db, order_id)
    return jsonify({"message": "Order deleted successfully"})
