# Task 028: Device Schemas

## Story/Phase
- **Story**: Story 03: Device Management
- **Phase**: Phase 1: Device Registration

## Description

Create Pydantic schemas for device data validation, request/response models, and API documentation.

## Type
- [x] Backend
- [ ] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Acceptance Criteria

1. [ ] DeviceCreate schema exists with validation
2. [ ] DeviceUpdate schema exists (all fields optional)
3. [ ] DeviceResponse schema exists with all fields
4. [ ] DeviceListResponse schema exists with pagination
5. [ ] IP address validation (IPv4/IPv6 format)
6. [ ] Port validation (1-65535 range)
7. [ ] Serial number validation (if provided)
8. [ ] Status enum properly defined
9. [ ] All schemas documented with descriptions

## Technical Details

### Files to Create/Modify

```
backend/shared/schemas/device.py
```

### Key Code Patterns

```python
# schemas/device.py
from pydantic import BaseModel, Field, field_validator, IPvAnyAddress
from typing import Optional
from datetime import datetime
from enum import Enum

class DeviceStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    UNKNOWN = "unknown"

class DeviceBase(BaseModel):
    """Base schema with common device fields."""
    name: str = Field(..., min_length=1, max_length=200, description="Device display name")
    ip_address: str = Field(..., description="Device IP address (IPv4 or IPv6)")
    port: int = Field(default=4370, ge=1, le=65535, description="Device port (default: 4370)")
    serial_number: Optional[str] = Field(None, max_length=100, description="Device serial number")
    location: Optional[str] = Field(None, max_length=200, description="Device location")
    description: Optional[str] = Field(None, description="Device description")

    @field_validator("ip_address")
    @classmethod
    def validate_ip_address(cls, v: str) -> str:
        """Validate IP address format."""
        try:
            IPvAnyAddress(v)
            return v
        except Exception:
            raise ValueError("Invalid IP address format")

class DeviceCreate(DeviceBase):
    """Schema for creating a new device."""
    device_group_id: Optional[int] = Field(None, description="Optional device group ID")

class DeviceUpdate(BaseModel):
    """Schema for updating device (all fields optional)."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    ip_address: Optional[str] = None
    port: Optional[int] = Field(None, ge=1, le=65535)
    serial_number: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    device_group_id: Optional[int] = None

    @field_validator("ip_address")
    @classmethod
    def validate_ip_address(cls, v: Optional[str]) -> Optional[str]:
        """Validate IP address format if provided."""
        if v is None:
            return v
        try:
            IPvAnyAddress(v)
            return v
        except Exception:
            raise ValueError("Invalid IP address format")

class DeviceResponse(DeviceBase):
    """Schema for device response."""
    id: int
    school_id: int
    status: DeviceStatus
    last_seen: Optional[datetime] = None
    last_sync: Optional[datetime] = None
    max_users: Optional[int] = None
    enrolled_users: int = 0
    device_group_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class DeviceListResponse(BaseModel):
    """Paginated list of devices."""
    items: list[DeviceResponse]
    total: int
    page: int
    page_size: int
    pages: int

class DeviceConnectionTest(BaseModel):
    """Schema for connection test request."""
    timeout: Optional[int] = Field(default=5, ge=1, le=30, description="Connection timeout in seconds")

class DeviceConnectionTestResponse(BaseModel):
    """Schema for connection test response."""
    success: bool
    message: str
    device_info: Optional[dict] = None  # Device information if connection successful
    response_time_ms: Optional[int] = None
```

### Dependencies

- Task 027 (Device model must exist)

## Visual Testing

### Before State
- No device schemas exist
- Cannot validate device data

### After State
- All schemas exist
- Validation works correctly
- API documentation includes schemas

### Testing Steps

1. Test DeviceCreate validation - verify required fields
2. Test IP address validation - verify IPv4/IPv6 formats
3. Test port validation - verify range 1-65535
4. Test DeviceUpdate - verify all fields optional
5. Test DeviceResponse - verify serialization works

## Definition of Done

- [ ] Code written and follows standards
- [ ] All validations tested
- [ ] Schemas documented with descriptions
- [ ] Pydantic v2 patterns used
- [ ] Tests written and passing
- [ ] API documentation shows schemas correctly

## Time Estimate

2-3 hours

## Notes

- Use Pydantic v2 Field() with proper constraints
- IP validation should support both IPv4 and IPv6
- Port range validation prevents invalid ports
- Serial number is optional (can be added after connection)
- Status enum matches database enum
- Response schemas include all computed fields (last_seen, enrolled_users, etc.)

