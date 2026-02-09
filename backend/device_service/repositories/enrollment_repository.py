"""Repository for EnrollmentSession data access."""

import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional, Sequence

from device_service.models.enrollment import EnrollmentSession, EnrollmentStatus
from shared.schemas.enrollment import EnrollmentSessionCreate, EnrollmentSessionUpdate


class EnrollmentRepository:
    """Repository for EnrollmentSession database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, enrollment_data: EnrollmentSessionCreate) -> EnrollmentSession:
        """
        Create a new enrollment session.
        
        Args:
            enrollment_data: Enrollment session creation data
            
        Returns:
            Created EnrollmentSession instance
        """
        # Generate session_id if not provided
        session_id = enrollment_data.session_id or str(uuid.uuid4())
        
        enrollment_session = EnrollmentSession(
            session_id=session_id,
            student_id=enrollment_data.student_id,
            device_id=enrollment_data.device_id,
            finger_id=enrollment_data.finger_id,
            school_id=enrollment_data.school_id,
            status=enrollment_data.status.value if isinstance(enrollment_data.status, EnrollmentStatus) else enrollment_data.status,
        )
        self.db.add(enrollment_session)
        await self.db.commit()
        await self.db.refresh(enrollment_session)
        return enrollment_session

    async def get_by_id(
        self, enrollment_id: int, school_id: Optional[int] = None
    ) -> Optional[EnrollmentSession]:
        """
        Get enrollment session by ID.
        
        Args:
            enrollment_id: Enrollment session ID
            school_id: Optional school ID to filter by (for authorization)
            
        Returns:
            EnrollmentSession instance or None if not found
        """
        query = select(EnrollmentSession).where(
            EnrollmentSession.id == enrollment_id,
            EnrollmentSession.is_deleted == False
        )
        
        if school_id is not None:
            query = query.where(EnrollmentSession.school_id == school_id)
        
        query = query.options(
            selectinload(EnrollmentSession.student),
            selectinload(EnrollmentSession.device),
            selectinload(EnrollmentSession.school)
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_session_id(
        self, session_id: str, school_id: Optional[int] = None
    ) -> Optional[EnrollmentSession]:
        """
        Get enrollment session by session_id.
        
        Args:
            session_id: Session ID (UUID string)
            school_id: Optional school ID to filter by (for authorization)
            
        Returns:
            EnrollmentSession instance or None if not found
        """
        query = select(EnrollmentSession).where(
            EnrollmentSession.session_id == session_id,
            EnrollmentSession.is_deleted == False
        )
        
        if school_id is not None:
            query = query.where(EnrollmentSession.school_id == school_id)
        
        query = query.options(
            selectinload(EnrollmentSession.student),
            selectinload(EnrollmentSession.device),
            selectinload(EnrollmentSession.school)
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update(
        self,
        enrollment_id: int,
        enrollment_data: EnrollmentSessionUpdate,
        school_id: Optional[int] = None
    ) -> Optional[EnrollmentSession]:
        """
        Update enrollment session.
        
        Args:
            enrollment_id: Enrollment session ID
            enrollment_data: Update data
            school_id: Optional school ID to verify ownership
            
        Returns:
            Updated EnrollmentSession instance or None if not found
        """
        query = select(EnrollmentSession).where(
            EnrollmentSession.id == enrollment_id,
            EnrollmentSession.is_deleted == False
        )
        
        if school_id is not None:
            query = query.where(EnrollmentSession.school_id == school_id)
        
        result = await self.db.execute(query)
        enrollment_session = result.scalar_one_or_none()
        
        if not enrollment_session:
            return None
        
        # Convert Pydantic model to dict, excluding unset fields
        update_dict = enrollment_data.model_dump(exclude_unset=True)
        
        # Handle status enum conversion
        if "status" in update_dict and isinstance(update_dict["status"], EnrollmentStatus):
            update_dict["status"] = update_dict["status"].value
        
        # Update fields
        for key, value in update_dict.items():
            setattr(enrollment_session, key, value)
        
        await self.db.commit()
        await self.db.refresh(enrollment_session)
        return enrollment_session

    async def update_status(
        self,
        enrollment_id: int,
        status: EnrollmentStatus,
        error_message: Optional[str] = None,
        completed_at: Optional[datetime] = None,
    ) -> bool:
        """
        Update enrollment session status.
        
        Args:
            enrollment_id: Enrollment session ID
            status: New status
            error_message: Optional error message
            completed_at: Optional completion timestamp
            
        Returns:
            True if updated, False if not found
        """
        enrollment_session = await self.get_by_id(enrollment_id)
        
        if not enrollment_session:
            return False
        
        enrollment_session.status = status.value if isinstance(status, EnrollmentStatus) else status
        if error_message is not None:
            enrollment_session.error_message = error_message
        if completed_at is not None:
            enrollment_session.completed_at = completed_at
        
        await self.db.commit()
        await self.db.refresh(enrollment_session)
        return True

    async def delete(
        self, enrollment_id: int, school_id: Optional[int] = None
    ) -> bool:
        """
        Soft delete an enrollment session.
        
        Args:
            enrollment_id: Enrollment session ID
            school_id: Optional school ID to verify ownership
            
        Returns:
            True if deleted, False if not found
        """
        query = select(EnrollmentSession).where(
            EnrollmentSession.id == enrollment_id,
            EnrollmentSession.is_deleted == False
        )
        
        if school_id is not None:
            query = query.where(EnrollmentSession.school_id == school_id)
        
        result = await self.db.execute(query)
        enrollment_session = result.scalar_one_or_none()
        
        if not enrollment_session:
            return False
        
        enrollment_session.is_deleted = True
        await self.db.commit()
        return True

    async def get_completed_by_student(
        self, school_id: int, student_id: int
    ) -> Sequence[EnrollmentSession]:
        """
        Get completed enrollment sessions for a student (for UI and sync readiness).

        Returns distinct student-device-finger combinations (latest per combo).
        """
        from sqlalchemy import distinct, func

        # Subquery: latest completed enrollment per (student_id, device_id, finger_id)
        subq = (
            select(
                EnrollmentSession.student_id,
                EnrollmentSession.device_id,
                EnrollmentSession.finger_id,
                func.max(EnrollmentSession.id).label("max_id"),
            )
            .where(
                EnrollmentSession.school_id == school_id,
                EnrollmentSession.student_id == student_id,
                EnrollmentSession.status == EnrollmentStatus.COMPLETED.value,
                EnrollmentSession.is_deleted == False,
            )
            .group_by(
                EnrollmentSession.student_id,
                EnrollmentSession.device_id,
                EnrollmentSession.finger_id,
            )
        ).subquery()

        query = (
            select(EnrollmentSession)
            .join(subq, EnrollmentSession.id == subq.c.max_id)
            .options(
                selectinload(EnrollmentSession.student),
                selectinload(EnrollmentSession.device),
            )
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_completed_by_device(
        self, school_id: int, device_id: int
    ) -> Sequence[EnrollmentSession]:
        """
        Get completed enrollment sessions for a device (for UI and sync readiness).

        Returns distinct student-device-finger combinations (latest per combo).
        """
        from sqlalchemy import func

        subq = (
            select(
                EnrollmentSession.student_id,
                EnrollmentSession.device_id,
                EnrollmentSession.finger_id,
                func.max(EnrollmentSession.id).label("max_id"),
            )
            .where(
                EnrollmentSession.school_id == school_id,
                EnrollmentSession.device_id == device_id,
                EnrollmentSession.status == EnrollmentStatus.COMPLETED.value,
                EnrollmentSession.is_deleted == False,
            )
            .group_by(
                EnrollmentSession.student_id,
                EnrollmentSession.device_id,
                EnrollmentSession.finger_id,
            )
        ).subquery()

        query = (
            select(EnrollmentSession)
            .join(subq, EnrollmentSession.id == subq.c.max_id)
            .options(
                selectinload(EnrollmentSession.student),
                selectinload(EnrollmentSession.device),
            )
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_enrolled_fingers_from_db(
        self, school_id: int, student_id: int, device_id: int
    ) -> list[int]:
        """
        Get finger IDs enrolled for student on device from database (offline lookup).
        """
        query = select(EnrollmentSession.finger_id).where(
            EnrollmentSession.school_id == school_id,
            EnrollmentSession.student_id == student_id,
            EnrollmentSession.device_id == device_id,
            EnrollmentSession.status == EnrollmentStatus.COMPLETED.value,
            EnrollmentSession.is_deleted == False,
        )
        result = await self.db.execute(query)
        fingers = list(dict.fromkeys(r[0] for r in result.fetchall()))
        return sorted(fingers)
