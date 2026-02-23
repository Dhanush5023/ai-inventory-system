from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
import bcrypt
from flask import request, jsonify, g
from functools import wraps
from .config import settings

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None


def login_required(f):
    """Decorator for routes that require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(" ")[1]
        
        if not token:
            return jsonify({"detail": "Token is missing"}), 401
        
        payload = decode_access_token(token)
        if not payload:
            return jsonify({"detail": "Token is invalid or expired"}), 401
        
        g.user_id = payload.get("sub")
        g.user_role = payload.get("role")
        return f(*args, **kwargs)
    
    return decorated


def roles_required(*roles):
    """Decorator for routes that require specific roles"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(g, 'user_role'):
                return jsonify({"detail": "User role not found"}), 401
            
            if g.user_role not in roles:
                return jsonify({"detail": f"Access denied. Required roles: {', '.join(roles)}"}), 403
            
            return f(*args, **kwargs)
        return decorated
    return decorator


def get_current_user_id() -> int:
    """Helper to get current user ID from g"""
    return g.get("user_id")
