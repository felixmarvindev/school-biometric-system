# Phase 5: Multi-step Student Creation

## Overview

Refactor student creation and edit into an intuitive multi-step wizard. **Each Next saves** progress.

1. **Step 1: Personal Info** - first_name, last_name, date_of_birth, gender, parent_phone, parent_email → Next saves
2. **Step 2: Class Assignment** - admission_number (unique), class_id, stream_id → Next saves
3. **Step 3 (optional): Sync to Device** - Student can be synced to **multiple devices**; multi-select
4. **Step 4 (optional): Fingerprint Enrollment** - Select device, finger, complete enrollment

## Key Requirements

- **Admission number**: Unique per school (Task 087)
- **Multi-device sync**: Student can be synced to many devices in one flow
- **Step-by-step saves**: Each Next commits; Back allows revisiting previous steps

## Tasks

- **Task 085**: Multi-step Add Student Wizard
- **Task 086**: Multi-step Edit Student Wizard
- **Task 087**: Admission Number Uniqueness (backend + frontend)

## Dependencies

- Story 08 Task 077 (student sync API)
- Story 08 Task 078 (ensure student on device before enrollment)
- Story 04 enrollment flow
