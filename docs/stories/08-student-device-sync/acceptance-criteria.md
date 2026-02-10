# Story 08: Acceptance Criteria

## Phase 1: Student Sync to Device
- [ ] API to sync student to device
- [ ] Student details (name, user_id) appear on device
- [ ] Device must be online

## Phase 2: Ensure Student on Device Before Enrollment
- [ ] Enrollment always syncs student first if not on device
- [ ] No "user not found" errors during enrollment when device is online

## Phase 3: Fingerprint Templates Table
- [ ] Dedicated fingerprint_templates table
- [ ] Templates stored on enrollment completion
- [ ] Templates independent of enrollment_sessions for transfer

## Phase 4: Template Transfer
- [ ] API to push templates from DB to device
- [ ] Use case: device lost, transfer to new device
- [ ] Student synced + templates pushed
