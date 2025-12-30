"""School Service - Main FastAPI application."""

import sys
from pathlib import Path

from fastapi.responses import RedirectResponse

# Add backend directory to Python path for imports
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from school_service.core.config import settings
from school_service.api.routes import schools, auth, students, classes, streams

app = FastAPI(
    title="School Biometric System - School Service",
    description="School, student, class, and stream management",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(schools.router)
app.include_router(auth.router)
app.include_router(students.router)
app.include_router(classes.router)
app.include_router(streams.router)

# on going to root / redirect to /docs
@app.get("/")
async def root():
    return RedirectResponse(url="/docs")    

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "school_service"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)

