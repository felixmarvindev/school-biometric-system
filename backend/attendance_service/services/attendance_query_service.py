"""Service layer for querying attendance records."""

import math
from datetime import date
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from attendance_service.repositories.attendance_query_repository import AttendanceQueryRepository
from school_service.models.student import Student
from shared.schemas.attendance import (
    AttendanceEventResponse,
    PaginatedAttendanceResponse,
    AttendanceStatsResponse,
)


class AttendanceQueryService:
    """Business logic for attendance queries."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = AttendanceQueryRepository(db)

    async def list_attendance(
        self,
        school_id: int,
        *,
        target_date: Optional[date] = None,
        student_id: Optional[int] = None,
        class_id: Optional[int] = None,
        device_id: Optional[int] = None,
        event_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> PaginatedAttendanceResponse:
        """Get paginated, filtered attendance records."""
        items, total = await self.repo.list_records(
            school_id=school_id,
            target_date=target_date,
            student_id=student_id,
            class_id=class_id,
            device_id=device_id,
            event_type=event_type,
            page=page,
            page_size=page_size,
        )
        total_pages = math.ceil(total / page_size) if total > 0 else 0

        return PaginatedAttendanceResponse(
            items=[AttendanceEventResponse(**item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def get_stats(
        self,
        school_id: int,
        target_date: date,
    ) -> AttendanceStatsResponse:
        """Get attendance summary stats for a date."""
        # Count total active students in this school
        total_students = (
            await self.db.execute(
                select(func.count(Student.id)).where(
                    Student.school_id == school_id,
                    Student.is_deleted == False,  # noqa: E712
                )
            )
        ).scalar_one()

        stats = await self.repo.get_stats(school_id, target_date, total_students)
        return AttendanceStatsResponse(**stats)

    async def get_student_attendance(
        self,
        school_id: int,
        student_id: int,
        target_date: Optional[date] = None,
    ) -> list[AttendanceEventResponse]:
        """Get attendance records for a specific student."""
        items = await self.repo.get_student_records(school_id, student_id, target_date)
        return [AttendanceEventResponse(**item) for item in items]
