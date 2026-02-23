from flask import Blueprint, request, jsonify
from typing import Optional, List
from sqlalchemy import func
from ...models.database import get_db, Alert
from ...schemas.alerts import (
    AlertCreate,
    AlertUpdate,
    AlertResponse,
    AlertListResponse,
    AlertSummary
)
from ...services.alert_service import AlertService
from ...core.security import login_required

bp = Blueprint("alerts", __name__)


@bp.route("", methods=["GET"])
@login_required
def get_alerts():
    """Get alerts with filtering"""
    db = get_db()
    
    try:
        skip = int(request.args.get("skip", 0))
        limit = int(request.args.get("limit", 20))
        unread_only = request.args.get("unread_only", "false").lower() == "true"
        unresolved_only = request.args.get("unresolved_only", "false").lower() == "true"
        severity = request.args.get("severity")
    except ValueError:
        return jsonify({"detail": "Invalid query parameters"}), 400

    alerts, total = AlertService.get_alerts(
        db,
        skip=skip,
        limit=limit,
        unread_only=unread_only,
        unresolved_only=unresolved_only,
        severity=severity
    )
    
    unread_count = db.query(func.count(Alert.id)).filter(Alert.is_read == False).scalar()
    critical_count = db.query(func.count(Alert.id)).filter(Alert.severity == "critical").scalar()

    enriched_alerts = [
        AlertResponse(
            id=alert.id,
            product_id=alert.product_id,
            alert_type=alert.alert_type,
            message=alert.message,
            severity=alert.severity,
            recommended_quantity=alert.recommended_quantity,
            is_read=alert.is_read,
            is_resolved=alert.is_resolved,
            created_at=alert.created_at,
            resolved_at=alert.resolved_at,
            product_name=alert.product.name if alert.product else "Unknown",
            product_sku=alert.product.sku if alert.product else "Unknown",
            current_stock=alert.product.current_stock if alert.product else 0
        ).model_dump()
        for alert in alerts
    ]

    page = (skip // limit) + 1
    response_data = AlertListResponse(
        alerts=enriched_alerts,
        total=total,
        unread_count=unread_count,
        critical_count=critical_count,
        page=page,
        page_size=limit
    )
    return jsonify(response_data.model_dump())


@bp.route("/summary", methods=["GET"])
@login_required
def get_alert_summary():
    """Get alert statistics"""
    db = get_db()
    summary = AlertService.get_alert_summary(db)
    return jsonify(AlertSummary.model_validate(summary).model_dump())


@bp.route("/<int:alert_id>", methods=["GET"])
@login_required
def get_alert(alert_id: int):
    """Get alert details"""
    db = get_db()
    alert = AlertService.get_alert(db, alert_id)
    if not alert:
        return jsonify({"detail": "Alert not found"}), 404
        
    enriched = AlertResponse(
        id=alert.id,
        product_id=alert.product_id,
        alert_type=alert.alert_type,
        message=alert.message,
        severity=alert.severity,
        recommended_quantity=alert.recommended_quantity,
        is_read=alert.is_read,
        is_resolved=alert.is_resolved,
        created_at=alert.created_at,
        resolved_at=alert.resolved_at,
        product_name=alert.product.name if alert.product else "Unknown",
        product_sku=alert.product.sku if alert.product else "Unknown",
        current_stock=alert.product.current_stock if alert.product else 0
    )
    return jsonify(enriched.model_dump())


@bp.route("", methods=["POST"])
@login_required
def create_alert():
    """Create a manual alert"""
    db = get_db()
    try:
        alert_data = AlertCreate(**request.json)
    except Exception as e:
        return jsonify({"detail": str(e)}), 400
        
    alert = AlertService.create_alert(db, alert_data)
    return jsonify(AlertResponse.model_validate(alert).model_dump()), 201


@bp.route("/<int:alert_id>", methods=["PUT"])
@login_required
def update_alert(alert_id: int):
    """Update alert"""
    db = get_db()
    try:
        alert_data = AlertUpdate(**request.json)
    except Exception as e:
        return jsonify({"detail": str(e)}), 400
        
    alert = AlertService.update_alert(db, alert_id, alert_data)
    if not alert:
        return jsonify({"detail": "Alert not found"}), 404
    return jsonify(AlertResponse.model_validate(alert).model_dump())


@bp.route("/<int:alert_id>/read", methods=["POST"])
@login_required
def mark_alert_read(alert_id: int):
    """Mark alert as read"""
    db = get_db()
    alert = AlertService.mark_as_read(db, alert_id)
    if not alert:
        return jsonify({"detail": "Alert not found"}), 404
    return jsonify(AlertResponse.model_validate(alert).model_dump())


@bp.route("/<int:alert_id>/resolve", methods=["POST"])
@login_required
def mark_alert_resolved(alert_id: int):
    """Mark alert as resolved"""
    db = get_db()
    alert = AlertService.mark_as_resolved(db, alert_id)
    if not alert:
        return jsonify({"detail": "Alert not found"}), 404
    return jsonify(AlertResponse.model_validate(alert).model_dump())


@bp.route("/<int:alert_id>", methods=["DELETE"])
@login_required
def delete_alert(alert_id: int):
    """Delete alert"""
    db = get_db()
    result = AlertService.delete_alert(db, alert_id)
    return jsonify(result)


@bp.route("/check-all", methods=["POST"])
@login_required
def trigger_alert_check():
    """Manually trigger alert check for all products"""
    db = get_db()
    return jsonify(AlertService.check_all_products(db))
