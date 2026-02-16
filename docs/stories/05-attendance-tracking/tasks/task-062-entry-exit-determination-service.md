# Task 062: Entry/Exit Determination Service

## Story/Phase
- **Story**: Story 05: Attendance Tracking
- **Phase**: Phase 2: Entry/Exit Logic

## Task Type
- [x] Backend
- [ ] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Description

Implement the core logic that determines whether an attendance tap is an IN (entry) or OUT (exit) event. This is based on the student's previous attendance record for the same school/day.

### Rules

| Scenario | Previous Record | Time Gap | Result |
|---|---|---|---|
| First tap of the day | None | — | **IN** |
| After an IN | IN | > configurable window (default 30 min) | **OUT** |
| After an OUT | OUT | > configurable window | **IN** |
| Rapid re-tap | Any | < configurable window | **DUPLICATE** (skip) |
| Unmatched student | — | — | **UNKNOWN** (no student_id to query history) |

## Acceptance Criteria

1. [x] `EntryExitService` created with `determine()`, `determine_from_previous()`, and `get_last_records_for_students()` methods.
2. [x] Queries the last non-deleted attendance record for the student on the same calendar day.
3. [x] Applies rules: first tap → IN, after IN → OUT, after OUT → IN.
4. [x] Configurable duplicate window (default 30 minutes) — taps within the window are marked as DUPLICATE and skipped.
5. [x] Handles unmatched students gracefully (student_id is None → event_type = UNKNOWN).
6. [x] Configurable settings via `config.py` (`ATTENDANCE_DUPLICATE_WINDOW_MINUTES`).
7. [x] Day boundary uses the school's timezone (configurable via `ATTENDANCE_TIMEZONE`, default Africa/Nairobi).

## Notes

- The determination happens during ingestion (Task 063 will wire it in).
- "Same day" should be based on local timezone, not UTC.
- Records sorted by `occurred_at` descending to get the latest.
- This service is stateless — it reads from DB and returns a determination.
