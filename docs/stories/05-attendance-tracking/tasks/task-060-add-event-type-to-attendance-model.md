# Task 060: Add event_type to Attendance Record Model

## Story/Phase
- **Story**: Story 05: Attendance Tracking
- **Phase**: Phase 2: Entry/Exit Logic

## Task Type
- [x] Backend
- [ ] Frontend
- [x] Database
- [ ] DevOps
- [ ] Documentation

## Description

Add an `event_type` column to the `AttendanceRecord` model to store whether each attendance tap is an entry (IN), exit (OUT), or unknown. Update the Pydantic schemas to include the new field.

## Acceptance Criteria

1. [x] `event_type` column added to `AttendanceRecord` model as a String(10) with values: `IN`, `OUT`, `UNKNOWN`.
2. [x] Column is NOT NULL with server_default `'UNKNOWN'` (existing records get UNKNOWN).
3. [x] `AttendanceRecordResponse` schema updated to include `event_type`.
4. [x] `AttendanceRecordCreate` schema updated to accept optional `event_type`.
5. [ ] Alembic migration generated and applied.
6. [x] Column is indexed (queried frequently for "show me all IN events today").

## Notes

- Use a simple String column with constrained values rather than a DB-level enum (easier to extend later).
- Existing records ingested in Phase 1 will have `UNKNOWN` until re-processed or going forward.
- This is a prerequisite for Tasks 062 and 063.
