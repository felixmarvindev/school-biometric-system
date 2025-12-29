"""Configuration management for Attendance Service."""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Service
    APP_NAME: str = "School Biometric System - Attendance Service"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/school_biometric"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/3"

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",  # API Gateway
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

