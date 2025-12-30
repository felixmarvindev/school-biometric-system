"""API routes for Device management."""

from fastapi import APIRouter, HTTPException, status, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import math

from device_service.core.database import get_db
from device_service.services.device_service import DeviceService
from device_service.api.dependencies import get_current_user
from shared.schemas.device import (
    DeviceCreate,
    DeviceUpdate,
    DeviceResponse,
    DeviceListResponse,
    DeviceConnectionTest,
    DeviceConnectionTestResponse,
)
from shared.schemas.user import UserResponse
from device_service.models.device import DeviceStatus

router = APIRouter(prefix="/api/v1/devices", tags=["devices"])


@router.post(
    "",
    response_model=DeviceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new device",
    description="""
    Register a new biometric device in the authenticated user's school.
    
    The IP address and port combination must be unique within the school.
    Serial number (if provided) must be globally unique.
    """,
    responses={
        201: {
            "description": "Device registered successfully",
            "model": DeviceResponse,
        },
        409: {
            "description": "IP/port combination or serial number already exists",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Device with IP 192.168.1.100 and port 4370 already exists for this school"
                    }
                }
            },
        },
        422: {
            "description": "Validation error",
        },
    },
)
async def create_device(
    device_data: DeviceCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new device.
    
    - **Authentication**: Required (JWT token)
    - **Authorization**: Device is automatically associated with user's school
    """
    device_service = DeviceService(db)
    
    # Ensure device is created for the authenticated user's school
    if not current_user.school_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with a school to create devices",
        )
    
    try:
        device = await device_service.create_device(
            device_data=device_data,
            school_id=current_user.school_id
        )
        return DeviceResponse.model_validate(device)
    except ValueError as e:
        # Handle validation errors (duplicate IP/port, serial number, etc.)
        error_msg = str(e)
        if "already exists" in error_msg.lower() or "duplicate" in error_msg.lower():
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
    response_model=DeviceListResponse,
    summary="List devices",
    description="""
    Get a paginated list of devices for the authenticated user's school.
    
    Supports search, filtering by status and group, and pagination.
    """,
    responses={
        200: {
            "description": "List of devices retrieved successfully",
            "model": DeviceListResponse,
        },
    },
)
async def list_devices(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by name, IP, or serial number"),
    status: Optional[DeviceStatus] = Query(None, description="Filter by device status"),
    device_group_id: Optional[int] = Query(None, description="Filter by device group"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List devices with pagination and filtering.
    
    - **Authentication**: Required (JWT token)
    - **Authorization**: Only returns devices from user's school
    """
    device_service = DeviceService(db)
    
    result = await device_service.list_devices(
        school_id=current_user.school_id,
        page=page,
        page_size=page_size,
        search=search,
        status=status,
        device_group_id=device_group_id,
    )
    
    devices, total = result
    pages = math.ceil(total / page_size) if total > 0 else 0
    
    return DeviceListResponse(
        items=[DeviceResponse.model_validate(d) for d in devices],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get(
    "/{device_id}",
    response_model=DeviceResponse,
    summary="Get device by ID",
    description="""
    Retrieve a single device by ID.
    
    Only returns devices from the authenticated user's school.
    """,
    responses={
        200: {"description": "Device found"},
        404: {"description": "Device not found"},
        403: {"description": "Device belongs to different school"},
    },
)
async def get_device(
    device_id: int = Path(..., description="Device ID"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a device by ID.
    
    - **Authentication**: Required (JWT token)
    - **Authorization**: Only returns devices from user's school
    """
    device_service = DeviceService(db)
    
    device = await device_service.get_device_by_id(
        device_id=device_id,
        school_id=current_user.school_id
    )
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found",
        )
    
    return DeviceResponse.model_validate(device)


@router.patch(
    "/{device_id}",
    response_model=DeviceResponse,
    summary="Update device",
    description="""
    Update device information (partial update supported).
    
    If IP/port or serial number is changed, uniqueness is validated.
    Only devices from the authenticated user's school can be updated.
    """,
    responses={
        200: {"description": "Device updated successfully"},
        404: {"description": "Device not found"},
        409: {"description": "Duplicate IP/port or serial number"},
    },
)
async def update_device(
    device_id: int = Path(..., description="Device ID"),
    device_data: DeviceUpdate = ...,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a device.
    
    - **Authentication**: Required (JWT token)
    - **Authorization**: Only updates devices from user's school
    """
    device_service = DeviceService(db)
    
    try:
        device = await device_service.update_device(
            device_id=device_id,
            device_data=device_data,
            school_id=current_user.school_id
        )
        
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device with ID {device_id} not found",
            )
        
        return DeviceResponse.model_validate(device)
    except ValueError as e:
        error_msg = str(e)
        if "already exists" in error_msg.lower() or "duplicate" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_msg,
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        )


@router.delete(
    "/{device_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete device",
    description="""
    Soft-delete a device (sets is_deleted = true).
    
    Only devices from the authenticated user's school can be deleted.
    Soft-deleted devices are excluded from list and get operations.
    """,
    responses={
        204: {"description": "Device deleted successfully"},
        404: {"description": "Device not found"},
    },
)
async def delete_device(
    device_id: int = Path(..., description="Device ID"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a device (soft delete).
    
    - **Authentication**: Required (JWT token)
    - **Authorization**: Only deletes devices from user's school
    """
    device_service = DeviceService(db)
    
    success = await device_service.delete_device(
        device_id=device_id,
        school_id=current_user.school_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found",
        )
    
    return None


@router.post(
    "/{device_id}/test",
    response_model=DeviceConnectionTestResponse,
    summary="Test device connection",
    description="""
    Test connectivity to a biometric device.
    
    Attempts to establish a TCP connection to the device's IP and port.
    Updates device status based on test results.
    """,
    responses={
        200: {"description": "Connection test completed"},
        404: {"description": "Device not found"},
    },
)
async def test_device_connection(
    device_id: int = Path(..., description="Device ID"),
    test_config: DeviceConnectionTest = DeviceConnectionTest(),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Test device connection.
    
    - **Authentication**: Required (JWT token)
    - **Authorization**: Only tests devices from user's school
    """
    from device_service.services.device_service import DeviceService
    from device_service.services.device_connection import DeviceConnectionService
    from datetime import datetime
    import asyncio
    
    device_service = DeviceService(db)
    
    # Get device and verify authorization
    device = await device_service.get_device_by_id(
        device_id=device_id,
        school_id=current_user.school_id
    )
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found",
        )
    
    # Test connection
    connection_service = DeviceConnectionService()
    
    try:
        # Attempt TCP connection (basic connectivity test)
        start_time = datetime.utcnow()
        
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(device.ip_address, device.port),
            timeout=test_config.timeout
        )
        writer.close()
        await writer.wait_closed()
        
        # Connection successful
        end_time = datetime.utcnow()
        response_time_ms = int((end_time - start_time).total_seconds() * 1000)
        
        # Update device status
        await device_service.update_device_status(
            device_id=device_id,
            status=DeviceStatus.ONLINE,
            last_seen=datetime.utcnow()
        )
        
        return DeviceConnectionTestResponse(
            success=True,
            message="Connection successful",
            response_time_ms=response_time_ms,
        )
    except (asyncio.TimeoutError, ConnectionRefusedError, OSError) as e:
        # Connection failed
        await device_service.update_device_status(
            device_id=device_id,
            status=DeviceStatus.OFFLINE,
        )
        
        return DeviceConnectionTestResponse(
            success=False,
            message=f"Connection failed: {str(e)}",
        )

