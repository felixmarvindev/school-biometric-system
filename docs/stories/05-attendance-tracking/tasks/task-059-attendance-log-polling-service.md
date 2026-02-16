# Task 059: Attendance Log Polling Service (Periodic)

## Story/Phase
- **Story**: Story 05: Attendance Tracking
- **Phase**: Phase 1: Event Capture

## Task Type
- [x] Backend
- [ ] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Description

Add a periodic background service that polls online devices for new attendance logs and ingests them automatically (hands-free attendance capture).

## Acceptance Criteria

1. [x] Background poller runs on an interval (configurable, e.g. every 1–5 minutes).
2. [x] Polls only online devices (or uses connection test before polling).
3. [x] Uses the ingestion pipeline from Task 058.
4. [ ] Emits optional WebSocket events for new attendance records (can be a follow-up).
5. [x] Graceful shutdown (stops task on app shutdown).

## Notes

- Similar pattern to `DeviceHealthCheckService` / `DeviceInfoSyncService`.
- Ensure device connections are not exhausted (use pooling / bounded concurrency).

