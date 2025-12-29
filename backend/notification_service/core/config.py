"""Configuration management for Notification Service."""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Service
    APP_NAME: str = "School Biometric System - Notification Service"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/school_biometric"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/4"

    # SMS Gateway (Africa's Talking)
    AFRICASTALKING_USERNAME: str = "sandbox"
    AFRICASTALKING_API_KEY: str = ""
    AFRICASTALKING_SENDER_ID: str = "SchoolBio"

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",  # API Gateway
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

