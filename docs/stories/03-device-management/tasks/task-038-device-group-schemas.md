# Task 038: Device Group Schemas

## Story/Phase
- **Story**: Story 03: Device Management
- **Phase**: Phase 2: Device Groups

## Description

Create Pydantic schemas for device group data validation, request/response models, and API documentation.

## Type
- [x] Backend
- [ ] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Acceptance Criteria

1. [ ] DeviceGroupCreate schema exists with validation
2. [ ] DeviceGroupUpdate schema exists (all fields optional)
3. [ ] DeviceGroupResponse schema exists with all fields
4. [ ] DeviceGroupListResponse schema exists with pagination
5. [ ] Name validation (min length, max length)
6. [ ] All schemas documented with descriptions

## Technical Details

### Files to Create/Modify

```
backend/shared/schemas/device_group.py
```

### Key Code Patterns

```python
# schemas/device_group.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class DeviceGroupBase(BaseModel):
    """Base schema with common device group fields."""
    name: str = Field(..., min_length=1, max_length=200, description="Group name")
    description: Optional[str] = Field(None, description="Group description")

class DeviceGroupCreate(DeviceGroupBase):
    """Schema for creating a new device group."""
    pass

class DeviceGroupUpdate(BaseModel):
    """Schema for updating device group (all fields optional)."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None

class DeviceGroupResponse(DeviceGroupBase):
    """Schema for device group response."""
    id: int
    school_id: int
    device_count: int = 0  # Number of devices in group
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class DeviceGroupListResponse(BaseModel):
    """Paginated list of device groups."""
    items: List[DeviceGroupResponse]
    total: int
    page: int
    page_size: int
    pages: int
```

### Dependencies

- Task 037 (DeviceGroup model must exist)

## Visual Testing

### Before State
- No device group schemas exist
- Cannot validate device group data

### After State
- All schemas exist
- Validation works correctly
- API documentation includes schemas

### Testing Steps

1. Test DeviceGroupCreate validation - verify required fields
2. Test name validation - verify min/max length
3. Test DeviceGroupUpdate - verify all fields optional
4. Test DeviceGroupResponse - verify serialization works

## Definition of Done

- [ ] Code written and follows standards
- [ ] All validations tested
- [ ] Schemas documented with descriptions
- [ ] Pydantic v2 patterns used
- [ ] Tests written and passing
- [ ] API documentation shows schemas correctly

## Time Estimate

2 hours

## Notes

- Use Pydantic v2 Field() with proper constraints
- Name validation: 1-200 characters
- Description is optional
- Response schema includes device_count (computed field)
- All standard CRUD schemas included

