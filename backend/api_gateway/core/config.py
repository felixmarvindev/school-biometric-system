"""Configuration management for API Gateway."""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Gateway
    APP_NAME: str = "School Biometric System - API Gateway"
    DEBUG: bool = False

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
    ]

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Service URLs (for routing)
    SCHOOL_SERVICE_URL: str = "http://localhost:8001"
    DEVICE_SERVICE_URL: str = "http://localhost:8002"
    ATTENDANCE_SERVICE_URL: str = "http://localhost:8003"
    NOTIFICATION_SERVICE_URL: str = "http://localhost:8004"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

