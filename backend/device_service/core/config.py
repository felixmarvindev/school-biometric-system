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
    SIMULATION_MODE: bool = False  # Toggle for demo vs production
    SIMULATION_DELAY_MIN: float = 1.0  # Min delay in seconds
    SIMULATION_DELAY_MAX: float = 3.0  # Max delay in seconds
    DEFAULT_DEVICE_TIMEOUT: int = 5  # Connection timeout in seconds
    DEVICE_HEALTH_CHECK_INTERVAL: int = 5  # Health check interval in seconds (default: 5 minutes)
    
    # ZKTeco Device Connection Settings
    DEVICE_DEFAULT_PORT: int = 4370  # Default ZKTeco device port
    DEVICE_CONNECTION_RETRY_ATTEMPTS: int = 3  # Number of connection retry attempts
    DEVICE_CONNECTION_RETRY_DELAY: float = 1.0  # Delay between retry attempts (seconds)
    DEVICE_CONNECTION_POOL_SIZE: int = 10  # Maximum number of concurrent device connections
    DEVICE_OMIT_PING: bool = False  # Whether to omit ping during connection (some devices need this)


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

