# Task 078: Check Student on Device & Enforce Before Enrollment

## Story/Phase
- **Story**: Story 08: Student-Device Sync & Template Lifecycle
- **Phase**: Phase 2: Ensure Student on Device

## Description

When starting enrollment, the student must exist on the device. The **UI** checks when a device is selected and prompts the user to sync if the student is not on the device. The backend does **NOT** auto-sync; it returns a clear error if enrollment is attempted when the student is not on the device.

## Type
- [x] Backend
- [x] Frontend

## Prerequisites
- Task 077 complete (student sync to device)

## Acceptance Criteria

### Backend
1. [x] API: GET `/api/v1/sync/devices/{device_id}/students/{student_id}/status` - returns `{ synced: boolean }` (student user record exists on device)
2. [x] In `EnrollmentService.start_enrollment`, before CMD_STARTENROLL:
   - Check if student exists on device (student_on_device helper)
   - If NOT on device: raise error with code `STUDENT_NOT_ON_DEVICE` (do NOT auto-sync)
   - If on device: proceed with enrollment
3. [x] Clear error message for STUDENT_NOT_ON_DEVICE so frontend can show sync prompt (400 with detail.code)

### Frontend (Enrollment UI)
4. [ ] When user selects a device (and has selected a student), call check API
5. [ ] If student is NOT on device: show message "Student is not synced to this device" with [Sync Student] and [Choose Different Device] actions
6. [ ] [Sync Student] calls sync API; on success, refresh check and allow user to proceed
7. [ ] User must sync before "Start Capture" is allowed (or Start Capture fails and shows sync prompt)
8. [ ] No automatic sync - user explicitly confirms
