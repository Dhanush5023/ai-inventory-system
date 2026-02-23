from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
import os

from .core.config import settings
from .models.database import init_db, close_db
from .api.v1 import api_v1_bp


def create_app():
    """Application factory"""
    app = Flask(__name__)
    
    # Configuration
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    
    # CORS
    CORS(app, resources={r"/api/*": {"origins": settings.CORS_ORIGINS or "*"}})
    
    # Initialize database and teardown
    with app.app_context():
        print("[INFO] Starting AI Inventory Management System...")
        print(f"[INFO] App: {settings.APP_NAME} v{settings.APP_VERSION}")
        print("[INFO] Initializing database...")
        init_db()
        print("[OK] Database initialized")

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        close_db(exception)

    @app.errorhandler(HTTPException)
    def handle_exception(e):
        """Return JSON instead of HTML for HTTP errors."""
        response = e.get_response()
        response.data = jsonify({
            "code": e.code,
            "name": e.name,
            "detail": e.description,
        }).data
        response.content_type = "application/json"
        return response

    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        """Return JSON for unexpected errors."""
        return jsonify({
            "code": 500,
            "name": "Internal Server Error",
            "detail": str(e) if settings.DEBUG else "An unexpected error occurred"
        }), 500

    # Register Blueprints
    app.register_blueprint(api_v1_bp, url_prefix="/api/v1")

    @app.route("/")
    def root():
        """Root endpoint"""
        return jsonify({
            "message": "AI Inventory Management System API",
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "health": "/health",
        })

    @app.route("/health")
    def health_check():
        """Health check endpoint"""
        return jsonify({
            "status": "healthy",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
        })

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8000,
        debug=False,
    )
