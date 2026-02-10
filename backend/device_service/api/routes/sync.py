"""API routes for student-device sync."""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from device_service.core.database import get_db
from device_service.services.sync_service import SyncService
from device_service.api.dependencies import get_current_user
from shared.schemas.user import UserResponse
from device_service.exceptions import (
    DeviceOfflineError,
    DeviceNotFoundError,
    StudentNotFoundError,
)

router = APIRouter(prefix="/api/v1/sync", tags=["sync"])


class SyncStatusResponse(BaseModel):
    """Response for sync status check."""

    device_id: int
    student_id: int
    synced: bool


class SyncSuccessResponse(BaseModel):
    """Response for successful sync."""

    message: str
    device_id: int
    student_id: int


@router.post(
    "/students/{student_id}/devices/{device_id}",
    response_model=SyncSuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Sync student to device",
    description="""
    Sync a student to a biometric device by creating/updating the user record on the device.
    
    This must be done before fingerprint enrollment. The student's ID and display name
    are written to the device so it can accept enrollment.
    """,
    responses={
        200: {"description": "Student synced successfully"},
        404: {"description": "Student or device not found"},
        503: {"description": "Device is offline"},
    },
)
async def sync_student_to_device(
    student_id: int,
    device_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Sync a student to a device."""
    sync_service = SyncService(db)
    try:
        await sync_service.sync_student_to_device(
            student_id=student_id,
            device_id=device_id,
            school_id=current_user.school_id,
        )
        return SyncSuccessResponse(
            message="Student synced to device successfully",
            device_id=device_id,
            student_id=student_id,
        )
    except StudentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DeviceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DeviceOfflineError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )


@router.get(
    "/devices/{device_id}/students/{student_id}/status",
    response_model=SyncStatusResponse,
    summary="Check sync status",
    description="Check if a student is synced to a device (exists on device as a user).",
    responses={
        200: {"description": "Sync status returned"},
        404: {"description": "Device not found"},
        503: {"description": "Device is offline"},
    },
)
async def get_sync_status(
    device_id: int,
    student_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Check if student is synced to device."""
    sync_service = SyncService(db)
    try:
        synced = await sync_service.check_student_on_device(
            student_id=student_id,
            device_id=device_id,
            school_id=current_user.school_id,
        )
        return SyncStatusResponse(
            device_id=device_id,
            student_id=student_id,
            synced=synced,
        )
    except DeviceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DeviceOfflineError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )
