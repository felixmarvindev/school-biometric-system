# Task 076: Persist Enrollment to Database and Templates (Syncing & UI Readiness)

## Story/Phase
- **Story**: Story 04: Automated Enrollment
- **Phase**: Phase 4: Template Storage (extended)

## Description

Persist completed enrollments and fingerprint templates to the database so that:
1. Enrollment history and student–device–finger mappings are durable for UI (e.g. "enrolled fingers" lists, enrollment history).
2. Templates are stored (encrypted) in readiness for syncing to other devices later.
3. A single source of truth supports both UI display and future cross-device sync.

## Type
- [x] Backend
- [ ] Frontend
- [x] Database
- [ ] DevOps
- [ ] Documentation

## Duration Estimate
2–3 days

## Prerequisites

- ✅ Task 073 complete (enrollment success flow)
- ✅ Enrollment session model and completion flow exist
- ✅ Task 072 partially complete (template_data, quality_score on session)

## Acceptance Criteria

1. [x] Completed enrollment sessions are the source of truth for "enrolled" state (already in place; verify/use consistently).
2. [x] Optional: Student–device–finger enrollment record table (or equivalent) for quick "is this student enrolled on this device?" and "which fingers?" queries for UI and sync. (Using enrollment_sessions with status=completed; get_enrolled_fingers falls back to DB when device offline.)
3. [x] Template capture from device on enrollment success (when device supports it).
4. [x] Template encrypted before storage (backend/device_service/core/encryption.py).
5. [x] Template stored in enrollment session (template_data).
6. [x] API or service method to list enrollments per student and per device for UI.
7. [x] Data model and APIs ready for future "sync templates to other devices" (no sync implementation required in this task).

## Implementation Details

### Backend Changes

1. **Enrollment persistence (verify/extend)**
   - Ensure `EnrollmentSession` status, `completed_at`, `quality_score` are set on completion (already done in `complete_enrollment()`).
   - Option A: Add `student_device_enrollments` (or similar) table: student_id, device_id, finger_id, enrollment_session_id, template_id (FK to templates if separate table), synced_at (nullable), created_at.
   - Option B: Use enrollment_sessions with status=completed as the enrollment record; add indexes/query helpers for "by student", "by device".

2. **Template capture and storage**
   - **backend/device_service/zk/** or device connection layer: add or use `get_template(user_id, finger_id)` to read template from device after enrollment (if supported by device/SDK).
   - **backend/device_service/core/encryption.py** (or shared): encrypt template before save; decrypt only when pushing to another device (future task).
   - Store encrypted template in `EnrollmentSession.template_data` and/or in a `fingerprint_templates` table (id, enrollment_session_id, student_id, device_id, finger_id, encrypted_data, quality_score, created_at).

3. **Queries for UI and future sync**
   - Service/repository methods: e.g. `get_enrollments_by_student(school_id, student_id)`, `get_enrollments_by_device(school_id, device_id)`, `get_enrolled_fingers_for_student_on_device(device_id, student_id)` (can call device when online or read from DB when offline).
   - Optional: GET `/api/v1/enrollment/students/{student_id}/enrollments` and GET `/api/v1/enrollment/devices/{device_id}/enrollments` for UI and sync readiness.

### Database

- If new table: migration for `student_device_enrollments` and/or `fingerprint_templates` with indexes on (student_id, device_id), (device_id, finger_id), school_id.
- Ensure enrollment_sessions has index on (student_id, device_id, status) for listing completed enrollments.

### Key Code Patterns

```python
# Example: after enrollment completion in enrollment_service
async def complete_enrollment(self, enrollment_id: int, template_data: Optional[bytes] = None, ...):
    # If template_data from device available:
    #   encrypted = encrypt_template(template_data)
    #   update session with template_data=encrypted
    # Create or update student_device_enrollment record for quick lookups
    ...
```

## Testing

### Manual Testing

1. Complete an enrollment and verify session has status=completed, completed_at, quality_score.
2. If template capture implemented: verify template stored (encrypted) and retrievable for future sync.
3. Call enrollment list APIs and verify results for UI.

## Definition of Done

- [x] Enrollment completion persists all relevant fields to database.
- [x] Template capture and encrypted storage implemented (or clearly scoped for follow-up).
- [x] Query methods/APIs for enrollments by student and by device available for UI.
- [x] Data model and storage ready for future sync-to-other-devices work.

## Next Task

**Task 074: Bulk Enrollment API** – Bulk enrollment can use this persistence layer. Task 072 (template capture from device) can be completed in parallel or before this task.
