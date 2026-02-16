"""Database models for Attendance Service."""

from attendance_service.models.attendance_record import AttendanceRecord, EventType  # noqa: F401

__all__ = ["AttendanceRecord", "EventType"]