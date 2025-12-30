"""API routes for Class management."""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from school_service.core.database import get_db
from school_service.services.class_service import ClassService
from shared.schemas.class_schema import (
    ClassCreate,
    ClassUpdate,
    ClassResponse,
)
from shared.schemas.user import UserResponse
from school_service.api.routes.auth import get_current_user

router = APIRouter(prefix="/api/v1/classes", tags=["classes"])


@router.post(
    "",
    response_model=ClassResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new class",
    description="""
    Create a new class in the authenticated user's school.
    
    The class name must be unique within the school.
    """,
    responses={
        201: {
            "description": "Class created successfully",
            "model": ClassResponse,
        },
        409: {
            "description": "Class name already exists",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Class name 'Form 1' already exists for this school"
                    }
                }
            },
        },
        422: {
            "description": "Validation error",
        },
    },
)
async def create_class(
    class_data: ClassCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new class.
    
    - **Authentication**: Required (JWT token)
    - **Authorization**: Class is automatically associated with user's school
    """
    class_service = ClassService(db)
    
    # Ensure class is created for the authenticated user's school
    if not current_user.school_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with a school to create classes",
        )
    
    class_data_with_school = ClassCreate(
        **class_data.model_dump(exclude={"school_id"}),
        school_id=current_user.school_id,
    )
    
    try:
        academic_class = await class_service.create_class(class_data_with_school)
        return ClassResponse.model_validate(academic_class)
    except ValueError as e:
        error_msg = str(e)
        if "name" in error_msg.lower() and ("unique" in error_msg.lower() or "already exists" in error_msg.lower()):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_msg,
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        )


@router.get(
    "",
    response_model=List[ClassResponse],
    summary="List classes",
    description="""
    List all classes in the authenticated user's school.
    """,
    responses={
        200: {
            "description": "List of classes retrieved successfully",
            "model": List[ClassResponse],
        },
    },
)
async def list_classes(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all classes in the authenticated user's school.
    
    - **Authentication**: Required (JWT token)
    - **Authorization**: Only returns classes from user's school
    """
    class_service = ClassService(db)
    
    classes = await class_service.list_classes(school_id=current_user.school_id)
    return [ClassResponse.model_validate(c) for c in classes]


@router.get(
    "/{class_id}",
    response_model=ClassResponse,
    summary="Get class by ID",
    description="""
    Get a specific class by ID.
    
    The class must belong to the authenticated user's school.
    """,
    responses={
        200: {
            "description": "Class retrieved successfully",
            "model": ClassResponse,
        },
        404: {
            "description": "Class not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Class not found"
                    }
                }
            },
        },
    },
)
async def get_class(
    class_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a class by ID.
    
    - **Authentication**: Required (JWT token)
    - **Authorization**: Class must belong to user's school
    """
    class_service = ClassService(db)
    
    academic_class = await class_service.get_class_by_id(
        class_id=class_id,
        school_id=current_user.school_id,
    )
    
    if not academic_class:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found",
        )
    
    return ClassResponse.model_validate(academic_class)


@router.put(
    "/{class_id}",
    response_model=ClassResponse,
    summary="Update class",
    description="""
    Update class information.
    
    School ID cannot be changed.
    """,
    responses={
        200: {
            "description": "Class updated successfully",
            "model": ClassResponse,
        },
        404: {
            "description": "Class not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Class not found"
                    }
                }
            },
        },
        409: {
            "description": "Class name already exists",
        },
    },
)
async def update_class(
    class_id: int,
    class_data: ClassUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a class.
    
    - **Authentication**: Required (JWT token)
    - **Authorization**: Class must belong to user's school
    - **Immutable Fields**: school_id
    """
    class_service = ClassService(db)
    
    # Verify class exists and belongs to user's school
    existing_class = await class_service.get_class_by_id(
        class_id=class_id,
        school_id=current_user.school_id,
    )
    
    if not existing_class:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found",
        )
    
    try:
        updated_class = await class_service.update_class(
            class_id=class_id,
            class_data=class_data,
            school_id=current_user.school_id,
        )
        
        if not updated_class:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Class not found",
            )
        
        return ClassResponse.model_validate(updated_class)
    except ValueError as e:
        error_msg = str(e)
        if "name" in error_msg.lower() and ("unique" in error_msg.lower() or "already exists" in error_msg.lower()):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_msg,
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        )


@router.delete(
    "/{class_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete class (soft delete)",
    description="""
    Soft delete a class (deactivate).
    
    The class data is preserved but marked as deleted.
    This is a soft delete - the class record remains in the database.
    """,
    responses={
        204: {
            "description": "Class deleted successfully",
        },
        404: {
            "description": "Class not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Class not found"
                    }
                }
            },
        },
    },
)
async def delete_class(
    class_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Soft delete a class.
    
    - **Authentication**: Required (JWT token)
    - **Authorization**: Class must belong to user's school
    - **Operation**: Soft delete (sets is_deleted = true)
    """
    class_service = ClassService(db)
    
    # Verify class exists and belongs to user's school
    existing_class = await class_service.get_class_by_id(
        class_id=class_id,
        school_id=current_user.school_id,
    )
    
    if not existing_class:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found",
        )
    
    deleted = await class_service.delete_class(
        class_id=class_id,
        school_id=current_user.school_id,
    )
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found",
        )
    
    return None

