# Attendance Workflow

## Overview

Complete workflow for capturing and processing attendance events.

## Flow Diagram

```
┌─────────────────┐
│ Student taps    │
│ finger on device│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Device verifies │
│ fingerprint     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Device emits    │
│ EF_ATTLOG event │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Backend captures│
│ event           │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Match event to  │
│ student (via    │
│ enrollment)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Determine IN/OUT│
│ (entry/exit     │
│ logic)          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Store attendance│
│ record          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Emit WebSocket  │
│ event to        │
│ frontend        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Trigger SMS     │
│ notification    │
│ (Story 06)      │
└─────────────────┘
```

## Steps

1. **Event Capture**: Student uses device, event emitted
2. **Event Reception**: Backend receives EF_ATTLOG event
3. **Student Matching**: Match event to student via enrollment
4. **Entry/Exit Logic**: Determine IN or OUT
5. **Storage**: Store attendance record
6. **Real-time Update**: Emit WebSocket event
7. **Notification**: Trigger SMS notification (if enabled)

## Entry/Exit Logic

1. **No Previous Record**: First event of day → IN
2. **Last was IN**: Last event > 30 mins ago → OUT
3. **Last was OUT**: Next event → IN
4. **Duplicate**: Last event < 30 mins ago → Ignore

## WebSocket Events

- `attendance_event`: New attendance event (student, time, device, type)

