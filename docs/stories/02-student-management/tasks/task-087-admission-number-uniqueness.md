# Task 087: Admission Number Uniqueness

## Story/Phase
- **Story**: Story 02: Student Management
- **Phase**: Phase 5: Multi-step Student Creation

## Description

Ensure admission_number is unique per school across the system. Backend constraint exists; validate in UI and return clear errors.

## Type
- [x] Backend
- [x] Frontend
- [ ] Database

## Prerequisites
- Students table has UniqueConstraint(school_id, admission_number)
- Student create/update API

## Acceptance Criteria

### Backend
1. [ ] Create/update API returns 400 or 409 when admission_number duplicates within same school
2. [ ] Error response includes code (e.g. `ADMISSION_NUMBER_EXISTS`) and clear message
3. [ ] On edit: exclude current student when checking uniqueness (allow keeping same admission_number)

### Frontend
4. [ ] Show validation error when API returns duplicate admission_number
5. [ ] Message: "Admission number already exists for this school"
6. [ ] Optional: Debounced client-side check before submit (GET or validation endpoint)
7. [ ] Works in both add and edit student wizards
