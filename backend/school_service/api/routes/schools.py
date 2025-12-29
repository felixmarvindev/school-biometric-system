"""API routes for School management."""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from school_service.core.database import get_db
from school_service.core.config import settings
from school_service.services.school_service import SchoolService
from shared.schemas.school import SchoolCreate, SchoolResponse

router = APIRouter(prefix="/api/v1/schools", tags=["schools"])


@router.post(
    "/register",
    response_model=SchoolResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new school",
    description="""
    Register a new school in the system.
    
    The school code must be unique and will be automatically converted to uppercase.
    All fields except name and code are optional.
    """,
    responses={
        201: {
            "description": "School registered successfully",
            "model": SchoolResponse,
        },
        409: {
            "description": "School code already exists",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "School code 'GFA-001' already exists"
                    }
                }
            },
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "name"],
                                "msg": "field required",
                                "type": "value_error.missing"
                            }
                        ]
                    }
                }
            },
        },
    },
)
async def register_school(
    school_data: SchoolCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new school.
    
    - **name**: School name (required, 1-200 characters)
    - **code**: Unique school code (required, 3-50 characters, uppercase letters, numbers, and hyphens only)
    - **address**: School address (optional, max 500 characters)
    - **phone**: Phone number (optional, 10-15 digits)
    - **email**: Email address (optional, must be valid email format)
    """
    try:
        school_service = SchoolService(db)
        school = await school_service.create_school(school_data)
        return SchoolResponse.model_validate(school)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except Exception as e:
        # Log the actual error for debugging (in production, use proper logging)
        import traceback
        error_detail = str(e) if settings.DEBUG else "An error occurred while registering the school"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail,
        )

