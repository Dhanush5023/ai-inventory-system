from flask import Blueprint, request, jsonify
from ...models.database import get_db
from ...schemas.auth import UserLogin, UserRegister, Token
from ...schemas.users import UserResponse
from ...services.auth_service import AuthService
from ...core.security import login_required, get_current_user_id

bp = Blueprint("auth", __name__)


@bp.route("/register", methods=["POST"])
def register():
    """Register a new user"""
    db = get_db()
    try:
        user_data = UserRegister(**request.json)
    except Exception as e:
        return jsonify({"detail": str(e)}), 400
        
    user = AuthService.register_user(db, user_data)
    # Convert Pydantic model to dict for jsonify
    return jsonify(UserResponse.model_validate(user).model_dump()), 201


@bp.route("/login", methods=["POST"])
def login():
    """Authenticate user and return JWT token"""
    db = get_db()
    try:
        login_data = UserLogin(**request.json)
    except Exception as e:
        return jsonify({"detail": str(e)}), 400
        
    token_data = AuthService.authenticate_user(db, login_data)
    return jsonify(token_data.model_dump())


@bp.route("/me", methods=["GET"])
@login_required
def get_current_user():
    """Get current authenticated user"""
    db = get_db()
    user_id = get_current_user_id()
    user = AuthService.get_user_by_id(db, user_id)
    return jsonify(UserResponse.model_validate(user).model_dump())


@bp.route("/logout", methods=["POST"])
def logout():
    """Logout user (token invalidation handled client-side)"""
    return jsonify({"message": "Successfully logged out"})
