import sys
import os
from sqlalchemy.orm import Session

# Force SQLite for local testing
from sqlalchemy import create_engine
engine = create_engine("sqlite:///./backend/inventory.db")
from backend.app.models.database import Product, Order, OrderItem, sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
from backend.app.ai.optimization.po_agent import po_agent
from backend.app.services.order_service import OrderService
from backend.app.schemas.orders import ReceiveOrder, ReceiveOrderItem

def test_restock():
    db = SessionLocal()
    try:
        print("Starting Autonomous Restock Test...")
        # Get a user ID (usually 1 or the first one)
        user_id = 1 
        
        # 1. Generate orders
        orders = po_agent.analyze_and_restock(db, user_id)
        print(f"Generated {len(orders)} orders.")
        
        for order in orders:
            print(f"Processing Order: {order.order_number} (ID: {order.id})")
            # 2. Transition to shipped
            order.status = "shipped"
            db.commit()
            db.refresh(order)
            
            # 3. Try to receive
            receive_data = ReceiveOrder(
                items=[ReceiveOrderItem(order_item_id=item.id, received_quantity=item.quantity) for item in order.items],
                notes="Test auto-receive"
            )
            print(f"Attempting to receive order {order.id}...")
            OrderService.receive_order(db, order.id, receive_data)
            print(f"Order {order.id} received successfully.")
            
    except Exception as e:
        print(f"TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_restock()
