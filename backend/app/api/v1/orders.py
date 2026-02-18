from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
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
from ...core.security import get_current_user_id
from ...core.config import settings

router = APIRouter()


@router.get("", response_model=OrderListResponse)
def get_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=settings.MAX_PAGE_SIZE),
    status_filter: Optional[str] = Query(None, alias="status"),
    supplier_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get orders with filtering and pagination"""
    filters = OrderFilter(
        status=status_filter,
        supplier_id=supplier_id,
        start_date=start_date,
        end_date=end_date,
    )

    orders, total = OrderService.get_orders(db, skip, limit, filters)

    # Enrich orders
    orders_response = []
    for order in orders:
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

        orders_response.append(OrderResponse(
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
        ))

    page = (skip // limit) + 1
    return OrderListResponse(
        orders=orders_response,
        total=total,
        page=page,
        page_size=limit
    )


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get order by ID"""
    order = OrderService.get_order(db, order_id)

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


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: OrderCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Create a new purchase order"""
    order = OrderService.create_order(db, order_data, user_id)

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


@router.put("/{order_id}", response_model=OrderResponse)
def update_order(
    order_id: int,
    order_data: OrderUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Update order"""
    order = OrderService.update_order(db, order_id, order_data)

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


@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Update order status"""
    order = OrderService.update_order_status(db, order_id, status_update.status)

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


@router.post("/{order_id}/receive", response_model=OrderResponse)
def receive_order(
    order_id: int,
    receive_data: ReceiveOrder,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Receive order and update inventory"""
    order = OrderService.receive_order(db, order_id, receive_data)

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


@router.delete("/{order_id}")
def delete_order(
    order_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Delete order (only pending)"""
    OrderService.delete_order(db, order_id)
    return {"message": "Order deleted successfully"}
