"""API routes for Device Group management."""

from fastapi import APIRouter, HTTPException, status, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import math

from device_service.core.database import get_db
from device_service.services.device_group_service import DeviceGroupService
from device_service.api.dependencies import get_current_user
from shared.schemas.device_group import (
    DeviceGroupCreate,
    DeviceGroupUpdate,
    DeviceGroupResponse,
    DeviceGroupListResponse,
)
from shared.schemas.user import UserResponse

router = APIRouter(prefix="/api/v1/device-groups", tags=["device-groups"])


@router.post(
    "",
    response_model=DeviceGroupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create device group",
    description="""
    Create a new device group in the authenticated user's school.
    
    The group name must be unique within the school.
    """,
    responses={
        201: {
            "description": "Device group created successfully",
            "model": DeviceGroupResponse,
        },
        409: {
            "description": "Group name already exists for this school",
        },
        422: {
            "description": "Validation error",
        },
    },
)
async def create_device_group(
    group_data: DeviceGroupCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new device group.
    
    - **Authentication**: Required (JWT token)
    - **Authorization**: Group is automatically associated with user's school
    """
    device_group_service = DeviceGroupService(db)
    
    if not current_user.school_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with a school to create device groups",
        )
    
    try:
        device_group = await device_group_service.create_device_group(
            group_data=group_data,
            school_id=current_user.school_id
        )
        # Get device count
        device_count = await device_group_service.get_device_count(device_group.id)
        
        # Build response with device_count
        response_dict = {
            "id": device_group.id,
            "school_id": device_group.school_id,
            "name": device_group.name,
            "description": device_group.description,
            "device_count": device_count,
            "created_at": device_group.created_at,
            "updated_at": device_group.updated_at,
        }
        return DeviceGroupResponse(**response_dict)
    except ValueError as e:
        error_msg = str(e)
        if "already exists" in error_msg.lower():
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
    response_model=DeviceGroupListResponse,
    summary="List device groups",
    description="""
    Get a paginated list of device groups for the authenticated user's school.
    """,
    responses={
        200: {
            "description": "List of device groups retrieved successfully",
            "model": DeviceGroupListResponse,
        },
    },
)
async def list_device_groups(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List device groups with pagination.
    
    - **Authentication**: Required (JWT token)
    - **Authorization**: Only returns groups from user's school
    """
    device_group_service = DeviceGroupService(db)
    
    groups, total = await device_group_service.list_device_groups(
        school_id=current_user.school_id,
        page=page,
        page_size=page_size,
    )
    
    # Build responses with device counts
    items = []
    for group in groups:
        device_count = await device_group_service.get_device_count(group.id)
        response_dict = {
            "id": group.id,
            "school_id": group.school_id,
            "name": group.name,
            "description": group.description,
            "device_count": device_count,
            "created_at": group.created_at,
            "updated_at": group.updated_at,
        }
        items.append(DeviceGroupResponse(**response_dict))
    
    pages = math.ceil(total / page_size) if total > 0 else 0
    
    return DeviceGroupListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get(
    "/{group_id}",
    response_model=DeviceGroupResponse,
    summary="Get device group by ID",
    description="""
    Retrieve a single device group by ID.
    
    Only returns groups from the authenticated user's school.
    """,
    responses={
        200: {"description": "Device group found"},
        404: {"description": "Device group not found"},
    },
)
async def get_device_group(
    group_id: int = Path(..., description="Device group ID"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a device group by ID.
    
    - **Authentication**: Required (JWT token)
    - **Authorization**: Only returns groups from user's school
    """
    device_group_service = DeviceGroupService(db)
    
    device_group = await device_group_service.get_device_group_by_id(
        group_id=group_id,
        school_id=current_user.school_id
    )
    
    if not device_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device group with ID {group_id} not found",
        )
    
    # Get device count
    device_count = await device_group_service.get_device_count(device_group.id)
    
    # Build response with device_count
    response_dict = {
        "id": device_group.id,
        "school_id": device_group.school_id,
        "name": device_group.name,
        "description": device_group.description,
        "device_count": device_count,
        "created_at": device_group.created_at,
        "updated_at": device_group.updated_at,
    }
    return DeviceGroupResponse(**response_dict)


@router.patch(
    "/{group_id}",
    response_model=DeviceGroupResponse,
    summary="Update device group",
    description="""
    Update device group information (partial update supported).
    
    If the name is changed, uniqueness is validated.
    Only groups from the authenticated user's school can be updated.
    """,
    responses={
        200: {"description": "Device group updated successfully"},
        404: {"description": "Device group not found"},
        409: {"description": "Group name already exists for this school"},
    },
)
async def update_device_group(
    group_id: int = Path(..., description="Device group ID"),
    group_data: DeviceGroupUpdate = ...,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a device group.
    
    - **Authentication**: Required (JWT token)
    - **Authorization**: Only updates groups from user's school
    """
    device_group_service = DeviceGroupService(db)
    
    try:
        device_group = await device_group_service.update_device_group(
            group_id=group_id,
            group_data=group_data,
            school_id=current_user.school_id
        )
        
        if not device_group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device group with ID {group_id} not found",
            )
        
        # Get device count
        device_count = await device_group_service.get_device_count(device_group.id)
        
        # Build response with device_count
        response_dict = {
            "id": device_group.id,
            "school_id": device_group.school_id,
            "name": device_group.name,
            "description": device_group.description,
            "device_count": device_count,
            "created_at": device_group.created_at,
            "updated_at": device_group.updated_at,
        }
        return DeviceGroupResponse(**response_dict)
    except ValueError as e:
        error_msg = str(e)
        if "already exists" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_msg,
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        )


@router.delete(
    "/{group_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete device group",
    description="""
    Soft-delete a device group (sets is_deleted = true).
    
    Only groups from the authenticated user's school can be deleted.
    Soft-deleted groups are excluded from list and get operations.
    """,
    responses={
        204: {"description": "Device group deleted successfully"},
        404: {"description": "Device group not found"},
    },
)
async def delete_device_group(
    group_id: int = Path(..., description="Device group ID"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a device group (soft delete).
    
    - **Authentication**: Required (JWT token)
    - **Authorization**: Only deletes groups from user's school
    """
    device_group_service = DeviceGroupService(db)
    
    success = await device_group_service.delete_device_group(
        group_id=group_id,
        school_id=current_user.school_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device group with ID {group_id} not found",
        )
    
    return None  # 204 No Content

