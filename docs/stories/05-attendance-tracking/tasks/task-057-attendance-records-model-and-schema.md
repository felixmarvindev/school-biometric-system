# Task 057: Attendance Records Model + Schema

## Story/Phase
- **Story**: Story 05: Attendance Tracking
- **Phase**: Phase 1: Event Capture

## Task Type
- [ ] Backend
- [ ] Frontend
- [x] Database
- [x] Backend
- [ ] DevOps
- [ ] Documentation

## Description

Create database model(s) and Pydantic schemas for attendance records captured from biometric devices.

## Acceptance Criteria

1. [ ] `attendance_records` table/model exists with required fields:
   - `id`, `created_at`, `updated_at`, `is_deleted`
   - `school_id`
   - `device_id`
   - `student_id` (nullable if user not mapped yet)
   - `device_user_id` / `uid` (string/int as appropriate)
   - `occurred_at` (timestamp from device)
   - `raw_payload` (JSON, optional)
2. [ ] Appropriate indexes exist (`device_id`, `school_id`, `occurred_at`, `device_user_id`).
3. [ ] Alembic migration is generated via `--autogenerate` (no manual edits).
4. [ ] Shared schemas exist for:
   - `AttendanceRecordResponse`
   - `AttendanceRecordCreate` (if needed internally)

## Notes

- Use soft deletes (`is_deleted`) per system standard.
- Keep it flexible for later entry/exit logic (phase 2).

## Files to Create/Modify (Expected)

- `backend/attendance_service/models/attendance_record.py` (or appropriate service path)
- `backend/shared/schemas/attendance.py`
- `backend/<service>/alembic/versions/*_attendance_records.py` (generated)

