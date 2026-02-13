# Task 085: Multi-step Add Student Wizard (Refined)

## Story/Phase
- **Story**: Story 02: Student Management
- **Phase**: Phase 5: Multi-step Student Creation

## Description

Refactor add-student UI into an intuitive multi-step wizard. Each step saves on "Next". Personal info first, then class assignment, then optional sync to device(s), then optional fingerprint enrollment.

## Type
- [ ] Backend
- [x] Frontend
- [ ] Database

## Prerequisites
- Task 077 (student sync API)
- Task 078 (ensure student on device before enrollment)
- Existing student create API

## Acceptance Criteria

### Step 1: Personal Info
1. [x] Fields: first_name, last_name, date_of_birth, gender, parent_phone, parent_email
2. [x] "Next" validates and advances (edit: PATCH; add: advance to step 2)
3. [x] Validation before allowing Next

### Step 2: Class Assignment
4. [x] Fields: admission_number (unique), class_id, stream_id
5. [x] "Next" saves (add: creates student; edit: PATCH class/stream)
6. [x] **Admission number**: Must be unique per school; show validation error if duplicate
7. [x] Backend validates admission_number uniqueness; UI shows clear error on conflict

### Step 3: Sync to Device (Optional)
8. [x] User can skip this step
9. [x] Multi-device sync: Student can be synced to **multiple devices**
10. [x] Device selector (online devices only) with multi-select
11. [x] Call sync API for each selected device
12. [x] Show success/error per device (toast)
13. [x] "Next" or "Skip" to proceed

### Step 4: Fingerprint Enrollment (Optional)
14. [x] User can skip this step
15. [x] Select device, select finger, start enrollment
16. [x] Reuse EnrollmentCapture flow
17. [x] "Finish" or "Skip" to complete

### General
18. [x] Route: `/dashboard/students/new` uses wizard
19. [x] Step indicator (match EnrollmentWizard pattern)
20. [x] Back button allows revisiting previous steps
21. [x] Intuitive flow: each Next commits progress

## Implementation Notes

- Create student after Step 1 (minimal) or after Step 2 (full) depending on API design
- Admission number uniqueness: API returns 409 or 400 with code; UI shows "Admission number already exists for this school"
- Sync step: Allow selecting multiple devices; sync each via POST `/api/v1/sync/students/{id}/devices/{device_id}`
