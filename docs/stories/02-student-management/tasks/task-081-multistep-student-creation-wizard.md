# Task 081: Multi-step Student Creation Wizard (Frontend)

> **Note:** Superseded/refined by Task 085 (Multi-step Add Student Wizard) which specifies step-by-step saves, multi-device sync, and admission number uniqueness. Task 081 can be considered completed when 085 is done.

## Story/Phase
- **Story**: Story 02: Student Management
- **Phase**: Phase 5: Multi-step Student Creation

## Description

Refactor student creation into a multi-step wizard. Personal details first, then school details, then optional sync and enroll.

## Type
- [ ] Backend
- [x] Frontend
- [ ] Database

## Prerequisites
- Task 021 (StudentForm) complete
- Task 077 (student sync API) - for sync step

## Acceptance Criteria

1. [ ] New `StudentCreationWizard` component with steps:
   - Step 1: Personal Details (first_name, last_name, date_of_birth, gender, parent_phone, parent_email)
   - Step 2: School Details (admission_number, class_id, stream_id)
   - Step 3 (optional): Sync to Device - select device(s), call sync API after student created
   - Step 4 (optional): Enroll - select device (from step 3 or new), finger, start enrollment
2. [ ] Student is created after Step 2 (or saved as draft and committed at end)
3. [ ] Step 3 and 4 are optional - user can skip and go to student list
4. [ ] Reuse EnrollmentWizard/EnrollmentCapture for Step 4 or integrate enrollment flow
5. [ ] Route: `/dashboard/students/new` uses wizard instead of single form

## Implementation Notes

- Can create student at end of Step 2, then offer "Sync to device" and "Enroll" as post-creation actions
- Or create student only when user completes Step 2 and clicks "Create" - then show optional Step 3/4
- Match EnrollmentWizard step-indicator pattern for consistency
