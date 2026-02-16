"""Shared Pydantic schemas used across services."""

from shared.schemas.attendance import (
    EventTypeEnum,
    AttendanceRecordCreate,
    AttendanceRecordResponse,
    AttendanceEventResponse,
    PaginatedAttendanceResponse,
    AttendanceStatsResponse,
    IngestionSummaryResponse,
)
from shared.schemas.enrollment import (
    EnrollmentStatus,
    EnrollmentSessionBase,
    EnrollmentSessionCreate,
    EnrollmentSessionUpdate,
    EnrollmentSessionResponse,
    EnrollmentStartRequest,
    EnrollmentStartResponse,
    EnrollmentCountResponse,
)

__all__ = [
    "EventTypeEnum",
    "AttendanceRecordCreate",
    "AttendanceRecordResponse",
    "AttendanceEventResponse",
    "PaginatedAttendanceResponse",
    "AttendanceStatsResponse",
    "IngestionSummaryResponse",
    "EnrollmentStatus",
    "EnrollmentSessionBase",
    "EnrollmentSessionCreate",
    "EnrollmentSessionUpdate",
    "EnrollmentSessionResponse",
    "EnrollmentStartRequest",
    "EnrollmentStartResponse",
    "EnrollmentCountResponse",
]
