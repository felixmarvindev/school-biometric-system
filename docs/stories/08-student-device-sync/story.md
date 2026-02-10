# Story 08: Student-Device Sync & Template Lifecycle

## User Story

**As a** school administrator,  
**I want to** sync student details to devices and manage fingerprint templates independently,  
**So that** students can be enrolled reliably, templates can be transferred if a device is lost, and student data is consistent across devices.

## Business Value

- **Device resilience**: If an enrollment device is lost, templates are stored centrally and can be pushed to a replacement device
- **Reliable enrollment**: Enrollment always works because students are synced to the device before capture
- **Template transfer**: Sync a student (including fingerprints) to additional devices without re-enrollment
- **Single source of truth**: Fingerprint templates live in a dedicated table, not only in enrollment history

## Phases

### Phase 1: Student Sync to Device
- Add `set_user` (CMD_USER_WRQ) to ZKDeviceConnection
- Create sync service: sync student details to device
- API: POST `/api/v1/sync/students/{student_id}/devices/{device_id}`

### Phase 2: Ensure Student on Device Before Enrollment
- Before CMD_STARTENROLL, check if student exists on device
- If not, sync student (set_user) first, then start enrollment
- Enrollment flow becomes reliable regardless of prior sync

### Phase 3: Fingerprint Templates Table
- New table: `fingerprint_templates` (student_id, device_id, finger_id, encrypted_data, quality_score, source_enrollment_id, created_at)
- On enrollment completion: insert into fingerprint_templates and optionally keep copy in enrollment_sessions
- Templates table is the canonical store for transfer

### Phase 4: Template Transfer to Device
- Add `set_user_template` (CMD_USERTEMP_WRQ) to ZKDeviceConnection
- API: POST `/api/v1/sync/students/{student_id}/devices/{device_id}/templates` - push templates from DB to device
- Use case: device lost, new device added, sync student + templates

## Prerequisites

- Story 02 (Student Management)
- Story 03 (Device Management)
- Story 04 (Automated Enrollment) - Task 076 complete
