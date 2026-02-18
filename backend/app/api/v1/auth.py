from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session

from ...models.database import get_db
from ...schemas.auth import UserLogin, UserRegister, Token
from ...schemas.users import UserResponse
from ...services.auth_service import AuthService
from ...core.security import get_current_user_id

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    user = AuthService.register_user(db, user_data)
    return user


@router.post("/login", response_model=Token)
def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """Authenticate user and return JWT token"""
    return AuthService.authenticate_user(db, login_data)


@router.get("/me", response_model=UserResponse)
def get_current_user(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get current authenticated user"""
    user = AuthService.get_user_by_id(db, user_id)
    return user


@router.post("/logout")
def logout():
    """Logout user (token invalidation handled client-side)"""
    return {"message": "Successfully logged out"}
