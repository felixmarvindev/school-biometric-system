"""Repository for AttendanceRecord - used by device service for ingestion."""

from datetime import datetime
from typing import Optional

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from attendance_service.models.attendance_record import AttendanceRecord, EventType


class AttendanceRecordRepository:
    """Repository for attendance record bulk insert with deduplication."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_existing_keys(
        self,
        device_id: int,
        school_id: int,
        keys: list[tuple[str, datetime]],
    ) -> set[tuple[str, datetime]]:
        """
        Find which (device_user_id, occurred_at) pairs already exist.

        Args:
            device_id: Device ID
            school_id: School ID
            keys: List of (device_user_id, occurred_at) tuples

        Returns:
            Set of (device_user_id, occurred_at) that already exist
        """
        if not keys:
            return set()

        or_clauses = [
            (AttendanceRecord.device_user_id == uid) & (AttendanceRecord.occurred_at == ts)
            for uid, ts in keys
        ]
        condition = or_(*or_clauses)

        query = (
            select(AttendanceRecord.device_user_id, AttendanceRecord.occurred_at)
            .where(
                AttendanceRecord.device_id == device_id,
                AttendanceRecord.school_id == school_id,
                AttendanceRecord.is_deleted == False,  # noqa: E712
                condition,
            )
        )
        result = await self.db.execute(query)
        rows = result.all()
        return {(r[0], r[1]) for r in rows}

    async def bulk_insert_enriched(
        self,
        records: list[AttendanceRecord],
    ) -> int:
        """
        Bulk insert pre-built AttendanceRecord objects.

        The caller is responsible for setting all fields (school_id, device_id,
        student_id, device_user_id, occurred_at, event_type, raw_payload).

        Args:
            records: List of AttendanceRecord ORM instances ready to insert.

        Returns:
            Number of records inserted.
        """
        if not records:
            return 0
        self.db.add_all(records)
        await self.db.flush()
        return len(records)
