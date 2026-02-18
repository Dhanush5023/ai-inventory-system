from sqlalchemy.orm import Session
from datetime import datetime
import uuid
from typing import List, Dict, Any

from ...models.database import Product, Order, OrderItem, Supplier
from ..optimization.engine import optimization_engine

class POAgent:
    """AI Agent for autonomous Purchase Order generation"""
    
    def analyze_and_restock(self, db: Session, user_id: int = None) -> List[Order]:
        """Analyze all products and generate POs for those below reorder point"""
        products = db.query(Product).all()
        print(f"[DEBUG] POAgent: Analyzing {len(products)} products for restocking...")
        generated_orders = []
        
        # Group products by supplier for efficient ordering
        supplier_orders: Dict[int, List[Dict[str, Any]]] = {}
        
        for product in products:
            # Calculate total inbound quantity from active (draft/pending/shipped) orders
            inbound_items = db.query(OrderItem).join(Order).filter(
                OrderItem.product_id == product.id,
                Order.status.in_(["draft", "pending", "shipped"])
            ).all()
            
            inbound_qty = sum(item.quantity for item in inbound_items)
            total_projected_stock = product.current_stock + inbound_qty

            metrics = optimization_engine.optimize_product(db, product.id)
            reorder_point = metrics['reorder_point']

            if total_projected_stock <= reorder_point:
                # Needs restocking or supplementary restocking
                if inbound_qty > 0:
                    print(f"[DEBUG] POAgent: Product '{product.name}' (Stock: {product.current_stock}, Inbound: {inbound_qty}, ROP: {reorder_point}) still below ROP. Triggering supplementary order.")
                
                supplier_id = product.supplier_id
                if not supplier_id:
                    continue # Skip products with no supplier
                
                if supplier_id not in supplier_orders:
                    supplier_orders[supplier_id] = []
                    
                print(f"[DEBUG] POAgent: Product '{product.name}' (Stock: {product.current_stock}, ROP: {metrics['reorder_point']}) NEEDS RESTOCK. Suggesting {metrics['eoq']} units.")
                supplier_orders[supplier_id].append({
                    "product": product,
                    "quantity": int(metrics['eoq'])
                })
            else:
                if product.current_stock <= product.minimum_stock * 1.5:  # Log near-misses
                    print(f"[DEBUG] POAgent: Product '{product.name}' (Stock: {product.current_stock}, ROP: {metrics['reorder_point']}) - Stock OK.")
        
        # Create Orders for each supplier
        for supplier_id, items in supplier_orders.items():
            supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
            if not supplier:
                continue
                
            total_amount = sum(item['product'].cost_price * item['quantity'] for item in items)
            
            order = Order(
                order_number=f"PO-{uuid.uuid4().hex[:8].upper()}",
                supplier_id=supplier_id,
                user_id=user_id,
                order_date=datetime.utcnow(),
                total_amount=total_amount,
                status="draft", # Starts as draft for approval
                notes=f"AI-Generated Autorestock: {datetime.now().strftime('%Y-%m-%d')}"
            )
            db.add(order)
            db.flush() # Get order ID
            
            for item in items:
                order_item = OrderItem(
                    product_id=item['product'].id,
                    quantity=item['quantity'],
                    unit_price=item['product'].cost_price,
                    total_price=item['product'].cost_price * item['quantity']
                )
                order.items.append(order_item)
            
            db.add(order)
            db.flush() # Ensure order and items have IDs for autonomous receiving swept away by the 404s
            
            generated_orders.append(order)
            
        db.commit()
        print(f"[DEBUG] POAgent: Restock analysis complete. Generated {len(generated_orders)} POs.")
        return generated_orders

# Global instance
po_agent = POAgent()
