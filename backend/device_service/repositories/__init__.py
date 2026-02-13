"""Repositories for Device Service."""

from device_service.repositories.device_repository import DeviceRepository
from device_service.repositories.enrollment_repository import EnrollmentRepository
from device_service.repositories.fingerprint_template_repository import FingerprintTemplateRepository

__all__ = [
    "DeviceRepository",
    "EnrollmentRepository",
    "FingerprintTemplateRepository",
]

