from flask import abort
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional, Dict
from datetime import datetime, timedelta

from ..models.database import Alert, Product, Prediction
from ..schemas.alerts import AlertCreate, AlertUpdate


class AlertService:
    """Alert management service"""
    
    @staticmethod
    def create_alert(db: Session, alert_data: AlertCreate) -> Alert:
        """Create a manual alert"""
        # Verify product exists
        product = db.query(Product).filter(Product.id == alert_data.product_id).first()
        if not product:
            abort(404, description="Product not found")
        
        new_alert = Alert(**alert_data.model_dump())
        
        try:
            db.add(new_alert)
            db.commit()
            db.refresh(new_alert)
            return new_alert
        except Exception as e:
            db.rollback()
            abort(400, description=f"Failed to create alert: {str(e)}")
    
    @staticmethod
    def get_alert(db: Session, alert_id: int) -> Alert:
        """Get alert by ID"""
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            abort(404, description="Alert not found")
        return alert
    
    @staticmethod
    def get_alerts(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        unread_only: bool = False,
        unresolved_only: bool = False,
        severity: Optional[str] = None
    ) -> tuple[List[Alert], int]:
        """
        Get alerts with filtering
        
        Returns:
            (alerts, total_count)
        """
        query = db.query(Alert)
        
        if unread_only:
            query = query.filter(Alert.is_read == False)
        
        if unresolved_only:
            query = query.filter(Alert.is_resolved == False)
        
        if severity:
            query = query.filter(Alert.severity == severity)
        
        # Order by severity and date
        severity_order = {
            'critical': 0,
            'high': 1,
            'medium': 2,
            'low': 3
        }
        
        query = query.order_by(Alert.created_at.desc())
        
        total = query.count()
        alerts = query.offset(skip).limit(limit).all()
        
        return alerts, total
    
    @staticmethod
    def update_alert(db: Session, alert_id: int, alert_data: AlertUpdate) -> Alert:
        """Update alert"""
        alert = AlertService.get_alert(db, alert_id)
        
        update_data = alert_data.model_dump(exclude_unset=True)
        
        # Set resolved_at if marking as resolved
        if 'is_resolved' in update_data and update_data['is_resolved'] and not alert.is_resolved:
            alert.resolved_at = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(alert, field, value)
        
        try:
            db.commit()
            db.refresh(alert)
            return alert
        except Exception as e:
            db.rollback()
            abort(400, description=f"Failed to update alert: {str(e)}")
    
    @staticmethod
    def mark_as_read(db: Session, alert_id: int) -> Alert:
        """Mark alert as read"""
        alert = AlertService.get_alert(db, alert_id)
        alert.is_read = True
        db.commit()
        db.refresh(alert)
        return alert
    
    @staticmethod
    def mark_as_resolved(db: Session, alert_id: int) -> Alert:
        """Mark alert as resolved"""
        alert = AlertService.get_alert(db, alert_id)
        alert.is_resolved = True
        alert.resolved_at = datetime.utcnow()
        db.commit()
        db.refresh(alert)
        return alert
    
    @staticmethod
    def delete_alert(db: Session, alert_id: int) -> dict:
        """Delete alert"""
        alert = AlertService.get_alert(db, alert_id)
        
        try:
            db.delete(alert)
            db.commit()
            return {"message": "Alert deleted successfully"}
        except Exception as e:
            db.rollback()
            abort(400, description=f"Failed to delete alert: {str(e)}")
    
    @staticmethod
    def check_product_stock(db: Session, product: Product) -> Optional[Alert]:
        """
        Check if product needs stock alert
        
        Returns:
            Created alert or None
        """
        # Check if alert already exists for this product
        existing_alert = db.query(Alert).filter(
            and_(
                Alert.product_id == product.id,
                Alert.is_resolved == False
            )
        ).first()
        
        if existing_alert:
            return None  # Don't create duplicate alerts
        
        # Determine alert type and severity
        alert_type = None
        severity = None
        message = None
        recommended_quantity = None
        
        if product.current_stock == 0:
            alert_type = "out_of_stock"
            severity = "critical"
            message = f"Product '{product.name}' is OUT OF STOCK!"
            recommended_quantity = product.minimum_stock * 2
        
        elif product.current_stock <= product.minimum_stock * 0.5:
            alert_type = "restock_needed"
            severity = "high"
            message = f"Product '{product.name}' stock is critically low ({product.current_stock} units). Immediate restocking required."
            recommended_quantity = product.maximum_stock
        
        elif product.current_stock <= product.minimum_stock:
            alert_type = "low_stock"
            severity = "medium"
            message = f"Product '{product.name}' stock is below minimum level ({product.current_stock}/{product.minimum_stock} units)."
            recommended_quantity = product.maximum_stock - product.current_stock
        
        if alert_type:
            # Check predictions for better recommendation
            prediction = db.query(Prediction).filter(
                Prediction.product_id == product.id,
                Prediction.target_date >= datetime.utcnow()
            ).order_by(Prediction.target_date.asc()).first()
            
            if prediction and prediction.recommended_stock:
                recommended_quantity = prediction.recommended_stock
            
            # Create alert
            alert = Alert(
                product_id=product.id,
                alert_type=alert_type,
                message=message,
                severity=severity,
                recommended_quantity=recommended_quantity
            )
            
            db.add(alert)
            db.commit()
            db.refresh(alert)
            
            return alert
        
        return None
    
    @staticmethod
    def check_all_products(db: Session) -> Dict[str, int]:
        """
        Check all products and generate alerts
        
        Returns:
            Statistics about generated alerts
        """
        products = db.query(Product).all()
        
        stats = {
            'total_products': len(products),
            'alerts_generated': 0,
            'critical_alerts': 0,
            'high_alerts': 0,
            'medium_alerts': 0
        }
        
        for product in products:
            alert = AlertService.check_product_stock(db, product)
            if alert:
                stats['alerts_generated'] += 1
                if alert.severity == 'critical':
                    stats['critical_alerts'] += 1
                elif alert.severity == 'high':
                    stats['high_alerts'] += 1
                elif alert.severity == 'medium':
                    stats['medium_alerts'] += 1
        
        return stats
    
    @staticmethod
    def get_alert_summary(db: Session) -> Dict:
        """Get alert statistics"""
        total = db.query(Alert).count()
        unread = db.query(Alert).filter(Alert.is_read == False).count()
        unresolved = db.query(Alert).filter(Alert.is_resolved == False).count()
        
        critical = db.query(Alert).filter(
            and_(Alert.severity == 'critical', Alert.is_resolved == False)
        ).count()
        
        high = db.query(Alert).filter(
            and_(Alert.severity == 'high', Alert.is_resolved == False)
        ).count()
        
        return {
            'total_alerts': total,
            'unread_alerts': unread,
            'unresolved_alerts': unresolved,
            'critical_alerts': critical,
            'high_alerts': high
        }
