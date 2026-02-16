# Task 065: WebSocket Attendance Event Emission

## Story/Phase
- **Story**: Story 05: Attendance Tracking
- **Phase**: Phase 3: Attendance Display

## Task Type
- [x] Backend
- [ ] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Description

Emit real-time attendance events via WebSocket (Socket.IO) whenever new attendance records are ingested. This powers the live feed on the frontend — events appear instantly without polling.

## Acceptance Criteria

1. [x] After successful ingestion, newly inserted attendance records are emitted as `attendance_events` WebSocket message.
2. [x] Payload includes: `id`, `student_name`, `admission_number`, `class_name`, `device_name`, `event_type` (IN/OUT/UNKNOWN), `occurred_at`.
3. [x] Events are emitted to school-scoped connections (broadcaster groups by school_id).
4. [x] Frontend clients join via `/ws/attendance?token=<jwt>` and are auto-grouped by school.
5. [x] Works for both manual ingestion (API endpoint) and automatic polling (AttendancePollService).
6. [x] Gracefully handles WebSocket being unavailable (ingestion still works, just no real-time push).

## Notes

- Check the existing WebSocket/Socket.IO setup in the codebase — there should be a `sio` instance from the enrollment feature.
- The poll service runs in background tasks with their own DB sessions — the emission should happen after commit.
- Consider emitting a batch event for efficiency if many records are ingested at once.
