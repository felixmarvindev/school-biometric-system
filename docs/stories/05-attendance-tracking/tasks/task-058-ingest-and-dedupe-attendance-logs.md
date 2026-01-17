# Task 058: Ingest + Dedupe Attendance Logs (Device → DB)

## Story/Phase
- **Story**: Story 05: Attendance Tracking
- **Phase**: Phase 1: Event Capture

## Task Type
- [x] Backend
- [x] Database
- [ ] Frontend
- [ ] DevOps
- [ ] Documentation

## Description

Implement ingestion pipeline to store attendance logs fetched from devices into the database, with robust deduplication.

## Acceptance Criteria

1. [ ] Endpoint exists to trigger ingestion for one device (admin-only, school-scoped).
2. [ ] Ingestion stores new attendance records and skips duplicates.
3. [ ] Dedupe key is well-defined (e.g., `device_id + device_user_id + occurred_at + punch_type`).
4. [ ] Returns a summary: `{ inserted, skipped, total }`.
5. [ ] Does not commit partial state if response preparation fails (transaction-safe).

## Implementation Notes

- Prefer fetching logs in one call, then bulk insert new ones.
- Use unique constraint or application-level dedupe (unique constraint preferred).

## Files to Modify (Expected)

- Attendance service routes (or device_service route if that’s where ingestion will live initially)
- Attendance repository/service layer

