from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List

from ...models.database import get_db, Alert
from sqlalchemy import func
from ...schemas.alerts import (
    AlertCreate,
    AlertUpdate,
    AlertResponse,
    AlertListResponse,
    AlertSummary
)
from ...services.alert_service import AlertService
from ...core.security import get_current_user_id
from ...core.config import settings

router = APIRouter()


@router.get("", response_model=AlertListResponse)
def get_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=settings.MAX_PAGE_SIZE),
    unread_only: bool = False,
    unresolved_only: bool = False,
    severity: Optional[str] = None,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get alerts with filtering"""
    # Fetch alerts and total count from service
    alerts, total = AlertService.get_alerts(
        db,
        skip=skip,
        limit=limit,
        unread_only=unread_only,
        unresolved_only=unresolved_only,
        severity=severity
    )
    
    # Calculate extra counts for AlertListResponse
    unread_count = db.query(func.count(Alert.id)).filter(Alert.is_read == False).scalar()
    critical_count = db.query(func.count(Alert.id)).filter(Alert.severity == "critical").scalar()

    # Enrich alerts with product details
    enriched_alerts = []
    for alert in alerts:
        enriched_alerts.append(AlertResponse(
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
        ))

    page = (skip // limit) + 1
    return AlertListResponse(
        alerts=enriched_alerts,
        total=total,
        unread_count=unread_count,
        critical_count=critical_count,
        page=page,
        page_size=limit
    )


@router.get("/summary", response_model=AlertSummary)
def get_alert_summary(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get alert statistics"""
    return AlertService.get_alert_summary(db)


@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(
    alert_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get alert details"""
    return AlertService.get_alert(db, alert_id)


@router.post("", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
def create_alert(
    alert_data: AlertCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Create a manual alert"""
    return AlertService.create_alert(db, alert_data)


@router.put("/{alert_id}", response_model=AlertResponse)
def update_alert(
    alert_id: int,
    alert_data: AlertUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Update alert"""
    return AlertService.update_alert(db, alert_id, alert_data)


@router.post("/{alert_id}/read", response_model=AlertResponse)
def mark_alert_read(
    alert_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Mark alert as read"""
    return AlertService.mark_as_read(db, alert_id)


@router.post("/{alert_id}/resolve", response_model=AlertResponse)
def mark_alert_resolved(
    alert_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Mark alert as resolved"""
    return AlertService.mark_as_resolved(db, alert_id)


@router.delete("/{alert_id}")
def delete_alert(
    alert_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Delete alert"""
    return AlertService.delete_alert(db, alert_id)


@router.post("/check-all")
def trigger_alert_check(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Manually trigger alert check for all products"""
    return AlertService.check_all_products(db)
