# Device Synchronization Workflow

## Overview

Workflow for synchronizing student data between system and devices.

## Flow Diagram

```
┌─────────────────┐
│ Admin initiates │
│ sync (student or│
│ bulk)           │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Select target   │
│ devices         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Connect to each │
│ device          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Upload student  │
│ data (CMD_USER_ │
│ WRQ)            │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Upload          │
│ fingerprint     │
│ templates       │
│ (CMD_USERTEMP_  │
│ WRQ)            │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Refresh device  │
│ data            │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Update sync     │
│ status          │
└─────────────────┘
```

## Steps

1. **Initiation**: Admin starts sync operation
2. **Device Selection**: Select target devices
3. **Connection**: Connect to each device
4. **Data Upload**: Upload student information
5. **Template Upload**: Upload fingerprint templates
6. **Device Refresh**: Refresh device data
7. **Status Update**: Update sync status

## Sync Types

- **Student Sync**: Sync single student to device(s)
- **Bulk Sync**: Sync multiple students
- **Class Sync**: Sync entire class to device(s)
- **Full Sync**: Sync all students to device(s)

