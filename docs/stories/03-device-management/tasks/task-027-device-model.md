# Task 027: Device Database Model

## Story/Phase
- **Story**: Story 03: Device Management
- **Phase**: Phase 1: Device Registration

## Description

Create the Device database model with all required fields, relationships, and database migration.

## Type
- [x] Backend
- [ ] Frontend
- [x] Database
- [ ] DevOps
- [ ] Documentation

## Acceptance Criteria

1. [ ] Device model exists with all required fields
2. [ ] Database migration creates `devices` table correctly
3. [ ] IP address and port combination has unique constraint per school
4. [ ] Serial number has unique constraint (global)
5. [ ] Model includes timestamps (created_at, updated_at)
6. [ ] Model includes soft delete support (is_deleted)
7. [ ] Foreign key to schools table
8. [ ] Foreign key to device_groups table (optional, nullable)
9. [ ] Status field with enum (online, offline, unknown)
10. [ ] Migration runs successfully without errors

## Technical Details

### Files to Create/Modify

```
backend/device_service/models/device.py
backend/shared/schemas/device.py
backend/alembic/versions/XXXX_create_devices_table.py
```

### Key Code Patterns

```python
# models/device.py
from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Boolean, DateTime, Text
from sqlalchemy.sql import func, text
from sqlalchemy.orm import relationship
from shared.database.base import Base
import enum

class DeviceStatus(str, enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    UNKNOWN = "unknown"

class Device(Base):
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    ip_address = Column(String(45), nullable=False)  # IPv4 or IPv6
    port = Column(Integer, nullable=False, default=4370)  # Default ZKTeco port
    serial_number = Column(String(100), unique=True, nullable=True, index=True)
    location = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    
    # Device status and monitoring
    status = Column(Enum(DeviceStatus), default=DeviceStatus.UNKNOWN, nullable=False)
    last_seen = Column(DateTime(timezone=True), nullable=True)
    last_sync = Column(DateTime(timezone=True), nullable=True)
    
    # Device capacity (for enrollment tracking)
    max_users = Column(Integer, nullable=True)  # Max capacity from device
    enrolled_users = Column(Integer, default=0, nullable=False)  # Current enrollment count
    
    # Group assignment (optional)
    device_group_id = Column(Integer, ForeignKey("device_groups.id"), nullable=True, index=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True)
    is_deleted = Column(Boolean, server_default=text("false"), nullable=False, index=True)
    
    # Relationships
    school = relationship("School", back_populates="devices")
    device_group = relationship("DeviceGroup", back_populates="devices")
    
    __table_args__ = (
        {"comment": "Biometric devices registered in schools"}
    )
```

### Database Constraints

- Unique constraint on `serial_number` (if provided) - serial numbers are globally unique
- Unique constraint on `(school_id, ip_address, port)` - same IP/port can't be registered twice per school
- Foreign key to `schools.id` (required)
- Foreign key to `device_groups.id` (optional, nullable)
- Index on `school_id`, `serial_number`, `device_group_id`, `status`, `is_deleted`

### Dependencies

- Task 001 (School model must exist)
- Alembic migrations configured
- Device groups model will be created in Phase 2 (optional relationship for now)

## Visual Testing

### Before State
- No devices table exists
- Cannot store device data

### After State
- Devices table exists
- Can create Device instances
- Relationships work correctly

### Testing Steps

1. Run migration - verify table created
2. Create test device - verify all fields work
3. Test relationships - verify foreign keys work
4. Test unique constraint - verify IP/port uniqueness per school
5. Test serial number uniqueness - verify global uniqueness
6. Test status enum - verify valid values

## Definition of Done

- [ ] Code written and follows standards
- [ ] Migration script created and tested
- [ ] Model relationships verified
- [ ] Unique constraints tested
- [ ] Foreign keys tested
- [ ] Comprehensive tests written and passing (10+ tests)
- [ ] Migration applied to test database

## Time Estimate

4-6 hours

## Notes

- IP address supports both IPv4 and IPv6 (max 45 chars)
- Default port is 4370 (standard ZKTeco port)
- Serial number is optional initially (can be updated after connection test)
- Status starts as "unknown" until first connection test
- Device groups relationship is nullable (Phase 2 feature)
- Max users and enrolled users tracking for capacity management

