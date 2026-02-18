from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...models.database import get_db
from ...ai.optimization.po_agent import po_agent
from ...ai.risk.supplier_risk import risk_predictor
from ...core.security import get_current_user_id

router = APIRouter()

@router.post("/restock/generate")
async def generate_restock_orders(
    auto_receive: bool = False,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Trigger AI Agent to analyze stock and generate draft POs
    """
    try:
        orders = po_agent.analyze_and_restock(db, user_id)
        print(f"[DEBUG] AI Restock: Generated {len(orders)} orders. auto_receive={auto_receive}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"AI Agent Failure: {str(e)}")
    
    if auto_receive:
        print(f"[DEBUG] AI Restock: Starting auto-receive for {len(orders)} orders")
        from ...services.order_service import OrderService
        from ...schemas.orders import ReceiveOrder, ReceiveOrderItem
        
        for order in orders:
            try:
                # Transition to shipped first to allow receiving
                order.status = "shipped"
                db.commit()
                db.refresh(order)
                
                receive_data = ReceiveOrder(
                    items=[ReceiveOrderItem(order_item_id=item.id, received_quantity=item.quantity) for item in order.items],
                    notes="Auto-received by AI Agent"
                )
                print(f"[DEBUG] AI Restock: Receiving order {order.id} ({order.order_number}) with {len(order.items)} items")
                OrderService.receive_order(db, order.id, receive_data)
                print(f"[DEBUG] AI Restock: Order {order.id} received successfully")
            except Exception as e:
                print(f"[ERROR] AI Restock: Failed to auto-receive order {order.id}: {e}")
                db.rollback()
                continue # Try next order swept away by the 404s
            
    return {
        "status": "success",
        "message": f"Generated {len(orders)} {'and received ' if auto_receive else ''}purchase orders",
        "count": len(orders),
        "order_ids": [o.id for o in orders]
    }



@router.get("/risk/suppliers")
def get_all_supplier_risks(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get AI-predicted risk assessment for ALL suppliers
    """
    risks = risk_predictor.analyze_all_suppliers(db)
    return {
        "count": len(risks),
        "risks": risks
    }

@router.get("/risk/supplier/{supplier_id}")
def get_supplier_risk(
    supplier_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get AI-predicted risk assessment for a supplier
    """
    risk = risk_predictor.predict_risk(db, supplier_id)
    if not risk:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return risk
