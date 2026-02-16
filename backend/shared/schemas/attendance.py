"""Pydantic schemas for Attendance records."""

from datetime import datetime, date
from enum import Enum
from typing import Optional, Any, Literal

from pydantic import BaseModel, Field


class EventTypeEnum(str, Enum):
    """Attendance event type."""

    IN = "IN"
    OUT = "OUT"
    UNKNOWN = "UNKNOWN"


class AttendanceRecordCreate(BaseModel):
    """Schema for creating an attendance record (internal use)."""

    school_id: int = Field(..., description="School ID")
    device_id: int = Field(..., description="Device ID")
    student_id: Optional[int] = Field(None, description="Student ID (nullable if not matched)")
    device_user_id: str = Field(..., description="User ID from device (uid)")
    occurred_at: datetime = Field(..., description="Timestamp from device")
    event_type: EventTypeEnum = Field(
        default=EventTypeEnum.UNKNOWN,
        description="Event type: IN, OUT, or UNKNOWN",
    )
    raw_payload: Optional[dict[str, Any]] = Field(None, description="Raw event payload from device")


class IngestionSummaryResponse(BaseModel):
    """Response for attendance ingestion endpoint."""

    inserted: int
    skipped: int
    duplicates_filtered: int = Field(default=0, description="Records skipped as duplicate taps")
    total: int


class AttendanceRecordResponse(BaseModel):
    """Schema for attendance record API response (raw, ID-only)."""

    id: int
    school_id: int
    device_id: int
    student_id: Optional[int] = None
    device_user_id: str
    occurred_at: datetime
    event_type: EventTypeEnum = EventTypeEnum.UNKNOWN
    raw_payload: Optional[dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ------------------------------------------------------------------
# Enriched response schemas for the Attendance API (display-ready)
# ------------------------------------------------------------------


class AttendanceEventResponse(BaseModel):
    """Enriched attendance record for API display — includes names, not just IDs."""

    id: int
    student_id: Optional[int] = None
    student_name: Optional[str] = None
    admission_number: Optional[str] = None
    class_name: Optional[str] = None
    device_id: int
    device_name: str
    event_type: EventTypeEnum
    occurred_at: datetime

    class Config:
        from_attributes = True


class PaginatedAttendanceResponse(BaseModel):
    """Paginated list of enriched attendance records."""

    items: list[AttendanceEventResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class AttendanceStatsResponse(BaseModel):
    """Summary statistics for attendance on a given date."""

    date: date
    total_events: int = 0
    checked_in: int = Field(0, description="Unique students currently checked in (last event is IN)")
    checked_out: int = Field(0, description="Unique students whose last event is OUT")
    total_students: int = Field(0, description="Total students in school")
    present_rate: float = Field(0.0, description="Percentage of students with at least one IN today")
