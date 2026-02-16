# Task 061: Student Matching Service

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

Create a service that resolves `device_user_id` (the UID stored on the biometric device) to a `student_id` in our system. During ingestion, attendance records arrive with only a `device_user_id`; we need to look up which student that UID belongs to using the device-student sync/enrollment mapping.

## Acceptance Criteria

1. [x] `StudentMatchingService` created with `resolve_batch(school_id, device_user_ids)` and `resolve_single()` methods.
2. [x] Uses direct mapping: `device_user_id == str(student_id)` (set during device sync), validated against students table.
3. [x] Returns `None` when no student match is found (record stays with `student_id=NULL`).
4. [x] Handles edge cases: deleted students filtered out, non-numeric UIDs skipped gracefully.
5. [x] Integrated into the ingestion pipeline — newly ingested records get `student_id` populated when a match exists.
6. [x] Efficient: uses a single batch query for all records in an ingestion cycle (not N+1).

## Notes

- Check how students are synced to devices (likely a mapping table or the device user records).
- Cache mappings per device during a single ingestion cycle for efficiency.
- Records that can't be matched should still be saved (with `student_id=NULL`) for later reconciliation.
