# Task 077: Student Sync to Device (Backend API)

## Story/Phase
- **Story**: Story 08: Student-Device Sync & Template Lifecycle
- **Phase**: Phase 1: Student Sync to Device

## Description

Add ability to sync student details to a ZKTeco device using CMD_USER_WRQ (set_user). This ensures the student record exists on the device before enrollment.

## Type
- [x] Backend
- [ ] Frontend
- [ ] Database
- [ ] DevOps

## Prerequisites
- Task 076 complete
- pyzk `set_user` available

## Acceptance Criteria

1. [x] `ZKDeviceConnection.set_user(uid, name, user_id, privilege)` added
2. [x] Wraps pyzk `conn.set_user(uid=..., name=..., user_id=..., privilege=0)` with asyncio.to_thread
3. [x] Sync service: `sync_student_to_device(student_id, device_id, school_id)`
4. [x] Service fetches student from shared DB, calls set_user with student details
5. [x] API: POST `/api/v1/sync/students/{student_id}/devices/{device_id}`
6. [x] Returns success/failure with clear error messages
7. [x] Device must be online

## Implementation Notes

- pyzk `set_user(uid, name, privilege, password, group_id, user_id, card)` - use user_id=str(student_id), name=full name
- Student data: first_name, last_name, admission_number from Student model
- Device must exist and be online; use DeviceConnectionService
