"""
Sales Service Layer
Business logic for sales management
"""

from sqlalchemy import func, and_, extract
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from typing import List, Optional, Dict
from datetime import datetime, timedelta

from ..models.database import Sale, Product, User
from ..schemas.sales import SaleCreate, SaleUpdate
from ..services.product_service import ProductService


class SalesService:
    """Sales management service"""
    
    @staticmethod
    def create_sale(db: Session, sale_data: SaleCreate, user_id: int) -> Sale:
        """Create a new sale and update stock"""
        # Verify product exists
        product = ProductService.get_product(db, sale_data.product_id)
        
        # Check stock availability
        if product.current_stock < sale_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock. Available: {product.current_stock}, Requested: {sale_data.quantity}"
            )
        
        # Calculate total amount
        total_amount = sale_data.quantity * sale_data.unit_price
        
        # Create sale record
        new_sale = Sale(
            product_id=sale_data.product_id,
            user_id=user_id,
            quantity=sale_data.quantity,
            unit_price=sale_data.unit_price,
            total_amount=total_amount,
            sale_date=sale_data.sale_date or datetime.utcnow(),
            notes=sale_data.notes
        )
        
        # Update product stock
        product.current_stock -= sale_data.quantity
        product.updated_at = datetime.utcnow()
        
        try:
            db.add(new_sale)
            db.commit()
            db.refresh(new_sale)
            return new_sale
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create sale: {str(e)}"
            )
    
    @staticmethod
    def create_bulk_sales(db: Session, sales_data: list[SaleCreate], user_id: int) -> list[Sale]:
        """Create multiple sales in a transaction"""
        created_sales = []
        try:
            for sale_item in sales_data:
                # Verify product and stock
                product = ProductService.get_product(db, sale_item.product_id)
                if product.current_stock < sale_item.quantity:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Insufficient stock for {product.name}. Available: {product.current_stock}"
                    )
                
                # Calculate total
                total_amount = sale_item.quantity * sale_item.unit_price
                
                # Create sale
                new_sale = Sale(
                    product_id=sale_item.product_id,
                    user_id=user_id,
                    quantity=sale_item.quantity,
                    unit_price=sale_item.unit_price,
                    total_amount=total_amount,
                    sale_date=sale_item.sale_date or datetime.utcnow(),
                    notes=sale_item.notes
                )
                
                # Update stock
                product.current_stock -= sale_item.quantity
                product.updated_at = datetime.utcnow()
                
                db.add(new_sale)
                created_sales.append(new_sale)
            
            db.commit()
            for sale in created_sales:
                db.refresh(sale)
            return created_sales
            
        except Exception as e:
            db.rollback()
            print(f"Error in bulk sales: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Bulk sale failed: {str(e)}"
            )
    
    @staticmethod
    def get_sale(db: Session, sale_id: int) -> Sale:
        """Get sale by ID"""
        sale = db.query(Sale).filter(Sale.id == sale_id).first()
        if not sale:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sale not found"
            )
        return sale
    
    @staticmethod
    def get_sales(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        product_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> tuple[List[Sale], int]:
        """
        Get sales with filtering and pagination
        
        Returns:
            (sales, total_count)
        """
        query = db.query(Sale).options(
            joinedload(Sale.product),
            joinedload(Sale.user)
        )
        
        # Apply filters
        if product_id:
            query = query.filter(Sale.product_id == product_id)
        
        if start_date:
            query = query.filter(Sale.sale_date >= start_date)
        
        if end_date:
            query = query.filter(Sale.sale_date <= end_date)
        
        # Order by date descending (newest first)
        query = query.order_by(Sale.sale_date.desc())
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        sales = query.offset(skip).limit(limit).all()
        
        return sales, total
    
    @staticmethod
    def update_sale(db: Session, sale_id: int, sale_data: SaleUpdate) -> Sale:
        """Update sale (with stock adjustment)"""
        sale = SalesService.get_sale(db, sale_id)
        original_quantity = sale.quantity
        
        update_data = sale_data.model_dump(exclude_unset=True)
        
        # Handle quantity change
        if 'quantity' in update_data:
            new_quantity = update_data['quantity']
            quantity_diff = new_quantity - original_quantity
            
            # Check stock if increasing quantity
            if quantity_diff > 0:
                product = ProductService.get_product(db, sale.product_id)
                if product.current_stock < quantity_diff:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Insufficient stock for update. Available: {product.current_stock}"
                    )
                product.current_stock -= quantity_diff
            else:
                # Return stock if decreasing quantity
                product = ProductService.get_product(db, sale.product_id)
                product.current_stock += abs(quantity_diff)
        
        # Recalculate total if quantity or price changed
        if 'quantity' in update_data or 'unit_price' in update_data:
            quantity = update_data.get('quantity', sale.quantity)
            unit_price = update_data.get('unit_price', sale.unit_price)
            sale.total_amount = quantity * unit_price
        
        # Apply updates
        for field, value in update_data.items():
            setattr(sale, field, value)
        
        try:
            db.commit()
            db.refresh(sale)
            return sale
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to update sale: {str(e)}"
            )
    
    @staticmethod
    def delete_sale(db: Session, sale_id: int) -> dict:
        """Delete sale and restore stock"""
        sale = SalesService.get_sale(db, sale_id)
        
        # Restore stock
        product = ProductService.get_product(db, sale.product_id)
        product.current_stock += sale.quantity
        product.updated_at = datetime.utcnow()
        
        try:
            db.delete(sale)
            db.commit()
            return {"message": "Sale deleted and stock restored successfully"}
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to delete sale: {str(e)}"
            )
    
    @staticmethod
    def get_sales_summary(db: Session, days: int = 30) -> Dict:
        """Get sales summary statistics"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Total sales
        total_query = db.query(
            func.sum(Sale.total_amount).label('total_revenue'),
            func.sum(Sale.quantity).label('total_quantity'),
            func.count(Sale.id).label('total_transactions')
        ).filter(Sale.sale_date >= start_date)
        
        result = total_query.first()
        
        return {
            'total_revenue': float(result.total_revenue or 0),
            'total_quantity': int(result.total_quantity or 0),
            'total_transactions': int(result.total_transactions or 0),
            'period_days': days
        }
    
    @staticmethod
    def get_top_products(db: Session, limit: int = 10, days: int = 30) -> List[Dict]:
        """Get top-selling products"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        results = db.query(
            Product.id,
            Product.name,
            Product.sku,
            func.sum(Sale.quantity).label('total_sold'),
            func.sum(Sale.total_amount).label('total_revenue')
        ).join(
            Sale, Sale.product_id == Product.id
        ).filter(
            Sale.sale_date >= start_date
        ).group_by(
            Product.id, Product.name, Product.sku
        ).order_by(
            func.sum(Sale.quantity).desc()
        ).limit(limit).all()
        
        return [
            {
                'product_id': r.id,
                'product_name': r.name,
                'sku': r.sku,
                'total_sold': int(r.total_sold),
                'total_revenue': float(r.total_revenue)
            }
            for r in results
        ]
    
    @staticmethod
    def get_sales_by_date(db: Session, days: int = 30) -> List[Dict]:
        """Get daily sales data for charts"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        results = db.query(
            func.date(Sale.sale_date).label('date'),
            func.sum(Sale.total_amount).label('revenue'),
            func.sum(Sale.quantity).label('quantity'),
            func.count(Sale.id).label('transactions')
        ).filter(
            Sale.sale_date >= start_date
        ).group_by(
            func.date(Sale.sale_date)
        ).order_by(
            func.date(Sale.sale_date).asc()
        ).all()
        
        return [
            {
                'date': r.date.strftime('%Y-%m-%d'),
                'revenue': float(r.revenue),
                'quantity': int(r.quantity),
                'transactions': int(r.transactions)
            }
            for r in results
        ]
    
    @staticmethod
    def get_sales_by_category(db: Session, days: int = 30) -> List[Dict]:
        """Get sales grouped by product category"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        results = db.query(
            Product.category,
            func.sum(Sale.total_amount).label('revenue'),
            func.sum(Sale.quantity).label('quantity')
        ).join(
            Sale, Sale.product_id == Product.id
        ).filter(
            Sale.sale_date >= start_date
        ).group_by(
            Product.category
        ).order_by(
            func.sum(Sale.total_amount).desc()
        ).all()
        
        return [
            {
                'category': r.category or 'Uncategorized',
                'revenue': float(r.revenue),
                'quantity': int(r.quantity)
            }
            for r in results
        ]
