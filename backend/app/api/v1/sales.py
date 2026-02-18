from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from datetime import datetime

from ...models.database import get_db, Sale
from ...schemas.sales import (
    SaleCreate,
    SaleUpdate,
    SaleResponse,
    SaleListResponse,
    SalesSummary,
    BulkSaleCreate
)
from ...services.sales_service import SalesService
from ...core.security import get_current_user_id
from ...core.config import settings

router = APIRouter()


@router.get("", response_model=SaleListResponse)
def get_sales(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=settings.MAX_PAGE_SIZE),
    product_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get sales history with filtering"""
    print(f"FETCHING SALES: skip={skip}, limit={limit}, product_id={product_id}")
    sales, total = SalesService.get_sales(
        db,
        skip=skip,
        limit=limit,
        product_id=product_id,
        start_date=start_date,
        end_date=end_date
    )
    print(f"FOUND {len(sales)} SALES, TOTAL: {total}")


    # Calculate total revenue for the filtered results (not just the paged ones)
    total_rev_query = db.query(func.sum(Sale.total_amount))
    if product_id:
        total_rev_query = total_rev_query.filter(Sale.product_id == product_id)
    if start_date:
        total_rev_query = total_rev_query.filter(Sale.sale_date >= start_date)
    if end_date:
        total_rev_query = total_rev_query.filter(Sale.sale_date <= end_date)
    
    total_revenue = total_rev_query.scalar() or 0.0

    # Enrich sales with product_name and username
    enriched_sales = []
    for sale in sales:
        enriched_sales.append(SaleResponse(
            id=sale.id,
            product_id=sale.product_id,
            user_id=sale.user_id,
            quantity=sale.quantity,
            unit_price=sale.unit_price,
            total_amount=sale.total_amount,
            sale_date=sale.sale_date,
            notes=sale.notes,
            product_name=sale.product.name if sale.product else "Unknown",
            username=sale.user.username if sale.user else "System"
        ))
    
    page = (skip // limit) + 1
    return SaleListResponse(
        sales=enriched_sales,
        total=total,
        page=page,
        page_size=limit,
        total_revenue=total_revenue
    )


@router.get("/{sale_id}", response_model=SaleResponse)
def get_sale(
    sale_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get sale details"""
    return SalesService.get_sale(db, sale_id)


@router.post("", response_model=SaleResponse, status_code=status.HTTP_201_CREATED)
def create_sale(
    sale_data: SaleCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Record a new sale"""
    return SalesService.create_sale(db, sale_data, user_id)


@router.post("/bulk", response_model=List[SaleResponse], status_code=status.HTTP_201_CREATED)
def create_bulk_sales(
    bulk_data: BulkSaleCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Record multiple sales (POS transaction)"""
    print(f"CREATING BULK SALES: {len(bulk_data.items)} items for user {user_id}")
    sales = SalesService.create_bulk_sales(db, bulk_data.items, user_id)
    
    # Enrich before returning to match response_model
    enriched = []
    for s in sales:
        enriched.append(SaleResponse(
            id=s.id,
            product_id=s.product_id,
            user_id=s.user_id,
            quantity=s.quantity,
            unit_price=s.unit_price,
            total_amount=s.total_amount,
            sale_date=s.sale_date,
            notes=s.notes,
            product_name=s.product.name if s.product else "Unknown",
            username=s.user.username if s.user else "System"
        ))
    print(f"BULK SALES CREATED: {len(enriched)} items")
    return enriched



@router.put("/{sale_id}", response_model=SaleResponse)
def update_sale(
    sale_id: int,
    sale_data: SaleUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Update sale record"""
    return SalesService.update_sale(db, sale_id, sale_data)


@router.delete("/{sale_id}")
def delete_sale(
    sale_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Delete sale record (restores stock)"""
    return SalesService.delete_sale(db, sale_id)


@router.get("/stats/summary", response_model=SalesSummary)
def get_sales_summary(
    days: int = Query(30, ge=1, le=365),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get sales summary statistics"""
    return SalesService.get_sales_summary(db, days)


@router.get("/stats/top-products")
def get_top_products(
    limit: int = Query(10, ge=1, le=50),
    days: int = Query(30, ge=1, le=365),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get top selling products"""
    return SalesService.get_top_products(db, limit, days)


@router.get("/stats/daily")
def get_daily_sales(
    days: int = Query(30, ge=1, le=365),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get daily sales trend"""
    return SalesService.get_sales_by_date(db, days)


@router.get("/stats/by-category")
def get_category_sales(
    days: int = Query(30, ge=1, le=365),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get sales distribution by category"""
    return SalesService.get_sales_by_category(db, days)
