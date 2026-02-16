# Task 063: Integrate Entry/Exit Logic into Ingestion Pipeline

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

Wire the student matching (Task 061) and entry/exit determination (Task 062) into the existing attendance ingestion pipeline (Task 058). After this task, every newly ingested attendance record will automatically have:
- `student_id` populated (when a match is found)
- `event_type` set to IN, OUT, or UNKNOWN

## Acceptance Criteria

1. [x] `AttendanceIngestionService.ingest_for_device()` calls `StudentMatchingService` to resolve student IDs for all records in the batch.
2. [x] For each matched record, calls `EntryExitService.determine_from_previous()` to set `event_type`.
3. [x] Unmatched records are still inserted with `student_id=NULL` and `event_type=UNKNOWN`.
4. [x] Duplicate taps (within the configured window) are skipped (not inserted).
5. [x] `IngestionSummaryResponse` updated to include `duplicates_filtered` count.
6. [x] End-to-end flow works: device poll → fetch logs → match students → determine IN/OUT → store.
7. [x] Transaction safety maintained (rollback on any failure).

## Notes

- Process records in chronological order (`occurred_at` ascending) so the entry/exit logic sees the correct "previous" record.
- Student matching should be batched (one query per device, not per record).
- Entry/exit determination is per-record (sequential, since each depends on the previous).
- Keep the ingestion idempotent — re-running should not create duplicates or change existing event types.
