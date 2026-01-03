"""Database connection and session management."""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from device_service.core.config import settings

# Import all models to ensure SQLAlchemy can resolve relationships
# This is critical for the health check service which creates sessions independently
from school_service.models.school import School
from school_service.models.user import User
from device_service.models.device import Device
from device_service.models.device_group import DeviceGroup

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    """Dependency for getting database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

