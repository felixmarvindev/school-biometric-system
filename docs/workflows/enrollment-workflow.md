# Enrollment Workflow

## Overview

Complete workflow for enrolling a student's fingerprint on a biometric device.

## Flow Diagram

```
┌─────────────────┐
│ Admin selects   │
│ Student, Device,│
│ Finger          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ POST /enroll    │
│ Start Session   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Connect to      │
│ Device          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Send CMD_       │
│ STARTENROLL     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Device enters   │
│ Enrollment Mode │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Emit Progress   │
│ 0% (Ready)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Student places  │
│ finger on sensor│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Emit Progress   │
│ 33% (Placing)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Emit Progress   │
│ 66% (Capturing) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Capture Template│
│ Emit 100%       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Store Template  │
│ (Encrypted)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Create          │
│ Enrollment Record│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Emit Success    │
│ Event           │
└─────────────────┘
```

## Steps

1. **Initiation**: Admin selects student, device, and finger
2. **Session Creation**: Backend creates enrollment session
3. **Device Connection**: Connect to selected device
4. **Enrollment Command**: Send CMD_STARTENROLL to device
5. **Progress Updates**: Emit progress via WebSocket (0%, 33%, 66%, 100%)
6. **Template Capture**: Device captures fingerprint template
7. **Storage**: Store encrypted template in database
8. **Record Creation**: Create enrollment record
9. **Completion**: Emit success event to frontend

## Error Handling

- **Device Offline**: Show error, allow retry
- **Connection Timeout**: Show timeout error, allow retry
- **Poor Quality**: Show quality error, allow retry
- **Device Busy**: Show busy error, suggest retry later
- **Network Error**: Show network error, allow retry

## WebSocket Events

- `enrollment_progress`: Progress updates (0%, 33%, 66%, 100%)
- `enrollment_complete`: Enrollment successful
- `enrollment_error`: Enrollment failed with error details

