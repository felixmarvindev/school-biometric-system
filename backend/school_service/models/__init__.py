"""Database models for School Service."""

from school_service.models.school import School
from school_service.models.user import User
from school_service.models.student import Student, Gender
from school_service.models.academic_class import AcademicClass
from school_service.models.stream import Stream

# Import Device and DeviceGroup models to ensure they're registered with SQLAlchemy
# when School model initializes its relationships
from device_service.models.device import Device  # noqa: F401
from device_service.models.device_group import DeviceGroup  # noqa: F401

# Type alias for convenience (Class is a Python keyword, so model is named AcademicClass)
Class = AcademicClass

__all__ = ["School", "User", "Student", "Gender", "AcademicClass", "Class", "Stream"]
