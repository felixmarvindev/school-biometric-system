"""Service for resolving device_user_id to student_id.

During sync, students are written to devices with uid = student_id and
user_id = str(student_id).  So device_user_id in attendance logs is simply
str(student_id).  This service validates that the student exists and belongs
to the correct school.
"""

import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from school_service.models.student import Student

logger = logging.getLogger(__name__)


class StudentMatchingService:
    """Batch-resolves device_user_id values to student_id values."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def resolve_batch(
        self,
        school_id: int,
        device_user_ids: list[str],
    ) -> dict[str, int]:
        """
        Resolve a batch of device_user_ids to student IDs.

        Since the sync service writes ``uid = student_id`` and
        ``user_id = str(student_id)`` onto the device, the mapping is
        a direct integer parse + existence check.

        Args:
            school_id: The school these records belong to.
            device_user_ids: List of device_user_id strings from attendance logs.

        Returns:
            Dict mapping device_user_id -> student_id for matched students.
            Unmatched IDs are omitted from the dict.
        """
        # Parse candidate student IDs (skip non-numeric values)
        candidate_ids: dict[int, str] = {}  # student_id -> device_user_id
        for duid in set(device_user_ids):
            try:
                sid = int(duid)
                candidate_ids[sid] = duid
            except (ValueError, TypeError):
                logger.debug("Non-numeric device_user_id '%s' — cannot match", duid)
                continue

        if not candidate_ids:
            return {}

        # Batch-query: which of these student IDs actually exist in this school?
        query = (
            select(Student.id)
            .where(
                Student.school_id == school_id,
                Student.id.in_(list(candidate_ids.keys())),
                Student.is_deleted == False,  # noqa: E712
            )
        )
        result = await self.db.execute(query)
        existing_ids = {row[0] for row in result.all()}

        # Build the mapping
        mapping: dict[str, int] = {}
        for sid, duid in candidate_ids.items():
            if sid in existing_ids:
                mapping[duid] = sid
            else:
                logger.debug(
                    "device_user_id '%s' parsed as student %d but student not found in school %d",
                    duid,
                    sid,
                    school_id,
                )

        logger.debug(
            "Student matching: %d/%d device_user_ids resolved for school %d",
            len(mapping),
            len(set(device_user_ids)),
            school_id,
        )
        return mapping

    async def resolve_single(
        self,
        school_id: int,
        device_user_id: str,
    ) -> Optional[int]:
        """
        Resolve a single device_user_id to a student_id.

        Convenience wrapper around resolve_batch for single lookups.
        """
        mapping = await self.resolve_batch(school_id, [device_user_id])
        return mapping.get(device_user_id)
