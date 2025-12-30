"""API routes for School management."""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from school_service.core.database import get_db
from school_service.core.config import settings
from school_service.services.school_service import SchoolService
from shared.schemas.school import (
    SchoolCreate,
    SchoolResponse,
    SchoolRegistrationWithAdmin,
    SchoolRegistrationResponse,
    AdminUserDetails,
)
from shared.schemas.user import UserCreate

router = APIRouter(prefix="/api/v1/schools", tags=["schools"])


@router.post(
    "/register",
    response_model=SchoolRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new school with admin user",
    description="""
    Register a new school in the system and create the default admin user.
    
    The school code must be unique and will be automatically converted to uppercase.
    A default admin user will be automatically created for the school.
    All school fields except name and code are optional.
    """,
    responses={
        201: {
            "description": "School and admin user registered successfully",
            "model": SchoolRegistrationResponse,
        },
        409: {
            "description": "School code already exists or email already registered",
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
    registration_data: SchoolRegistrationWithAdmin,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new school with its default admin user.
    
    - **name**: School name (required, 1-200 characters)
    - **code**: Unique school code (required, 3-50 characters, uppercase letters, numbers, and hyphens only)
    - **address**: School address (optional, max 500 characters)
    - **phone**: Phone number (optional, 10-15 digits)
    - **email**: School email address (optional, must be valid email format)
    - **admin**: Admin user details (email, first_name, last_name, password)
    """
    try:
        school_service = SchoolService(db)
        
        # Extract school data
        school_data = SchoolCreate(
            name=registration_data.name,
            code=registration_data.code,
            address=registration_data.address,
            phone=registration_data.phone,
            email=registration_data.email,
        )
        
        # Extract admin user data
        admin_data = UserCreate(
            email=registration_data.admin.email,
            first_name=registration_data.admin.first_name,
            last_name=registration_data.admin.last_name,
            password=registration_data.admin.password,
            school_id=0,  # Will be set by create_school_with_admin
            role="school_admin",
        )
        
        # Create school and admin user in a transaction
        # Note: Response validation happens inside create_school_with_admin before commit
        # So if response preparation fails here, the data was already committed
        # This should be rare since we validate before committing
        school, admin_user = await school_service.create_school_with_admin(
            school_data, admin_data
        )
        
        # Prepare response (should succeed since we validated before committing)
        try:
            from shared.schemas.user import UserResponse
            
            # Convert school to dict first (using SchoolResponse which has from_attributes=True)
            school_response = SchoolResponse.model_validate(school)
            admin_user_response = UserResponse.model_validate(admin_user)
            
            # Construct SchoolRegistrationResponse with both school and admin_user
            response = SchoolRegistrationResponse(
                **school_response.model_dump(),
                admin_user=admin_user_response.model_dump()
            )
            
            return response
        except Exception as e:
            # This should be extremely rare since we validate before committing
            # Log the error for investigation
            import logging
            logger = logging.getLogger(__name__)
            logger.error(
                f"Failed to prepare response after successful registration: {str(e)}. "
                f"School ID: {school.id}, Admin User ID: {admin_user.id}"
            )
            # Re-raise as 500 error - data was created but response failed
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Registration succeeded but failed to prepare response. Please contact support.",
            )
    except ValueError as e:
        # Handle validation errors (duplicate code, duplicate email, weak password, etc.)
        error_msg = str(e)
        
        # Check if it's a bcrypt password length error
        if "72 bytes" in error_msg.lower() or "truncate" in error_msg.lower():
            error_msg = "Password cannot be longer than 72 bytes. Please use a shorter password."
        
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=error_msg,
        )
    except Exception as e:
        # Log the actual error for debugging (in production, use proper logging)
        import traceback
        error_msg = str(e)
        
        # Check if it's a bcrypt password length error
        if "72 bytes" in error_msg.lower() or "truncate" in error_msg.lower():
            error_msg = "Password cannot be longer than 72 bytes. Please use a shorter password."
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg,
            )
        
        error_detail = error_msg if settings.DEBUG else "An error occurred while registering the school"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail,
        )

