from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List

from ...models.database import get_db
from ...schemas.products import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse,
    StockAdjustment,
)
from ...services.product_service import ProductService
from ...core.security import get_current_user_id
from ...core.config import settings

router = APIRouter()


@router.get("", response_model=ProductListResponse)
def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=settings.MAX_PAGE_SIZE),
    query: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None, # Not yet supported in service but keeping for API consistecy
    max_price: Optional[float] = None, 
    in_stock_only: bool = False, # Not yet supported
    low_stock_only: bool = False,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get products with filtering and pagination"""
    products, total = ProductService.get_products(
        db, 
        skip=skip, 
        limit=limit, 
        category=category, 
        search=query, 
        low_stock_only=low_stock_only
    )

    # Enrich products with computed fields
    enriched_products = [
        ProductService.enrich_product_response(product, db) for product in products
    ]

    page = (skip // limit) + 1
    return ProductListResponse(
        products=enriched_products,
        total=total,
        page=page,
        page_size=limit
    )


@router.get("/categories", response_model=List[str])
def get_categories(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get all product categories"""
    return ProductService.get_categories(db)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get product by ID"""
    product = ProductService.get_product(db, product_id)
    return ProductService.enrich_product_response(product, db)


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Create a new product"""
    product = ProductService.create_product(db, product_data)
    return ProductService.enrich_product_response(product, db)


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Update product"""
    product = ProductService.update_product(db, product_id, product_data)
    return ProductService.enrich_product_response(product, db)


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Delete product"""
    return ProductService.delete_product(db, product_id)


@router.post("/stock/adjust", response_model=ProductResponse)
def adjust_stock(
    adjustment: StockAdjustment,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Adjust product stock"""
    product = ProductService.adjust_stock(
        db, 
        adjustment.product_id, 
        adjustment.quantity, 
        adjustment.reason
    )
    return ProductService.enrich_product_response(product, db)
