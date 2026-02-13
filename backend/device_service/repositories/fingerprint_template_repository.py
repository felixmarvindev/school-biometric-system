"""Repository for FingerprintTemplate data access."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from device_service.models.fingerprint_template import FingerprintTemplate


class FingerprintTemplateRepository:
    """Repository for FingerprintTemplate database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        student_id: int,
        device_id: int,
        finger_id: int,
        encrypted_data: str,
        school_id: int,
        quality_score: Optional[int] = None,
        source_enrollment_session_id: Optional[int] = None,
    ) -> FingerprintTemplate:
        """Create a fingerprint template record."""
        template = FingerprintTemplate(
            student_id=student_id,
            device_id=device_id,
            finger_id=finger_id,
            encrypted_data=encrypted_data,
            quality_score=quality_score,
            source_enrollment_session_id=source_enrollment_session_id,
            school_id=school_id,
        )
        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)
        return template

    async def get_by_student(
        self, student_id: int, school_id: Optional[int] = None
    ) -> List[FingerprintTemplate]:
        """Get all non-deleted templates for a student."""
        query = select(FingerprintTemplate).where(
            FingerprintTemplate.student_id == student_id,
            FingerprintTemplate.is_deleted == False,
        )
        if school_id is not None:
            query = query.where(FingerprintTemplate.school_id == school_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_student_and_finger(
        self,
        student_id: int,
        finger_id: int,
        school_id: Optional[int] = None,
    ) -> Optional[FingerprintTemplate]:
        """Get the latest template for a student and finger (e.g. for transfer)."""
        query = (
            select(FingerprintTemplate)
            .where(
                FingerprintTemplate.student_id == student_id,
                FingerprintTemplate.finger_id == finger_id,
                FingerprintTemplate.is_deleted == False,
            )
            .order_by(FingerprintTemplate.created_at.desc())
        )
        if school_id is not None:
            query = query.where(FingerprintTemplate.school_id == school_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
