# Task 056: Fetch Attendance Logs from Device (ZKTeco)

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

Implement real device attendance log fetching using the ZKTeco integration (pyzk wrapper). This task focuses on retrieving raw attendance logs from the device (not yet storing them).

## Acceptance Criteria

1. [x] A service method exists to fetch attendance logs from a device using the ZKTeco connection wrapper.
2. [x] Fetching logs is **async-safe** (wrap pyzk sync calls with `asyncio.to_thread`).
3. [x] Handles offline/auth errors gracefully (returns a clear error / empty result without crashing worker).
4. [ ] Works with real device during testing (at least one successful fetch).

## Implementation Notes

- Use the existing ZKTeco wrapper in `backend/device_service/zk/base.py` and extend it with a method like `get_attendance_logs()` if needed.
- Prefer returning a normalized dict structure per record:
  - `uid` / `user_id`
  - `timestamp`
  - `status` / `punch_type` (if available)
  - `device_serial` (if available)

## Files to Modify (Expected)

- `backend/device_service/zk/base.py`
- `backend/device_service/services/device_info_service.py` (optional helper) or new `device_service/services/attendance_log_service.py`

