# Task 064: Attendance Records API Endpoints

## Story/Phase
- **Story**: Story 05: Attendance Tracking
- **Phase**: Phase 3 & 4: Attendance Display & History

## Task Type
- [x] Backend
- [ ] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Description

Create REST API endpoints for querying attendance records. These serve both the live feed (initial load + polling fallback) and the history table. Routes live in the **API Gateway** since they read from the shared database and are consumed by the frontend.

### Endpoints

1. **`GET /api/v1/attendance`** — List attendance records with filters and pagination.
2. **`GET /api/v1/attendance/stats`** — Summary stats (total events, checked in, checked out, present rate) for a given date.
3. **`GET /api/v1/attendance/students/{student_id}`** — Attendance records for a single student (for the detail panel).

## Acceptance Criteria

1. [x] `GET /api/v1/attendance` returns paginated attendance records, newest first.
2. [x] Supports query filters: `date` (defaults today), `student_id`, `class_id`, `device_id`, `event_type` (IN/OUT/UNKNOWN).
3. [x] Supports `page` and `page_size` (default 50, max 200) pagination params.
4. [x] Response includes student name, admission number, class name, device name (joined data, not just IDs).
5. [x] `GET /api/v1/attendance/stats` returns `total_events`, `checked_in`, `checked_out`, `present_rate` for a date.
6. [x] `GET /api/v1/attendance/students/{student_id}` returns records for a student with optional date filter.
7. [x] All endpoints are school-scoped (use `current_user.school_id`).
8. [x] Proper error handling and input validation.

## Notes

- The response schema should include enriched data (student name, class, device name) not just foreign key IDs — the frontend needs display-ready data.
- Present rate = (unique students with at least one IN today) / (total students in school) × 100.
- Use `Africa/Nairobi` timezone for "today" boundary (same as entry/exit service).
