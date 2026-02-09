"""API routes for Enrollment management."""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from device_service.core.database import get_db
from device_service.services.enrollment_service import EnrollmentService
from device_service.api.dependencies import get_current_user
from shared.schemas.enrollment import (
    EnrollmentStartRequest,
    EnrollmentStartResponse,
    EnrollmentSessionResponse,
    EnrolledFingersResponse,
    EnrollmentRecordSummary,
    EnrollmentListResponse,
)
from shared.schemas.user import UserResponse
from device_service.exceptions import (
    DeviceOfflineError,
    DeviceNotFoundError,
    EnrollmentError,
    EnrollmentInProgressError,
)

router = APIRouter(prefix="/api/v1/enrollment", tags=["enrollment"])


@router.post(
    "/start",
    response_model=EnrollmentStartResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start enrollment",
    description="""
    Start fingerprint enrollment for a student on a device.
    
    This endpoint:
    1. Validates student and device exist
    2. Checks device is online
    3. Creates enrollment session
    4. Sends enrollment command to device
    5. Returns session information
    
    The device will enter enrollment mode and wait for the student to place their finger.
    Real-time progress updates are sent via WebSocket (to be implemented in Phase 3).
    """,
    responses={
        201: {"description": "Enrollment started successfully"},
        400: {"description": "Invalid request"},
        404: {"description": "Student or device not found"},
        503: {"description": "Device is offline"},
    },
)
async def start_enrollment(
    request: EnrollmentStartRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Start enrollment for a student.
    
    Args:
        request: Enrollment start request with student_id, device_id, and finger_id
        current_user: Authenticated user (automatically injected)
        db: Database session (automatically injected)
        
    Returns:
        EnrollmentStartResponse with session information
    """
    enrollment_service = EnrollmentService(db)
    
    try:
        enrollment_session = await enrollment_service.start_enrollment(
            student_id=request.student_id,
            device_id=request.device_id,
            finger_id=request.finger_id,
            school_id=current_user.school_id,
        )
        
        return EnrollmentStartResponse(
            session_id=enrollment_session.session_id,
            student_id=enrollment_session.student_id,
            device_id=enrollment_session.device_id,
            finger_id=enrollment_session.finger_id,
            status=enrollment_session.status,
            started_at=enrollment_session.started_at,
        )
        
    except DeviceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DeviceOfflineError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except EnrollmentInProgressError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except EnrollmentError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Log unexpected errors
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Unexpected error starting enrollment: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while starting enrollment"
        )


def _enrollment_to_summary(session) -> EnrollmentRecordSummary:
    """Build EnrollmentRecordSummary from EnrollmentSession."""
    return EnrollmentRecordSummary(
        id=session.id,
        session_id=session.session_id,
        student_id=session.student_id,
        device_id=session.device_id,
        finger_id=session.finger_id,
        quality_score=session.quality_score,
        completed_at=session.completed_at,
        has_template=bool(session.template_data),
        student_name=(
            f"{session.student.first_name} {session.student.last_name}"
            if session.student
            else None
        ),
        device_name=session.device.name if session.device else None,
    )


@router.get(
    "/students/{student_id}/enrollments",
    response_model=EnrollmentListResponse,
    summary="List enrollments by student",
    description="Get completed enrollment records for a student (for UI and sync readiness).",
)
async def list_enrollments_by_student(
    student_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List completed enrollments for a student."""
    enrollment_service = EnrollmentService(db)
    sessions = await enrollment_service.get_enrollments_by_student(
        school_id=current_user.school_id,
        student_id=student_id,
    )
    return EnrollmentListResponse(
        enrollments=[_enrollment_to_summary(s) for s in sessions]
    )


@router.get(
    "/devices/{device_id}/enrollments",
    response_model=EnrollmentListResponse,
    summary="List enrollments by device",
    description="Get completed enrollment records for a device (for UI and sync readiness).",
)
async def list_enrollments_by_device(
    device_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List completed enrollments for a device."""
    enrollment_service = EnrollmentService(db)
    sessions = await enrollment_service.get_enrollments_by_device(
        school_id=current_user.school_id,
        device_id=device_id,
    )
    return EnrollmentListResponse(
        enrollments=[_enrollment_to_summary(s) for s in sessions]
    )


@router.get(
    "/devices/{device_id}/students/{student_id}/fingers",
    response_model=EnrolledFingersResponse,
    summary="Get enrolled fingers",
    description="Get list of finger IDs (0-9) already enrolled for this student on the device.",
)
async def get_enrolled_fingers(
    device_id: int,
    student_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return enrolled finger IDs for student on device."""
    enrollment_service = EnrollmentService(db)
    try:
        finger_ids = await enrollment_service.get_enrolled_fingers(
            device_id=device_id,
            student_id=student_id,
            school_id=current_user.school_id,
        )
        return EnrolledFingersResponse(
            device_id=device_id,
            student_id=student_id,
            finger_ids=finger_ids,
        )
    except DeviceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DeviceOfflineError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))


