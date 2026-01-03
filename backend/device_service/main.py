"""Device Service - Main FastAPI application."""

import sys
from pathlib import Path
from contextlib import asynccontextmanager
import logging

# Add backend directory to Python path for imports
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from device_service.core.config import settings
from device_service.core.database import AsyncSessionLocal
from device_service.api.routes import devices_router, device_groups_router
from device_service.services.device_health_check import DeviceHealthCheckService

logger = logging.getLogger(__name__)

# Global health check service instance
health_check_service: DeviceHealthCheckService | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    global health_check_service
    
    # Startup
    logger.info("Starting Device Service...")
    
    # Start health check service
    try:
        health_check_service = DeviceHealthCheckService()
        await health_check_service.start()
        logger.info("Device health check service started")
    except Exception as e:
        logger.error(f"Failed to start health check service: {e}", exc_info=True)
    
    yield
    
    # Shutdown
    logger.info("Shutting down Device Service...")
    
    # Stop health check service
    if health_check_service:
        try:
            await health_check_service.stop()
            logger.info("Device health check service stopped")
        except Exception as e:
            logger.error(f"Error stopping health check service: {e}", exc_info=True)


app = FastAPI(
    title="School Biometric System - Device Service",
    description="Device registration, enrollment coordination, and ZKTeco integration",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Include routers
app.include_router(devices_router)
app.include_router(device_groups_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Redirect to API documentation."""
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "device_service",
        "simulation_mode": settings.SIMULATION_MODE,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002, reload=True)

