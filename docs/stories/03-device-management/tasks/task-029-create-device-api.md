# Task 029: Create Device API

## Story/Phase
- **Story**: Story 03: Device Management
- **Phase**: Phase 1: Device Registration

## Description

Create the API endpoint for registering new devices with validation, error handling, and proper authorization.

## Type
- [x] Backend
- [ ] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Acceptance Criteria

1. [x] POST `/api/v1/devices` endpoint exists
2. [x] Endpoint requires authentication (JWT token)
3. [x] Endpoint validates all required fields
4. [x] IP address and port combination validated per school (unique)
5. [x] Serial number uniqueness validated (global)
6. [x] Device is associated with authenticated user's school
7. [x] Returns 201 with created device data
8. [x] Returns 422 for validation errors
9. [x] Returns 409 for duplicate IP/port or serial number
10. [x] Returns 401 if not authenticated
11. [x] API endpoint is documented

## Technical Details

### Files to Create/Modify

```
backend/device_service/api/routes/devices.py
backend/device_service/services/device_service.py
backend/device_service/repositories/device_repository.py
backend/device_service/tests/test_device_api.py
```

### Key Code Patterns

```python
# routes/devices.py
from fastapi import APIRouter, HTTPException, status, Depends
from device_service.api.dependencies import get_current_user, get_db
from shared.schemas.device import DeviceCreate, DeviceResponse
from shared.schemas.auth import UserResponse
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/v1/devices", tags=["devices"])

@router.post(
    "/",
    response_model=DeviceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new device",
    description="""
    Register a new biometric device in the authenticated user's school.
    
    The IP address and port combination must be unique within the school.
    Serial number (if provided) must be globally unique.
    """,
)
async def create_device(
    device_data: DeviceCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new device.
    
    - **Authentication**: Required (JWT token)
    - **Authorization**: Device is automatically associated with user's school
    """
    from device_service.services.device_service import DeviceService
    
    device_service = DeviceService(db)
    
    # Ensure device is created for the authenticated user's school
    try:
        device = await device_service.create_device(
            device_data=device_data,
            school_id=current_user.school_id
        )
        return DeviceResponse.model_validate(device)
    except ValueError as e:
        # Handle validation errors (duplicate IP/port, serial number, etc.)
        error_msg = str(e)
        if "already exists" in error_msg.lower() or "duplicate" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_msg,
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        )
```

### Dependencies

- Task 027 (Device model must exist)
- Task 028 (Device schemas must exist)
- Task 011 (Authentication must work)

## Visual Testing

### Before State
- No endpoint to register devices
- Cannot add devices via API

### After State
- Can POST to `/api/v1/devices` with device data
- Device created successfully
- IP/port and serial number uniqueness enforced

### Testing Steps

1. Test without token - verify 401 error
2. Test with valid token - verify device created
3. Test duplicate IP/port - verify 409 error
4. Test duplicate serial number - verify 409 error
5. Test validation errors - verify 422 error
6. Verify device associated with correct school

## Definition of Done

- [x] Code written and follows standards
- [x] Unit tests written and passing
- [x] Integration tests with authentication
- [x] Authorization verified (user can only create devices in their school)
- [x] API documented (OpenAPI/Swagger)
- [x] Error handling comprehensive
- [x] Code reviewed
- [x] Tested with Postman/curl

## Time Estimate

4-6 hours

## Notes

- IP/port uniqueness is per-school (not global)
- Serial number uniqueness is global (if provided)
- Device status starts as "unknown" until first connection test
- Device group assignment is optional (can be done later)

