from flask import Blueprint, request, jsonify
from typing import Optional
from ...models.database import get_db, Supplier
from ...schemas.suppliers import (
    SupplierCreate,
    SupplierUpdate,
    SupplierResponse,
    SupplierListResponse,
)
from ...core.security import login_required

bp = Blueprint("suppliers", __name__)


@bp.route("", methods=["GET"])
@login_required
def get_suppliers():
    """Get suppliers with pagination"""
    db = get_db()
    
    try:
        skip = int(request.args.get("skip", 0))
        limit = int(request.args.get("limit", 20))
        is_active_str = request.args.get("is_active")
        is_active = is_active_str.lower() == "true" if is_active_str else None
    except ValueError:
        return jsonify({"detail": "Invalid query parameters"}), 400

    query = db.query(Supplier)

    if is_active is not None:
        query = query.filter(Supplier.is_active == is_active)

    total = query.count()
    suppliers = query.offset(skip).limit(limit).all()

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
            average_delivery_time=None,
        ).model_dump())

    page = (skip // limit) + 1
    response_data = SupplierListResponse(
        suppliers=suppliers_response,
        total=total,
        page=page,
        page_size=limit
    )
    return jsonify(response_data.model_dump())


@bp.route("/<int:supplier_id>", methods=["GET"])
@login_required
def get_supplier(supplier_id: int):
    """Get supplier by ID"""
    db = get_db()
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        return jsonify({"detail": "Supplier not found"}), 404

    return jsonify(SupplierResponse(
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
    ).model_dump())


@bp.route("", methods=["POST"])
@login_required
def create_supplier():
    """Create a new supplier"""
    db = get_db()
    try:
        supplier_data = SupplierCreate(**request.json)
    except Exception as e:
        return jsonify({"detail": str(e)}), 400
        
    supplier = Supplier(**supplier_data.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)

    return jsonify(SupplierResponse(
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
    ).model_dump()), 201


@bp.route("/<int:supplier_id>", methods=["PUT"])
@login_required
def update_supplier(supplier_id: int):
    """Update supplier"""
    db = get_db()
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        return jsonify({"detail": "Supplier not found"}), 404

    try:
        supplier_data = SupplierUpdate(**request.json)
    except Exception as e:
        return jsonify({"detail": str(e)}), 400

    update_data = supplier_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(supplier, field, value)

    db.commit()
    db.refresh(supplier)

    return jsonify(SupplierResponse(
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
    ).model_dump())


@bp.route("/<int:supplier_id>", methods=["DELETE"])
@login_required
def delete_supplier(supplier_id: int):
    """Delete supplier"""
    db = get_db()
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        return jsonify({"detail": "Supplier not found"}), 404

    if len(supplier.orders) > 0 or len(supplier.products) > 0:
        return jsonify({"detail": "Cannot delete supplier with existing orders or products. Deactivate instead."}), 400

    db.delete(supplier)
    db.commit()

    return jsonify({"message": "Supplier deleted successfully"})
