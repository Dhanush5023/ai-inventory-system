from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from ...models.database import get_db, Supplier
from ...schemas.suppliers import (
    SupplierCreate,
    SupplierUpdate,
    SupplierResponse,
    SupplierListResponse,
)
from ...core.security import get_current_user_id
from ...core.config import settings
from fastapi import HTTPException

router = APIRouter()


@router.get("", response_model=SupplierListResponse)
def get_suppliers(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=settings.MAX_PAGE_SIZE),
    is_active: Optional[bool] = None,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get suppliers with pagination"""
    query = db.query(Supplier)

    if is_active is not None:
        query = query.filter(Supplier.is_active == is_active)

    total = query.count()
    suppliers = query.offset(skip).limit(limit).all()

    # Enrich with counts
    suppliers_response = []
    for supplier in suppliers:
        suppliers_response.append(SupplierResponse(
            id=supplier.id,
            name=supplier.name,
            contact_person=supplier.contact_person,
            email=supplier.email,
            phone=supplier.phone,
            address=supplier.address,
            city=supplier.city,
            country=supplier.country,
            rating=supplier.rating,
            is_active=supplier.is_active,
            created_at=supplier.created_at,
            product_count=len(supplier.products),
            total_orders=len(supplier.orders),
            average_delivery_time=None,  # TODO: Calculate from orders
        ))

    page = (skip // limit) + 1
    return SupplierListResponse(
        suppliers=suppliers_response,
        total=total,
        page=page,
        page_size=limit
    )


@router.get("/{supplier_id}", response_model=SupplierResponse)
def get_supplier(
    supplier_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get supplier by ID"""
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )

    return SupplierResponse(
        id=supplier.id,
        name=supplier.name,
        contact_person=supplier.contact_person,
        email=supplier.email,
        phone=supplier.phone,
        address=supplier.address,
        city=supplier.city,
        country=supplier.country,
        rating=supplier.rating,
        is_active=supplier.is_active,
        created_at=supplier.created_at,
        product_count=len(supplier.products),
        total_orders=len(supplier.orders),
        average_delivery_time=None,
    )


@router.post("", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
def create_supplier(
    supplier_data: SupplierCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Create a new supplier"""
    supplier = Supplier(**supplier_data.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)

    return SupplierResponse(
        id=supplier.id,
        name=supplier.name,
        contact_person=supplier.contact_person,
        email=supplier.email,
        phone=supplier.phone,
        address=supplier.address,
        city=supplier.city,
        country=supplier.country,
        rating=supplier.rating,
        is_active=supplier.is_active,
        created_at=supplier.created_at,
        product_count=0,
        total_orders=0,
        average_delivery_time=None,
    )


@router.put("/{supplier_id}", response_model=SupplierResponse)
def update_supplier(
    supplier_id: int,
    supplier_data: SupplierUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Update supplier"""
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )

    update_data = supplier_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(supplier, field, value)

    db.commit()
    db.refresh(supplier)

    return SupplierResponse(
        id=supplier.id,
        name=supplier.name,
        contact_person=supplier.contact_person,
        email=supplier.email,
        phone=supplier.phone,
        address=supplier.address,
        city=supplier.city,
        country=supplier.country,
        rating=supplier.rating,
        is_active=supplier.is_active,
        created_at=supplier.created_at,
        product_count=len(supplier.products),
        total_orders=len(supplier.orders),
        average_delivery_time=None,
    )


@router.delete("/{supplier_id}")
def delete_supplier(
    supplier_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Delete supplier"""
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )

    # Check if supplier has orders or products
    if len(supplier.orders) > 0 or len(supplier.products) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete supplier with existing orders or products. Deactivate instead."
        )

    db.delete(supplier)
    db.commit()

    return {"message": "Supplier deleted successfully"}
