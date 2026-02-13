"""Service for syncing students to devices and transferring templates."""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from device_service.models.device import Device, DeviceStatus
from device_service.repositories.device_repository import DeviceRepository
from device_service.repositories.fingerprint_template_repository import FingerprintTemplateRepository
from device_service.services.device_connection import DeviceConnectionService
from device_service.core.encryption import decrypt_template
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
        self.fingerprint_template_repository = FingerprintTemplateRepository(db)

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

    async def transfer_templates_to_device(
        self,
        student_id: int,
        device_id: int,
        school_id: int,
    ) -> int:
        """
        Transfer stored fingerprint templates for a student to a target device.

        Syncs the student to the device if not present, then loads templates from
        fingerprint_templates, decrypts each, and pushes to the device.

        Args:
            student_id: Student ID
            device_id: Target device ID
            school_id: School ID (for authorization)

        Returns:
            Number of templates successfully transferred

        Raises:
            StudentNotFoundError: If student not found
            DeviceNotFoundError: If device not found
            DeviceOfflineError: If device is offline
        """
        # Ensure student exists on device (sync if not)
        if not await self.check_student_on_device(student_id, device_id, school_id):
            await self.sync_student_to_device(student_id, device_id, school_id)

        device = await self.device_repository.get_by_id(device_id, school_id)
        if not device:
            raise DeviceNotFoundError(device_id)
        conn = await self.connection_service.get_connection(device)
        if not conn:
            raise DeviceOfflineError(device_id)

        templates = await self.fingerprint_template_repository.get_by_student(
            student_id, school_id
        )
        if not templates:
            return 0

        # One template per finger (latest by created_at)
        by_finger: dict[int, type(templates[0])] = {}
        for t in sorted(templates, key=lambda x: x.id, reverse=True):
            if t.finger_id not in by_finger:
                by_finger[t.finger_id] = t

        user_id_str = str(student_id)
        transferred = 0
        for finger_id, rec in by_finger.items():
            raw = decrypt_template(rec.encrypted_data)
            if not raw:
                logger.warning(
                    "Skipping template transfer for student_id=%s finger_id=%s: decryption failed",
                    student_id,
                    finger_id,
                )
                continue
            try:
                await conn.set_user_template(user_id_str, finger_id, raw)
                transferred += 1
            except Exception as e:
                logger.warning(
                    "Failed to push template student_id=%s finger_id=%s: %s",
                    student_id,
                    finger_id,
                    e,
                )
        logger.info(
            "Transferred %s/%s templates for student %s to device %s",
            transferred,
            len(by_finger),
            student_id,
            device_id,
        )
        return transferred
