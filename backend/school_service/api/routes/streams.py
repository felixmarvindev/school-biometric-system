"""API routes for Stream management."""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from school_service.core.database import get_db
from school_service.services.stream_service import StreamService
from school_service.services.class_service import ClassService
from shared.schemas.stream_schema import (
    StreamCreate,
    StreamUpdate,
    StreamResponse,
)
from shared.schemas.user import UserResponse
from school_service.api.routes.auth import get_current_user

router = APIRouter(prefix="/api/v1/streams", tags=["streams"])


@router.post(
    "",
    response_model=StreamResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new stream",
    description="""
    Create a new stream within a class.
    
    The stream name must be unique within the class.
    The class must belong to the authenticated user's school.
    """,
    responses={
        201: {
            "description": "Stream created successfully",
            "model": StreamResponse,
        },
        404: {
            "description": "Class not found",
        },
        409: {
            "description": "Stream name already exists",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Stream name 'A' already exists for this class"
                    }
                }
            },
        },
        422: {
            "description": "Validation error",
        },
    },
)
async def create_stream(
    stream_data: StreamCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new stream within a class.
    
    - **Authentication**: Required (JWT token)
    - **Authorization**: Class must belong to user's school
    """
    stream_service = StreamService(db)
    class_service = ClassService(db)
    
    # Verify class exists and belongs to user's school
    class_obj = await class_service.get_class_by_id(
        class_id=stream_data.class_id,
        school_id=current_user.school_id,
    )
    
    if not class_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found",
        )
    
    try:
        stream = await stream_service.create_stream(stream_data)
        return StreamResponse.model_validate(stream)
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
    response_model=List[StreamResponse],
    summary="List streams",
    description="""
    List streams, optionally filtered by class.
    
    Only returns streams from classes in the authenticated user's school.
    """,
    responses={
        200: {
            "description": "List of streams retrieved successfully",
            "model": List[StreamResponse],
        },
        404: {
            "description": "Class not found (if class_id provided)",
        },
    },
)
async def list_streams(
    class_id: Optional[int] = Query(None, description="Filter by class ID"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List streams, optionally filtered by class.
    
    - **Authentication**: Required (JWT token)
    - **Authorization**: Only returns streams from user's school classes
    """
    stream_service = StreamService(db)
    class_service = ClassService(db)
    
    # If class_id provided, verify it belongs to user's school
    if class_id:
        class_obj = await class_service.get_class_by_id(
            class_id=class_id,
            school_id=current_user.school_id,
        )
        if not class_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Class not found",
            )
    
    streams = await stream_service.list_streams(
        school_id=current_user.school_id,
        class_id=class_id,
    )
    return [StreamResponse.model_validate(s) for s in streams]


@router.get(
    "/{stream_id}",
    response_model=StreamResponse,
    summary="Get stream by ID",
    description="""
    Get a specific stream by ID.
    
    The stream must belong to a class in the authenticated user's school.
    """,
    responses={
        200: {
            "description": "Stream retrieved successfully",
            "model": StreamResponse,
        },
        404: {
            "description": "Stream not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Stream not found"
                    }
                }
            },
        },
    },
)
async def get_stream(
    stream_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a stream by ID.
    
    - **Authentication**: Required (JWT token)
    - **Authorization**: Stream must belong to user's school (via class)
    """
    stream_service = StreamService(db)
    
    stream = await stream_service.get_stream_by_id(
        stream_id=stream_id,
        school_id=current_user.school_id,
    )
    
    if not stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stream not found",
        )
    
    return StreamResponse.model_validate(stream)


@router.put(
    "/{stream_id}",
    response_model=StreamResponse,
    summary="Update stream",
    description="""
    Update stream information.
    
    Class ID cannot be changed.
    """,
    responses={
        200: {
            "description": "Stream updated successfully",
            "model": StreamResponse,
        },
        404: {
            "description": "Stream not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Stream not found"
                    }
                }
            },
        },
        409: {
            "description": "Stream name already exists",
        },
    },
)
async def update_stream(
    stream_id: int,
    stream_data: StreamUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a stream.
    
    - **Authentication**: Required (JWT token)
    - **Authorization**: Stream must belong to user's school (via class)
    - **Immutable Fields**: class_id
    """
    stream_service = StreamService(db)
    
    # Verify stream exists and belongs to user's school
    existing_stream = await stream_service.get_stream_by_id(
        stream_id=stream_id,
        school_id=current_user.school_id,
    )
    
    if not existing_stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stream not found",
        )
    
    try:
        updated_stream = await stream_service.update_stream(
            stream_id=stream_id,
            stream_data=stream_data,
            school_id=current_user.school_id,
        )
        
        if not updated_stream:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Stream not found",
            )
        
        return StreamResponse.model_validate(updated_stream)
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
    "/{stream_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete stream (soft delete)",
    description="""
    Soft delete a stream (deactivate).
    
    The stream data is preserved but marked as deleted.
    This is a soft delete - the stream record remains in the database.
    """,
    responses={
        204: {
            "description": "Stream deleted successfully",
        },
        404: {
            "description": "Stream not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Stream not found"
                    }
                }
            },
        },
    },
)
async def delete_stream(
    stream_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Soft delete a stream.
    
    - **Authentication**: Required (JWT token)
    - **Authorization**: Stream must belong to user's school (via class)
    - **Operation**: Soft delete (sets is_deleted = true)
    """
    stream_service = StreamService(db)
    
    # Verify stream exists and belongs to user's school
    existing_stream = await stream_service.get_stream_by_id(
        stream_id=stream_id,
        school_id=current_user.school_id,
    )
    
    if not existing_stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stream not found",
        )
    
    deleted = await stream_service.delete_stream(
        stream_id=stream_id,
        school_id=current_user.school_id,
    )
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stream not found",
        )
    
    return None