@router.delete(
    "/devices/{device_id}/students/{student_id}/fingers/{finger_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete fingerprint",
    description="Delete the fingerprint template for the given student and finger on the device.",
)
async def delete_fingerprint(
    device_id: int,
    student_id: int,
    finger_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete fingerprint from device."""
    if not 0 <= finger_id <= 9:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="finger_id must be 0-9")
    enrollment_service = EnrollmentService(db)
    try:
        await enrollment_service.delete_fingerprint(
            device_id=device_id,
            student_id=student_id,
            finger_id=finger_id,
            school_id=current_user.school_id,
        )
    except DeviceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DeviceOfflineError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    except EnrollmentError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/cancel/{session_id}",
    response_model=EnrollmentSessionResponse,
    summary="Cancel enrollment",
    description="""
    Cancel an ongoing enrollment session.
    
    Sends cancel command to the device and broadcasts cancellation via WebSocket
    so the frontend receives the update immediately.
    """,
)
async def cancel_enrollment(
    session_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cancel an enrollment session by session_id."""
    enrollment_service = EnrollmentService(db)
    
    try:
        enrollment_session = await enrollment_service.cancel_enrollment_by_session_id(
            session_id=session_id,
            school_id=current_user.school_id,
        )
        
        if not enrollment_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Enrollment session {session_id} not found"
            )
        
        return EnrollmentSessionResponse(
            id=enrollment_session.id,
            session_id=enrollment_session.session_id,
            student_id=enrollment_session.student_id,
            device_id=enrollment_session.device_id,
            finger_id=enrollment_session.finger_id,
            school_id=enrollment_session.school_id,
            status=enrollment_session.status,
            error_message=enrollment_session.error_message,
            template_data=enrollment_session.template_data,
            quality_score=enrollment_session.quality_score,
            started_at=enrollment_session.started_at,
            completed_at=enrollment_session.completed_at,
            created_at=enrollment_session.created_at,
            updated_at=enrollment_session.updated_at,
            is_deleted=enrollment_session.is_deleted,
        )
        
    except EnrollmentError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/status/{session_id}",
    response_model=EnrollmentSessionResponse,
    summary="Check enrollment status",
    description="""
    Check the status of an enrollment session.
    
    This endpoint polls the device to check if enrollment has completed.
    Returns the current enrollment session status.
    """,
)
async def check_enrollment_status(
    session_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Check enrollment status for a session."""
    enrollment_service = EnrollmentService(db)
    
    try:
        enrollment_session = await enrollment_service.repository.get_by_session_id(
            session_id, current_user.school_id
        )
        
        if not enrollment_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Enrollment session {session_id} not found"
            )
        
        return EnrollmentSessionResponse(
            id=enrollment_session.id,
            session_id=enrollment_session.session_id,
            student_id=enrollment_session.student_id,
            device_id=enrollment_session.device_id,
            finger_id=enrollment_session.finger_id,
            school_id=enrollment_session.school_id,
            status=enrollment_session.status,
            error_message=enrollment_session.error_message,
            template_data=enrollment_session.template_data,
            quality_score=enrollment_session.quality_score,
            started_at=enrollment_session.started_at,
            completed_at=enrollment_session.completed_at,
            created_at=enrollment_session.created_at,
            updated_at=enrollment_session.updated_at,
            is_deleted=enrollment_session.is_deleted,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Unexpected error checking enrollment status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while checking enrollment status"
        )
