from flask import abort
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List, Tuple
from datetime import datetime, timedelta

from ..models.database import Order, OrderItem, Product, Supplier
from ..schemas.orders import OrderCreate, OrderUpdate, OrderFilter, ReceiveOrder
import random
import string


class OrderService:
    """Purchase order management service layer"""

    @staticmethod
    def generate_order_number() -> str:
        """Generate unique order number"""
        prefix = "PO"
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        random_suffix = ''.join(random.choices(string.digits, k=4))
        return f"{prefix}-{timestamp}-{random_suffix}"

    @staticmethod
    def create_order(db: Session, order_data: OrderCreate, user_id: int) -> Order:
        """Create a new purchase order"""
        # Verify supplier exists
        supplier = db.query(Supplier).filter(Supplier.id == order_data.supplier_id).first()
        if not supplier:
            abort(404, description="Supplier not found")

        # Generate unique order number
        order_number = OrderService.generate_order_number()

        # Create order
        order = Order(
            order_number=order_number,
            supplier_id=order_data.supplier_id,
            user_id=user_id,
            expected_delivery=order_data.expected_delivery,
            notes=order_data.notes,
        )

        db.add(order)
        db.flush()  # Get order ID

        # Create order items
        total_amount = 0.0
        for item_data in order_data.items:
            # Verify product exists
            product = db.query(Product).filter(Product.id == item_data.product_id).first()
            if not product:
                db.rollback()
                abort(404, description=f"Product ID {item_data.product_id} not found")

            total_price = item_data.quantity * item_data.unit_price
            total_amount += total_price

            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                unit_price=item_data.unit_price,
                total_price=total_price,
            )
            db.add(order_item)

        order.total_amount = total_amount

        db.commit()
        db.refresh(order)
        return order

    @staticmethod
    def get_order(db: Session, order_id: int) -> Order:
        """Get order by ID"""
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            abort(404, description="Order not found")
        return order

    @staticmethod
    def get_orders(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        filters: Optional[OrderFilter] = None
    ) -> Tuple[List[Order], int]:
        """Get orders with pagination and filtering"""
        query = db.query(Order)

        # Apply filters
        if filters:
            if filters.status:
                query = query.filter(Order.status == filters.status)

            if filters.supplier_id:
                query = query.filter(Order.supplier_id == filters.supplier_id)

            if filters.start_date:
                query = query.filter(Order.order_date >= filters.start_date)

            if filters.end_date:
                query = query.filter(Order.order_date <= filters.end_date)

        total = query.count()
        orders = query.order_by(Order.order_date.desc()).offset(skip).limit(limit).all()

        return orders, total

    @staticmethod
    def update_order(db: Session, order_id: int, order_data: OrderUpdate) -> Order:
        """Update order"""
        order = OrderService.get_order(db, order_id)

        # Prevent updates to received or cancelled orders
        if order.status in ["received", "cancelled"]:
            abort(400, description=f"Cannot update order with status '{order.status}'")

        # Update fields
        update_data = order_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(order, field, value)

        db.commit()
        db.refresh(order)
        return order

    @staticmethod
    def update_order_status(db: Session, order_id: int, new_status: str) -> Order:
        """Update order status"""
        order = OrderService.get_order(db, order_id)

        # Status transition validation
        valid_transitions = {
            "draft": ["pending", "approved", "cancelled"],
            "pending": ["approved", "cancelled"],
            "approved": ["shipped", "cancelled"],
            "shipped": ["received", "cancelled"],
            "received": [],
            "cancelled": [],
        }

        if new_status not in valid_transitions.get(order.status, []):
            abort(400, description=f"Cannot transition from '{order.status}' to '{new_status}'")

        order.status = new_status

        # Set received date if status is received
        if new_status == "received":
            order.received_date = datetime.utcnow()

        db.commit()
        db.refresh(order)
        return order

    @staticmethod
    def receive_order(db: Session, order_id: int, receive_data: ReceiveOrder) -> Order:
        """Receive order and update inventory"""
        order = OrderService.get_order(db, order_id)

        if order.status != "shipped":
            abort(400, description="Only shipped orders can be received")

        # Process received items
        for item in receive_data.items:
            # Get order item
            order_item = db.query(OrderItem).filter(
                OrderItem.id == item.order_item_id,
                OrderItem.order_id == order_id
            ).first()

            if not order_item:
                abort(404, description=f"Order item {item.order_item_id} not found")

            if item.received_quantity > order_item.quantity:
                abort(400, description=f"Received quantity cannot exceed ordered quantity for item {item.order_item_id}")

            # Update product stock
            product = db.query(Product).filter(Product.id == order_item.product_id).first()
            if product:
                product.current_stock += item.received_quantity

        # Update order status
        order.status = "received"
        order.received_date = datetime.utcnow()
        if receive_data.notes:
            order.notes = f"{order.notes}\nReceiving notes: {receive_data.notes}" if order.notes else receive_data.notes

        db.commit()
        db.refresh(order)
        return order

    @staticmethod
    def delete_order(db: Session, order_id: int) -> None:
        """Delete order (only if pending)"""
        order = OrderService.get_order(db, order_id)

        if order.status != "pending":
            abort(400, description="Only pending orders can be deleted")

        db.delete(order)
        db.commit()
