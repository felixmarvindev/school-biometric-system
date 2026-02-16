"""Repository for querying attendance records (read-side, used by Attendance Service API)."""

import math
from datetime import date, datetime, timedelta
from typing import Optional

import pytz
from sqlalchemy import select, func, and_, case, distinct
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from attendance_service.models.attendance_record import AttendanceRecord, EventType
from school_service.models.student import Student
from device_service.models.device import Device


class AttendanceQueryRepository:
    """Read-optimised queries for the attendance API."""

    def __init__(self, db: AsyncSession, tz_name: str = "Africa/Nairobi"):
        self.db = db
        self.tz = pytz.timezone(tz_name)

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    def _day_boundaries(self, target_date: date) -> tuple[datetime, datetime]:
        """Return (start_utc, end_utc) for *target_date* in the configured tz."""
        start_local = self.tz.localize(datetime.combine(target_date, datetime.min.time()))
        end_local = start_local + timedelta(days=1)
        return start_local.astimezone(pytz.utc), end_local.astimezone(pytz.utc)

    # ------------------------------------------------------------------
    # list (paginated + filtered)
    # ------------------------------------------------------------------

    async def list_records(
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
    ) -> tuple[list[dict], int]:
        """
        Return a page of enriched attendance records plus total count.

        Each item is a dict with display-ready fields (student_name,
        admission_number, class_name, device_name, etc.).
        """
        # base conditions
        conditions = [
            AttendanceRecord.school_id == school_id,
            AttendanceRecord.is_deleted == False,  # noqa: E712
        ]

        if target_date is not None:
            start_utc, end_utc = self._day_boundaries(target_date)
            conditions.append(AttendanceRecord.occurred_at >= start_utc)
            conditions.append(AttendanceRecord.occurred_at < end_utc)

        if student_id is not None:
            conditions.append(AttendanceRecord.student_id == student_id)

        if device_id is not None:
            conditions.append(AttendanceRecord.device_id == device_id)

        if event_type is not None:
            conditions.append(AttendanceRecord.event_type == event_type)

        if class_id is not None:
            # join through student → class
            conditions.append(Student.class_id == class_id)

        where = and_(*conditions)

        # --- count ---
        count_q = select(func.count(AttendanceRecord.id))
        if class_id is not None:
            count_q = count_q.join(Student, AttendanceRecord.student_id == Student.id, isouter=True)
        count_q = count_q.where(where)
        total = (await self.db.execute(count_q)).scalar_one()

        # --- data query ---
        q = (
            select(AttendanceRecord)
            .options(selectinload(AttendanceRecord.student), selectinload(AttendanceRecord.device))
        )
        if class_id is not None:
            q = q.join(Student, AttendanceRecord.student_id == Student.id, isouter=True)
        q = (
            q.where(where)
            .order_by(AttendanceRecord.occurred_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self.db.execute(q)
        records = result.scalars().all()

        items = [self._to_event_dict(r) for r in records]
        return items, total

    # ------------------------------------------------------------------
    # stats
    # ------------------------------------------------------------------

    async def get_stats(
        self,
        school_id: int,
        target_date: date,
        total_students: int,
    ) -> dict:
        """
        Compute attendance stats for a single day.

        Returns dict with total_events, checked_in, checked_out, present_rate.
        """
        start_utc, end_utc = self._day_boundaries(target_date)

        base = and_(
            AttendanceRecord.school_id == school_id,
            AttendanceRecord.is_deleted == False,  # noqa: E712
            AttendanceRecord.occurred_at >= start_utc,
            AttendanceRecord.occurred_at < end_utc,
        )

        # total events
        total_events = (
            await self.db.execute(select(func.count(AttendanceRecord.id)).where(base))
        ).scalar_one()

        # unique students with at least one event today
        unique_present = (
            await self.db.execute(
                select(func.count(distinct(AttendanceRecord.student_id))).where(
                    base, AttendanceRecord.student_id.isnot(None)
                )
            )
        ).scalar_one()

        # For checked_in / checked_out we need each student's *last* event type today.
        # Subquery: max occurred_at per student today
        subq = (
            select(
                AttendanceRecord.student_id,
                func.max(AttendanceRecord.occurred_at).label("max_ts"),
            )
            .where(base, AttendanceRecord.student_id.isnot(None))
            .group_by(AttendanceRecord.student_id)
            .subquery()
        )

        last_events = (
            await self.db.execute(
                select(AttendanceRecord.event_type, func.count())
                .join(
                    subq,
                    and_(
                        AttendanceRecord.student_id == subq.c.student_id,
                        AttendanceRecord.occurred_at == subq.c.max_ts,
                    ),
                )
                .where(base)
                .group_by(AttendanceRecord.event_type)
            )
        ).all()

        checked_in = 0
        checked_out = 0
        for evt, cnt in last_events:
            if evt == EventType.IN:
                checked_in = cnt
            elif evt == EventType.OUT:
                checked_out = cnt

        present_rate = round((unique_present / total_students) * 100, 1) if total_students > 0 else 0.0

        return {
            "date": target_date,
            "total_events": total_events,
            "checked_in": checked_in,
            "checked_out": checked_out,
            "total_students": total_students,
            "present_rate": present_rate,
        }

    # ------------------------------------------------------------------
    # student detail
    # ------------------------------------------------------------------

    async def get_student_records(
        self,
        school_id: int,
        student_id: int,
        target_date: Optional[date] = None,
    ) -> list[dict]:
        """
        Get all attendance records for a specific student, optionally filtered by date.
        Sorted chronologically (oldest first, for timeline display).
        """
        conditions = [
            AttendanceRecord.school_id == school_id,
            AttendanceRecord.student_id == student_id,
            AttendanceRecord.is_deleted == False,  # noqa: E712
        ]

        if target_date is not None:
            start_utc, end_utc = self._day_boundaries(target_date)
            conditions.append(AttendanceRecord.occurred_at >= start_utc)
            conditions.append(AttendanceRecord.occurred_at < end_utc)

        q = (
            select(AttendanceRecord)
            .options(selectinload(AttendanceRecord.student), selectinload(AttendanceRecord.device))
            .where(and_(*conditions))
            .order_by(AttendanceRecord.occurred_at.asc())
        )
        result = await self.db.execute(q)
        records = result.scalars().all()
        return [self._to_event_dict(r) for r in records]

    # ------------------------------------------------------------------
    # mapping helper
    # ------------------------------------------------------------------

    @staticmethod
    def _to_event_dict(record: AttendanceRecord) -> dict:
        """Convert an ORM record (with loaded relationships) to a display dict."""
        student = record.student
        device = record.device

        student_name = None
        admission_number = None
        class_name = None
        if student:
            student_name = f"{student.first_name} {student.last_name}"
            admission_number = student.admission_number
            if hasattr(student, "class_") and student.class_:
                class_name = student.class_.name
            elif hasattr(student, "academic_class") and student.academic_class:
                class_name = student.academic_class.name

        return {
            "id": record.id,
            "student_id": record.student_id,
            "student_name": student_name,
            "admission_number": admission_number,
            "class_name": class_name,
            "device_id": record.device_id,
            "device_name": device.name if device else "Unknown Device",
            "event_type": record.event_type,
            "occurred_at": record.occurred_at,
        }
