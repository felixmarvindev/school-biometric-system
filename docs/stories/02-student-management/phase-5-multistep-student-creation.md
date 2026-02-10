# Phase 5: Multi-step Student Creation

## Overview

Refactor student creation (and optionally update) into a multi-step wizard:

1. **Step 1: Personal Details** - first_name, last_name, date_of_birth, gender, parent_phone, parent_email
2. **Step 2: School Details** - admission_number, class_id, stream_id
3. **Step 3 (optional): Sync to Device** - Select device(s), sync student to device
4. **Step 4 (optional): Enroll** - Select finger, complete enrollment (ensures student on device first)

## Dependencies

- Story 08 Task 077 (student sync API)
- Story 08 Task 078 (ensure student on device before enrollment)
- Story 04 enrollment flow
