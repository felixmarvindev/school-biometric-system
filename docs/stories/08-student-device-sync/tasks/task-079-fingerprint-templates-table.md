# Task 079: Fingerprint Templates Table

## Story/Phase
- **Story**: Story 08: Student-Device Sync & Template Lifecycle
- **Phase**: Phase 3: Fingerprint Templates Table

## Description

Create a dedicated `fingerprint_templates` table to store templates independently of enrollment sessions. This enables template transfer when a device is lost and provides a canonical store.

## Type
- [x] Backend
- [ ] Frontend
- [x] Database

## Prerequisites
- Task 076 complete (encryption, template capture)

## Acceptance Criteria

1. [x] New model `FingerprintTemplate`:
   - student_id, device_id (source device), finger_id
   - encrypted_data (Text), quality_score (int)
   - source_enrollment_session_id (FK, nullable) - links to enrollment that produced it
   - school_id, created_at
   - Indexes: (student_id, finger_id), (school_id)
2. [x] Migration created and applied
3. [x] On enrollment completion: insert into fingerprint_templates (in addition to or instead of enrollment_sessions.template_data)
4. [x] Repository: create, get_by_student, get_by_student_and_finger
5. [x] Enrollment completion flow updated to write to fingerprint_templates
