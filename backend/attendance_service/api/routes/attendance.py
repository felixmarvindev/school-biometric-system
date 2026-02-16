"""API routes for querying attendance records."""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from attendance_service.core.database import get_db
from attendance_service.api.dependencies import get_current_user
from attendance_service.services.attendance_query_service import AttendanceQueryService
from shared.schemas.user import UserResponse
from shared.schemas.attendance import (
    AttendanceEventResponse,
    AttendanceStatsResponse,
    PaginatedAttendanceResponse,
)

router = APIRouter(prefix="/api/v1/attendance", tags=["attendance"])


@router.get(
    "",
    response_model=PaginatedAttendanceResponse,
    summary="List attendance records",
    description="""
    Get a paginated list of attendance records with optional filters.
    
    Returns enriched records with student name, admission number, class, and device name.
    Defaults to today's records if no date is specified.
    """,
    responses={
        200: {"description": "Attendance records retrieved successfully"},
    },
)
async def list_attendance(
    target_date: Optional[date] = Query(None, description="Filter by date (YYYY-MM-DD). Defaults to today if omitted."),
    student_id: Optional[int] = Query(None, description="Filter by student ID"),
    class_id: Optional[int] = Query(None, description="Filter by class ID"),
    device_id: Optional[int] = Query(None, description="Filter by device ID"),
    event_type: Optional[str] = Query(None, description="Filter by event type: IN, OUT, or UNKNOWN"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=200, description="Items per page (max 200)"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List attendance records with pagination and filtering."""
    # Default to today if no date specified
    if target_date is None:
        target_date = date.today()

    # Validate event_type if provided
    if event_type is not None:
        event_type = event_type.upper()
        if event_type not in ("IN", "OUT", "UNKNOWN"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="event_type must be one of: IN, OUT, UNKNOWN",
            )

    service = AttendanceQueryService(db)
    return await service.list_attendance(
        school_id=current_user.school_id,
        target_date=target_date,
        student_id=student_id,
        class_id=class_id,
        device_id=device_id,
        event_type=event_type,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/stats",
    response_model=AttendanceStatsResponse,
    summary="Get attendance statistics",
    description="""
    Get summary attendance statistics for a given date.
    
    Returns: total events, students currently checked in, checked out, 
    total students in school, and present rate percentage.
    """,
    responses={
        200: {"description": "Attendance stats retrieved successfully"},
    },
)
async def get_attendance_stats(
    target_date: Optional[date] = Query(None, description="Date for stats (YYYY-MM-DD). Defaults to today."),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get attendance summary statistics for a date."""
    if target_date is None:
        target_date = date.today()

    service = AttendanceQueryService(db)
    return await service.get_stats(
        school_id=current_user.school_id,
        target_date=target_date,
    )


@router.get(
    "/students/{student_id}",
    response_model=list[AttendanceEventResponse],
    summary="Get student attendance records",
    description="""
    Get attendance records for a specific student.
    
    Optionally filter by date. Returns records in chronological order 
    (oldest first) — suitable for timeline display.
    """,
    responses={
        200: {"description": "Student attendance records retrieved successfully"},
    },
)
async def get_student_attendance(
    student_id: int,
    target_date: Optional[date] = Query(None, description="Filter by date (YYYY-MM-DD). Returns all dates if omitted."),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get attendance records for a specific student."""
    service = AttendanceQueryService(db)
    return await service.get_student_attendance(
        school_id=current_user.school_id,
        student_id=student_id,
        target_date=target_date,
    )
