# Task 084: Enrollment - Device Check & Sync Prompt (UI)

## Story/Phase
- **Story**: Story 08: Student-Device Sync & Template Lifecycle
- **Phase**: Phase 2: Ensure Student on Device

## Description

When selecting a device in the Enrollment wizard, check if the student is synced to that device. If not, show a message and ask the user if they want to sync. Do NOT sync automatically - user must confirm.

## Type
- [ ] Backend
- [x] Frontend

## Prerequisites
- Task 077 (student sync API)
- Task 078 backend parts (check API, STUDENT_NOT_ON_DEVICE error)

## Acceptance Criteria

1. [ ] When user selects a device in Step 2 (Choose Device) and a student is already selected:
   - Call GET `/api/v1/sync/devices/{device_id}/students/{student_id}/status` (or equivalent)
   - If `synced: false`: show inline message/banner
2. [ ] Message: "Student is not synced to this device. Would you like to sync now?"
3. [ ] Actions: [Sync Student] button, optionally [Choose Different Device] or [Dismiss]
4. [ ] [Sync Student] calls sync API; on success, show "Student synced successfully" and hide the message
5. [ ] User cannot proceed to finger selection (or Start Capture) until student is synced OR user chooses a different device
6. [ ] No automatic sync - user explicitly clicks [Sync Student]
7. [ ] If sync fails, show error and allow retry or device change

## Implementation Notes

- Can be implemented in EnrollmentWizard (when selectedDevice + selectedStudent both set) or in DeviceSelector with student prop
- Show Alert or inline card below device list when not synced
- "Start Capture" / Next button disabled until synced, or show sync prompt when they try to proceed
