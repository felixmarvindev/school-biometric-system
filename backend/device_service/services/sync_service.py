"""Service for syncing students to devices."""

import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from device_service.models.device import Device, DeviceStatus
from device_service.repositories.device_repository import DeviceRepository
from device_service.services.device_connection import DeviceConnectionService
from device_service.exceptions import (
    DeviceOfflineError,
    DeviceNotFoundError,
    StudentNotFoundError,
)

# Import Student from school_service - device_service shares DB
from school_service.models.student import Student

logger = logging.getLogger(__name__)


class SyncService:
    """Service for syncing students to biometric devices."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.device_repository = DeviceRepository(db)
        self.connection_service = DeviceConnectionService(db)

    async def _get_student(self, student_id: int, school_id: int) -> Student:
        """Fetch student by ID within school. Raises StudentNotFoundError if not found."""
        result = await self.db.execute(
            select(Student).where(
                Student.id == student_id,
                Student.school_id == school_id,
                Student.is_deleted == False,
            )
        )
        student = result.scalar_one_or_none()
        if not student:
            raise StudentNotFoundError(student_id)
        return student

    async def sync_student_to_device(
        self,
        student_id: int,
        device_id: int,
        school_id: int,
    ) -> None:
        """
        Sync a student to a device (add/update user on device).

        Creates or updates the user record on the device so that fingerprint
        enrollment can proceed. Uses student_id as user_id on the device.

        Args:
            student_id: Student ID
            device_id: Device ID
            school_id: School ID (for authorization)

        Raises:
            StudentNotFoundError: If student not found
            DeviceNotFoundError: If device not found
            DeviceOfflineError: If device is offline
        """
        student = await self._get_student(student_id, school_id)

        device = await self.device_repository.get_by_id(device_id, school_id)
        if not device:
            raise DeviceNotFoundError(device_id)
        if device.status != DeviceStatus.ONLINE:
            raise DeviceOfflineError(device_id)

        conn = await self.connection_service.get_connection(device)
        if not conn:
            raise DeviceOfflineError(device_id)

        # Format name for device: "AdmissionNumber - FirstName LastName"
        name = f"{student.admission_number} - {student.first_name} {student.last_name}"
        user_id_str = str(student_id)

        await conn.set_user(
            uid=student_id,
            name=name,
            user_id=user_id_str,
            privilege=0,
        )
        logger.info(f"Synced student {student_id} to device {device_id}")

    async def check_student_on_device(
        self,
        student_id: int,
        device_id: int,
        school_id: int,
    ) -> bool:
        """
        Check if a student is synced to a device.

        Args:
            student_id: Student ID
            device_id: Device ID
            school_id: School ID (for authorization)

        Returns:
            True if student exists on device, False otherwise

        Raises:
            DeviceNotFoundError: If device not found
            DeviceOfflineError: If device is offline
        """
        device = await self.device_repository.get_by_id(device_id, school_id)
        if not device:
            raise DeviceNotFoundError(device_id)
        if device.status != DeviceStatus.ONLINE:
            raise DeviceOfflineError(device_id)

        conn = await self.connection_service.get_connection(device)
        if not conn:
            raise DeviceOfflineError(device_id)

        return await conn.student_on_device(student_id)
