from flask import Blueprint, request, jsonify, g
from typing import Optional
from ...models.database import get_db, User
from ...schemas.users import UserCreate, UserUpdate, UserResponse, UserListResponse, PasswordChange
from ...schemas.auth import UserRegister
from ...services.auth_service import AuthService
from ...core.security import login_required, get_current_user_id, get_password_hash, verify_password
from ...core.config import settings

bp = Blueprint("users", __name__)


@bp.route("", methods=["GET"])
@login_required
def get_users():
    """Get all users (admin only)"""
    db = get_db()
    user_id = get_current_user_id()
    current_user = db.query(User).filter(User.id == user_id).first()
    if not current_user or not current_user.is_admin:
        return jsonify({"detail": "Administrator access required"}), 403

    try:
        skip = int(request.args.get("skip", 0))
        limit = int(request.args.get("limit", 20))
    except ValueError:
        return jsonify({"detail": "Invalid pagination parameters"}), 400

    total = db.query(User).count()
    users = db.query(User).offset(skip).limit(limit).all()

    page = (skip // limit) + 1
    response_data = UserListResponse(
        users=[UserResponse.model_validate(u).model_dump() for u in users],
        total=total,
        page=page,
        page_size=limit
    )
    return jsonify(response_data.model_dump())


@bp.route("/<int:target_user_id>", methods=["GET"])
@login_required
def get_user(target_user_id: int):
    """Get user by ID"""
    db = get_db()
    user_id = get_current_user_id()
    
    current_user = db.query(User).filter(User.id == user_id).first()
    if user_id != target_user_id and (not current_user or not current_user.is_admin):
        return jsonify({"detail": "Not authorized to view this user"}), 403

    user = AuthService.get_user_by_id(db, target_user_id)
    if not user:
        return jsonify({"detail": "User not found"}), 404
        
    return jsonify(UserResponse.model_validate(user).model_dump())


@bp.route("", methods=["POST"])
@login_required
def create_user():
    """Create a new user (admin only)"""
    db = get_db()
    user_id = get_current_user_id()
    
    current_user = db.query(User).filter(User.id == user_id).first()
    if not current_user or not current_user.is_admin:
        return jsonify({"detail": "Administrator access required"}), 403

    try:
        user_data = UserCreate(**request.json)
    except Exception as e:
        return jsonify({"detail": str(e)}), 400

    register_data = UserRegister(
        email=user_data.email,
        username=user_data.username,
        password=user_data.password,
        full_name=user_data.full_name
    )

    new_user = AuthService.register_user(db, register_data)

    if user_data.is_admin:
        new_user.is_admin = True
        db.commit()
        db.refresh(new_user)

    return jsonify(UserResponse.model_validate(new_user).model_dump()), 201


@bp.route("/<int:target_user_id>", methods=["PUT"])
@login_required
def update_user(target_user_id: int):
    """Update user"""
    db = get_db()
    user_id = get_current_user_id()
    current_user = db.query(User).filter(User.id == user_id).first()

    if user_id != target_user_id and (not current_user or not current_user.is_admin):
        return jsonify({"detail": "Not authorized to update this user"}), 403

    try:
        user_data = UserUpdate(**request.json)
    except Exception as e:
        return jsonify({"detail": str(e)}), 400

    if user_data.is_admin is not None and (not current_user or not current_user.is_admin):
        return jsonify({"detail": "Only administrators can modify admin status"}), 403

    user = AuthService.get_user_by_id(db, target_user_id)
    if not user:
        return jsonify({"detail": "User not found"}), 404

    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return jsonify(UserResponse.model_validate(user).model_dump())


@bp.route("/<int:target_user_id>/change-password", methods=["POST"])
@login_required
def change_password(target_user_id: int):
    """Change user password"""
    db = get_db()
    user_id = get_current_user_id()
    
    if user_id != target_user_id:
        return jsonify({"detail": "Cannot change another user's password"}), 403

    try:
        password_data = PasswordChange(**request.json)
    except Exception as e:
        return jsonify({"detail": str(e)}), 400

    user = AuthService.get_user_by_id(db, target_user_id)
    if not user:
        return jsonify({"detail": "User not found"}), 404

    if not verify_password(password_data.current_password, user.hashed_password):
        return jsonify({"detail": "Incorrect current password"}), 400

    user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()

    return jsonify({"message": "Password changed successfully"})


@bp.route("/<int:target_user_id>", methods=["DELETE"])
@login_required
def delete_user(target_user_id: int):
    """Delete user (admin only)"""
    db = get_db()
    user_id = get_current_user_id()
    current_user = db.query(User).filter(User.id == user_id).first()
    
    if not current_user or not current_user.is_admin:
        return jsonify({"detail": "Administrator access required"}), 403

    if target_user_id == user_id:
        return jsonify({"detail": "Cannot delete your own account"}), 400

    user = AuthService.get_user_by_id(db, target_user_id)
    if not user:
        return jsonify({"detail": "User not found"}), 404
        
    db.delete(user)
    db.commit()

    return jsonify({"message": "User deleted successfully"})
