# Notification Workflow

## Overview

Complete workflow for sending SMS notifications to parents.

## Flow Diagram

```
┌─────────────────┐
│ Attendance event│
│ occurs          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Check if        │
│ notifications   │
│ enabled         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Fetch parent    │
│ phone number    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Generate SMS    │
│ message         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Send via        │
│ Africa's Talking│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Store           │
│ notification    │
│ record          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Track delivery  │
│ status          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ If failed, add  │
│ to retry queue  │
└─────────────────┘
```

## Steps

1. **Event Trigger**: Attendance event occurs
2. **Check Settings**: Verify notifications enabled for student/school
3. **Fetch Contact**: Get parent phone number
4. **Generate Message**: Create SMS message with template
5. **Send SMS**: Send via Africa's Talking API
6. **Store Record**: Create notification record
7. **Track Status**: Monitor delivery status
8. **Retry if Failed**: Queue for retry if delivery fails

## Message Templates

**Check-in**:
```
[Student Name] signed IN at [Time] via [Device Name].
```

**Check-out**:
```
[Student Name] signed OUT at [Time] via [Device Name].
```

## Retry Logic

- Failed notifications retried up to 3 times
- Retry intervals: 5 min, 15 min, 1 hour
- After 3 failures, mark as permanently failed

