from pydantic_settings import BaseSettings
from pydantic import ConfigDict, field_validator
from typing import Optional, List, Union, Any


class Settings(BaseSettings):
    """Application configuration settings"""
    
    # Application
    APP_NAME: str = "AI Inventory Management System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql://inventory_user:inventory_pass@db:5432/inventory_db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production-min-32-characters-long"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "https://ai-inventory-system.vercel.app", # Add placeholder for user
    ]
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> Any:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        return v
    
    # ML Models
    MODEL_PATH: str = "/app/models"
    RETRAIN_INTERVAL_DAYS: int = 7
    PREDICTION_HORIZON_DAYS: int = 30
    RESTOCK_THRESHOLD_DAYS: int = 7
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # External APIs
    GOOGLE_API_KEY: Optional[str] = None
    
    model_config = ConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()
