"""
Product Service Layer
Business logic for product management
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime

from ..models.database import Product, Supplier, Order, OrderItem
from ..schemas.products import ProductCreate, ProductUpdate
from ..ai.optimization.engine import optimization_engine
from ..ai.forecasting.prediction_service import PredictionService

# Global prediction service instance
prediction_service = PredictionService()


class ProductService:
    """Product management service"""
    
    @staticmethod
    def create_product(db: Session, product_data: ProductCreate) -> Product:
        """Create a new product"""
        # Verify supplier exists if provided
        if product_data.supplier_id:
            supplier = db.query(Supplier).filter(
                Supplier.id == product_data.supplier_id
            ).first()
            if not supplier:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Supplier not found"
                )
        
        # Check for duplicate SKU
        existing = db.query(Product).filter(Product.sku == product_data.sku).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product with SKU '{product_data.sku}' already exists"
            )
        
        # Create product
        new_product = Product(**product_data.model_dump())
        
        try:
            db.add(new_product)
            db.commit()
            db.refresh(new_product)
            return new_product
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create product. Check for duplicate values."
            )
    
    @staticmethod
    def get_product(db: Session, product_id: int) -> Product:
        """Get product by ID"""
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        return product
    
    @staticmethod
    def get_product_by_sku(db: Session, sku: str) -> Optional[Product]:
        """Get product by SKU"""
        return db.query(Product).filter(Product.sku == sku).first()
    
    @staticmethod
    def get_products(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        search: Optional[str] = None,
        low_stock_only: bool = False
    ) -> tuple[List[Product], int]:
        """
        Get products with filtering and pagination
        
        Returns:
            (products, total_count)
        """
        query = db.query(Product)
        
        # Apply filters
        if category:
            query = query.filter(Product.category == category)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Product.name.ilike(search_term)) |
                (Product.sku.ilike(search_term)) |
                (Product.description.ilike(search_term))
            )
        
        if low_stock_only:
            query = query.filter(Product.current_stock <= Product.minimum_stock)
        
        # Get total count before pagination
        total = query.count()
        
        # Apply pagination
        products = query.offset(skip).limit(limit).all()
        
        return products, total
    
    @staticmethod
    def update_product(db: Session, product_id: int, 
                      product_data: ProductUpdate) -> Product:
        """Update product"""
        product = ProductService.get_product(db, product_id)
        
        # Update fields
        update_data = product_data.model_dump(exclude_unset=True)
        
        # Check SKU uniqueness if being updated
        if 'sku' in update_data and update_data['sku'] != product.sku:
            existing = db.query(Product).filter(
                Product.sku == update_data['sku']
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product with SKU '{update_data['sku']}' already exists"
                )
        
        # Verify supplier if being updated
        if 'supplier_id' in update_data and update_data['supplier_id']:
            supplier = db.query(Supplier).filter(
                Supplier.id == update_data['supplier_id']
            ).first()
            if not supplier:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Supplier not found"
                )
        
        # Apply updates
        for field, value in update_data.items():
            setattr(product, field, value)
        
        product.updated_at = datetime.utcnow()
        
        try:
            db.commit()
            db.refresh(product)
            return product
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update product"
            )
    
    @staticmethod
    def delete_product(db: Session, product_id: int) -> dict:
        """Delete product"""
        product = ProductService.get_product(db, product_id)
        
        try:
            db.delete(product)
            db.commit()
            return {"message": f"Product '{product.name}' deleted successfully"}
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete product. It may have related records."
            )
    
    @staticmethod
    def adjust_stock(db: Session, product_id: int, quantity_change: int,
                    reason: str = "manual_adjustment") -> Product:
        """
        Adjust product stock
        
        Args:
            quantity_change: Positive to add, negative to subtract
        """
        product = ProductService.get_product(db, product_id)
        
        new_stock = product.current_stock + quantity_change
        
        if new_stock < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock. Current: {product.current_stock}, Requested: {abs(quantity_change)}"
            )
        
        product.current_stock = new_stock
        product.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(product)
        
        return product
    
    @staticmethod
    def get_categories(db: Session) -> List[str]:
        """Get list of all product categories"""
        categories = db.query(Product.category).distinct().all()
        return [cat[0] for cat in categories if cat[0]]
    
    @staticmethod
    def get_low_stock_products(db: Session, limit: int = 50) -> List[Product]:
        """Get products with stock below minimum"""
        return db.query(Product).filter(
            Product.current_stock <= Product.minimum_stock
        ).limit(limit).all()
    
    @staticmethod
    def enrich_product_response(product: Product, db: Session) -> dict:
        """Add computed fields to product response"""
        # Calculate status
        if product.current_stock == 0:
            status = "out_of_stock"
        elif product.current_stock <= product.minimum_stock:
            status = "low_stock"
        else:
            status = "in_stock"
            
        # Calculate profit margin
        margin = 0.0
        if product.unit_price > 0:
            margin = ((product.unit_price - product.cost_price) / product.unit_price) * 100
            
        # Get supplier name
        supplier_name = product.supplier.name if product.supplier else None
        
        # Get Pending Orders
        pending_orders = []
        try:
            order_items = db.query(OrderItem).join(Order).filter(
                OrderItem.product_id == product.id,
                Order.status.in_(["pending", "approved", "shipped", "draft"])
            ).all()
            for item in order_items:
                pending_orders.append({
                    "order_id": item.order_id,
                    "order_number": item.order.order_number,
                    "quantity": item.quantity,
                    "status": item.order.status
                })
        except:
            pass
            
        # Get AI Insights
        try:
            ai_insights = optimization_engine.optimize_product(db, product.id)
        except:
            ai_insights = None
            
        # Get Demand Forecast
        try:
            pred_service = PredictionService()
            forecast = pred_service.get_product_forecast(db, product.id, days_ahead=7)
        except:
            forecast = None
            
        return {
            "id": product.id,
            "name": product.name,
            "sku": product.sku,
            "category": product.category,
            "description": product.description,
            "unit_price": product.unit_price,
            "cost_price": product.cost_price,
            "current_stock": product.current_stock,
            "minimum_stock": product.minimum_stock,
            "maximum_stock": product.maximum_stock,
            "unit": product.unit,
            "supplier_id": product.supplier_id,
            "created_at": product.created_at,
            "updated_at": product.updated_at,
            "supplier_name": supplier_name,
            "stock_status": status,
            "profit_margin": round(margin, 2),
            "ai_insights": ai_insights,
            "demand_forecast": forecast,
            "pending_orders": pending_orders
        }
