from flask import Blueprint, request, jsonify
from ...models.database import get_db
from ...ai.optimization.po_agent import po_agent
from ...ai.risk.supplier_risk import risk_predictor
from ...core.security import login_required, get_current_user_id
import asyncio

bp = Blueprint("autonomous", __name__)

@bp.route("/restock/generate", methods=["POST"])
@login_required
def generate_restock_orders():
    """
    Trigger AI Agent to analyze stock and generate draft POs
    """
    db = get_db()
    user_id = get_current_user_id()
    auto_receive = request.args.get("auto_receive", "false").lower() == "true"
    
    try:
        # Run async function in sync Flask route
        orders = asyncio.run(po_agent.analyze_and_restock(db, user_id))
        print(f"[DEBUG] AI Restock: Generated {len(orders)} orders. auto_receive={auto_receive}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"detail": f"AI Agent Failure: {str(e)}"}), 500
    
    if auto_receive:
        print(f"[DEBUG] AI Restock: Starting auto-receive for {len(orders)} orders")
        from ...services.order_service import OrderService
        from ...schemas.orders import ReceiveOrder, ReceiveOrderItem
        
        for order in orders:
            try:
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
                continue
            
    return jsonify({
        "status": "success",
        "message": f"Generated {len(orders)} {'and received ' if auto_receive else ''}purchase orders",
        "count": len(orders),
        "order_ids": [o.id for o in orders]
    })


@bp.route("/risk/suppliers", methods=["GET"])
@login_required
def get_all_supplier_risks():
    """
    Get AI-predicted risk assessment for ALL suppliers
    """
    db = get_db()
    risks = risk_predictor.analyze_all_suppliers(db)
    return jsonify({
        "count": len(risks),
        "risks": risks
    })

@bp.route("/risk/supplier/<int:supplier_id>", methods=["GET"])
@login_required
def get_supplier_risk(supplier_id: int):
    """
    Get AI-predicted risk assessment for a supplier
    """
    db = get_db()
    risk = risk_predictor.predict_risk(db, supplier_id)
    if not risk:
        return jsonify({"detail": "Supplier not found"}), 404
    return jsonify(risk)
