"""Custom exceptions for Device Service."""

from typing import Optional


class AppException(Exception):
    """Base exception for application errors."""

    def __init__(self, message: str, code: Optional[str] = None):
        self.message = message
        self.code = code
        super().__init__(self.message)


class DeviceOfflineError(AppException):
    """Raised when device is offline or unreachable."""

    def __init__(self, device_id: int):
        super().__init__(
            message=f"Device {device_id} is offline or unreachable",
            code="DEVICE_OFFLINE"
        )
        self.device_id = device_id


class DeviceNotFoundError(AppException):
    """Raised when device is not found."""

    def __init__(self, device_id: int):
        super().__init__(
            message=f"Device {device_id} not found",
            code="DEVICE_NOT_FOUND"
        )
        self.device_id = device_id


class EnrollmentError(AppException):
    """Raised when enrollment operation fails."""

    def __init__(self, message: str, code: Optional[str] = None):
        super().__init__(
            message=message,
            code=code or "ENROLLMENT_ERROR"
        )


class EnrollmentInProgressError(AppException):
    """Raised when enrollment is already in progress."""

    def __init__(self, session_id: str):
        super().__init__(
            message=f"Enrollment session {session_id} is already in progress",
            code="ENROLLMENT_IN_PROGRESS"
        )
        self.session_id = session_id


class StudentNotFoundError(AppException):
    """Raised when student is not found."""

    def __init__(self, student_id: int):
        super().__init__(
            message=f"Student {student_id} not found",
            code="STUDENT_NOT_FOUND"
        )
        self.student_id = student_id
