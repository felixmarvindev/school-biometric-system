# Task 080: Template Transfer to Device

## Story/Phase
- **Story**: Story 08: Student-Device Sync & Template Lifecycle
- **Phase**: Phase 4: Template Transfer

## Description

Push stored fingerprint templates from the database to a target device using CMD_USERTEMP_WRQ. Enables recovering from device loss by transferring templates to a new device.

## Type
- [x] Backend
- [ ] Frontend

## Prerequisites
- Task 079 complete (fingerprint_templates table)
- pyzk supports set_user_template / CMD_USERTEMP_WRQ

## Acceptance Criteria

1. [ ] `ZKDeviceConnection.set_user_template(user_id, finger_id, template_bytes)` - wraps pyzk set_user_template with asyncio
2. [ ] Service: `transfer_templates_to_device(student_id, target_device_id, school_id)`:
   - Sync student to device (set_user) if not present
   - Load templates from fingerprint_templates for student
   - Decrypt each template
   - Push each to device (set_user_template)
3. [ ] API: POST `/api/v1/sync/students/{student_id}/devices/{device_id}/transfer-templates`
4. [ ] Returns success with count of templates transferred
5. [ ] Handles device offline, template missing, decryption errors
