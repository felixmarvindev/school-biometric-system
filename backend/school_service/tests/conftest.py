"""Pytest configuration and fixtures for School Service tests."""

import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.pool import StaticPool

import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from school_service.main import app
from school_service.core.database import get_db
from school_service.core.config import settings
from shared.database.base import Base

# Import all models to ensure they're registered with SQLAlchemy
from school_service.models import School, User, Student, AcademicClass, Stream  # noqa: F401
from device_service.models.device import Device  # noqa: F401
from device_service.models.device_group import DeviceGroup  # noqa: F401

# Enable debug mode for tests to see actual errors
settings.DEBUG = True


# Test database URL (use in-memory SQLite for fast tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="function")
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a test database session with in-memory SQLite.
    
    Creates all tables, yields a session, then drops all tables.
    """
    # Create test engine
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session factory
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    # Create session
    async with async_session() as session:
        yield session
        await session.rollback()

    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Create a test client with database dependency override.
    
    Overrides the database dependency to use the test database.
    """
    # Override database dependency
    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    # Create async client
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
def valid_school_data():
    """Valid school registration data for testing (includes admin user)."""
    return {
        "name": "Greenfield Academy",
        "code": "GFA-001",
        "address": "Nairobi, Kenya",
        "phone": "+254712345678",
        "email": "admin@greenfield.ac.ke",
        "admin": {
            "email": "admin@greenfield.ac.ke",
            "first_name": "John",
            "last_name": "Doe",
            "password": "TestPassword123!",
        },
    }


@pytest.fixture
def minimal_school_data():
    """Minimal valid school registration data (only required fields + admin)."""
    return {
        "name": "Test School",
        "code": "TEST-001",
        "admin": {
            "email": "admin@test.ac.ke",
            "first_name": "Test",
            "last_name": "Admin",
            "password": "TestPassword123!",
        },
    }

