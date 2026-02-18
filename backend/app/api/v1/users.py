from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from ...models.database import get_db
from ...schemas.users import UserCreate, UserUpdate, UserResponse, UserListResponse, PasswordChange
from ...schemas.auth import UserRegister
from ...services.auth_service import AuthService
from ...core.security import get_current_user_id, get_password_hash, verify_password
from ...models.database import User
from ...core.config import settings

router = APIRouter()


@router.get("", response_model=UserListResponse)
def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=settings.MAX_PAGE_SIZE),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)"""
    current_user = db.query(User).filter(User.id == user_id).first()
    if not current_user or not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required"
        )

    total = db.query(User).count()
    users = db.query(User).offset(skip).limit(limit).all()

    page = (skip // limit) + 1
    return UserListResponse(
        users=users,
        total=total,
        page=page,
        page_size=limit
    )


@router.get("/{target_user_id}", response_model=UserResponse)
def get_user(
    target_user_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get user by ID"""
    # Allow users to get their own profile or admins to get any profile
    current_user = db.query(User).filter(User.id == user_id).first()
    if user_id != target_user_id and (not current_user or not current_user.is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user"
        )

    user = AuthService.get_user_by_id(db, target_user_id)
    return user


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Create a new user (admin only)"""
    current_user = db.query(User).filter(User.id == user_id).first()
    if not current_user or not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required"
        )

    # Convert to UserRegister schema
    register_data = UserRegister(
        email=user_data.email,
        username=user_data.username,
        password=user_data.password,
        full_name=user_data.full_name
    )

    new_user = AuthService.register_user(db, register_data)

    # Set admin flag if specified
    if user_data.is_admin:
        new_user.is_admin = True
        db.commit()
        db.refresh(new_user)

    return new_user


@router.put("/{target_user_id}", response_model=UserResponse)
def update_user(
    target_user_id: int,
    user_data: UserUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Update user"""
    current_user = db.query(User).filter(User.id == user_id).first()

    # Users can update their own profile, admins can update any
    if user_id != target_user_id and (not current_user or not current_user.is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )

    # Only admins can change is_admin flag
    if user_data.is_admin is not None and (not current_user or not current_user.is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can modify admin status"
        )

    user = AuthService.get_user_by_id(db, target_user_id)

    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


@router.post("/{target_user_id}/change-password")
def change_password(
    target_user_id: int,
    password_data: PasswordChange,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Change user password"""
    if user_id != target_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot change another user's password"
        )

    user = AuthService.get_user_by_id(db, target_user_id)

    # Verify current password
    if not verify_password(password_data.current_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )

    # Set new password
    user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()

    return {"message": "Password changed successfully"}


@router.delete("/{target_user_id}")
def delete_user(
    target_user_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Delete user (admin only)"""
    current_user = db.query(User).filter(User.id == user_id).first()
    if not current_user or not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required"
        )

    if target_user_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    user = AuthService.get_user_by_id(db, target_user_id)
    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}
