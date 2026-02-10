# Analysis: Student Sync, Multi-step Creation & Template Lifecycle

## Overview

This document analyzes gaps between the desired flow and current implementation for:
1. Syncing students to devices (student details on device)
2. Multi-step student creation (personal → school → optional sync → optional enroll)
3. Ensuring student is on device before enrollment
4. Template transfer to another device
5. Separate fingerprint_templates table (device-loss resilience)

---

## Current State

### Backend

| Area | Status | Details |
|------|--------|---------|
| **Student sync to device** | ❌ Not implemented | No `set_user` (CMD_USER_WRQ) in ZKDeviceConnection. `test_enrollment_direct.py` has `ensure_user` using pyzk's `set_user`, but EnrollmentService does not call it. |
| **Enrollment flow** | ⚠️ Incomplete | `start_enrollment` sends CMD_STARTENROLL directly. It assumes student user exists on device (pyzk `enroll_user` resolves by get_users). If student is not on device, enrollment will fail (e.g. error 2001). |
| **Template storage** | ⚠️ Partial | Templates in `enrollment_sessions.template_data` only. No separate `fingerprint_templates` table. If device is lost, templates exist in DB but are tied to enrollment sessions. |
| **Template transfer** | ❌ Not implemented | No CMD_USERTEMP_WRQ (write template to device). Cannot push stored template to a new device. |
| **Device info sync** | ✅ Implemented | `DeviceInfoSyncService` syncs time, capacity, etc. Does NOT sync students. |

### Frontend

| Area | Status | Details |
|------|--------|---------|
| **Student form** | Single form | `StudentForm.tsx` has sections (Personal, Academic, Parent) but is one step. All fields submitted together. |
| **Sync step** | ❌ Not implemented | No "Sync to device" step during student creation. |
| **Enroll step** | ❌ Not integrated | Enrollment is separate page (`/dashboard/enrollment`). Not offered as optional step after student creation. |
| **Enrollment wizard** | ✅ Implemented | Select student → device → finger → capture. Does not ensure student is synced to device first. |

### Workflow doc

`docs/workflows/sync-workflow.md` describes the intended flow (Upload student CMD_USER_WRQ → Upload templates CMD_USERTEMP_WRQ) but this is **not implemented**.

---

## Desired Flow

### 1. Multi-step Student Creation

```
Step 1: Personal Details
  - first_name, last_name, date_of_birth, gender
  - parent_phone, parent_email

Step 2: School Details
  - admission_number, class_id, stream_id

Step 3 (optional): Sync to Device
  - Select device(s)
  - Upload student to device (set_user)
  - Student record exists on device (no fingerprint yet)

Step 4 (optional): Enroll
  - If coming from creation: device already selected from step 3
  - Select finger, start capture
  - Ensures student is on device (sync if needed) before enrollment
```

### 2. Enrollment Flow (from any entry point)

```
When user selects device (Enrollment UI):
  1. Check if student exists on device (API: GET sync status)
  2. If NOT on device: show "Student is not synced to this device. Would you like to sync now?"
  3. User clicks [Sync Student] → call sync API → on success, allow proceeding
  4. No automatic sync - user must confirm

Before CMD_STARTENROLL (backend):
  1. Verify student exists on device; if not, return STUDENT_NOT_ON_DEVICE error
  2. Do NOT auto-sync from backend - frontend handles sync with user consent
```

### 3. Template Lifecycle

```
On enrollment completion:
  1. Capture template from device (get_user_template)
  2. Encrypt and store in fingerprint_templates table (canonical)
  3. Also link to enrollment_sessions for history
  4. Template can be transferred to another device later
```

### 4. Template Transfer (Device Loss / New Device)

```
Admin action: "Transfer student to new device"
  1. Load templates from fingerprint_templates (not device)
  2. Sync student to target device (set_user)
  3. Push templates to device (CMD_USERTEMP_WRQ)
  4. Record sync in DB
```

---

## Gaps Summary

| # | Gap | Priority | Story/Task |
|---|-----|----------|------------|
| 1 | Student sync (set_user) not in ZKDeviceConnection | High | Story 08 |
| 2 | Enrollment does not ensure student on device | High | Story 08 |
| 3 | Multi-step student creation wizard | High | Story 02 extension |
| 4 | Optional sync step in student creation | Medium | Story 02 extension |
| 5 | Optional enroll step in student creation | Medium | Story 02 extension |
| 6 | Separate fingerprint_templates table | High | Story 08 |
| 7 | Template transfer (push to device) | High | Story 08 |

---

## Dependencies

- **Story 02 (Student)**: Student CRUD, classes, streams
- **Story 03 (Device)**: Device registration, connection
- **Story 04 (Enrollment)**: Enrollment flow, template capture, WebSocket progress
- **Task 076**: Persistence, encryption, list APIs

---

## Related Files

### Backend
- `device_service/zk/base.py` - No set_user, no set_user_template
- `device_service/services/enrollment_service.py` - No sync before enrollment
- `device_service/services/device_info_sync.py` - Device info only, not students
- `device_service/models/enrollment.py` - template_data on session only
- `school_service/api/routes/students.py` - Single create/update

### Frontend
- `components/features/students/StudentForm.tsx` - Single form
- `app/(dashboard)/dashboard/students/new/page.tsx` - Uses StudentForm
- `components/features/enrollment/EnrollmentWizard.tsx` - No sync check
