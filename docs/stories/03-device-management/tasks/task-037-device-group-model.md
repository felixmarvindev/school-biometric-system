# Task 037: Device Group Database Model

## Story/Phase
- **Story**: Story 03: Device Management
- **Phase**: Phase 2: Device Groups

## Description

Create the DeviceGroup database model to organize devices into logical groups (e.g., by location or purpose).

## Type
- [x] Backend
- [ ] Frontend
- [x] Database
- [ ] DevOps
- [ ] Documentation

## Acceptance Criteria

1. [x] DeviceGroup model exists with all required fields
2. [x] Database migration creates `device_groups` table correctly
3. [x] Group name has unique constraint per school
4. [x] Model includes timestamps (created_at, updated_at)
5. [x] Model includes soft delete support (is_deleted)
6. [x] Foreign key to schools table
7. [x] Relationship with devices table (one-to-many)
8. [x] Migration runs successfully without errors

## Technical Details

### Files to Create/Modify

```
backend/device_service/models/device_group.py
backend/shared/schemas/device_group.py
backend/alembic/versions/XXXX_create_device_groups_table.py
```

### Key Code Patterns

```python
# models/device_group.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime
from sqlalchemy.sql import func, text
from sqlalchemy.orm import relationship
from shared.database.base import Base

class DeviceGroup(Base):
    __tablename__ = "device_groups"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True)
    is_deleted = Column(Boolean, server_default=text("false"), nullable=False, index=True)
    
    # Relationships
    school = relationship("School", back_populates="device_groups")
    devices = relationship("Device", back_populates="device_group", cascade="all, delete-orphan")
    
    # Unique constraint: name must be unique per school
    __table_args__ = (
        {"comment": "Device groups for organizing biometric devices"}
    )
```

### Database Constraints

- Unique constraint on `(school_id, name)` - group names must be unique per school
- Foreign key to `schools.id` (required)
- Index on `school_id`, `name`, `is_deleted`

### Dependencies

- Task 001 (School model must exist)
- Task 027 (Device model exists - update to add device_group_id foreign key)
- Alembic migrations configured

## Visual Testing

### Before State
- No device_groups table exists
- Cannot organize devices into groups

### After State
- Device_groups table exists
- Can create DeviceGroup instances
- Devices can be assigned to groups

### Testing Steps

1. Run migration - verify table created
2. Create test device group - verify all fields work
3. Test relationships - verify foreign keys work
4. Test unique constraint - verify name uniqueness per school
5. Assign device to group - verify relationship works

## Definition of Done

- [x] Code written and follows standards
- [x] Migration script created and tested
- [x] Model relationships verified
- [x] Unique constraints tested
- [x] Foreign keys tested
- [x] Device model updated with device_group_id foreign key
- [x] Comprehensive tests written and passing
- [x] Migration applied to test database

## Time Estimate

3-4 hours

## Notes

- Group names should be descriptive (e.g., "Main Gate", "Dormitories", "Library")
- Description field is optional
- Unique constraint is per-school (not global)
- Devices can belong to zero or one group (nullable relationship)
- Soft delete preserves data integrity

