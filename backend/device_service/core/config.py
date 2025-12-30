"""Configuration management for Device Service."""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Service
    APP_NAME: str = "School Biometric System - Device Service"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/school_biometric"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/2"

    # Device Settings
    SIMULATION_MODE: bool = True  # Toggle for demo vs production
    SIMULATION_DELAY_MIN: float = 1.0  # Min delay in seconds
    SIMULATION_DELAY_MAX: float = 3.0  # Max delay in seconds
    DEFAULT_DEVICE_TIMEOUT: int = 5  # Connection timeout in seconds
    
    # Security (shared with school_service)
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",  # API Gateway
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

