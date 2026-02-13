# Task 086: Multi-step Edit Student Wizard

## Story/Phase
- **Story**: Story 02: Student Management
- **Phase**: Phase 5: Multi-step Student Creation

## Description

Refactor edit-student UI to match the add-student wizard flow. Same intuitive steps: Personal info, Class assignment, optional Sync to devices, optional Fingerprint enrollment. Each step saves on "Next".

## Type
- [ ] Backend
- [x] Frontend

## Prerequisites
- Task 085 (multi-step add student wizard)
- Student update API
- Task 077 (sync API)
- Task 078 (enrollment flow)

## Acceptance Criteria

### Step 1: Personal Info
1. [x] Pre-filled with existing student data
2. [x] "Next" saves personal info (PATCH student)

### Step 2: Class Assignment
3. [x] Pre-filled admission_number (read-only), class_id, stream_id
4. [x] **Admission number**: Read-only on edit (immutable)
5. [x] "Next" saves class assignment (PATCH class/stream)

### Step 3: Sync to Device (Optional)
6. [x] Student can be synced to multiple devices
7. [x] Multi-select devices, sync each
8. [x] Add sync to additional devices
9. [x] "Next" or "Skip"

### Step 4: Fingerprint Enrollment (Optional)
10. [x] Optional enrollment step (same as add wizard)
11. [x] "Finish" or "Skip"

### General
12. [x] Route: `/dashboard/students/[id]/edit` uses wizard
13. [x] Same step indicator and UX as add wizard
14. [x] Back button revisits previous steps (data persisted)
