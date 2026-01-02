# Task 031: Get Device API

## Story/Phase
- **Story**: Story 03: Device Management
- **Phase**: Phase 1: Device Registration

## Description

Create the API endpoint for retrieving a single device by ID with authorization.

## Type
- [x] Backend
- [ ] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Acceptance Criteria

1. [x] GET `/api/v1/devices/{device_id}` endpoint exists
2. [x] Endpoint requires authentication (JWT token)
3. [x] Returns device only if it belongs to user's school
4. [x] Returns 200 with device data if found
5. [x] Returns 404 if device not found
6. [x] Returns 403 if device belongs to different school
7. [x] Returns 401 if not authenticated
8. [x] API endpoint is documented

## Technical Details

### Files to Create/Modify

```
backend/device_service/api/routes/devices.py
backend/device_service/services/device_service.py
backend/device_service/repositories/device_repository.py
```

### Key Code Patterns

```python
# routes/devices.py
from fastapi import APIRouter, HTTPException, status, Depends, Path
from device_service.api.dependencies import get_current_user, get_db
from shared.schemas.device import DeviceResponse
from shared.schemas.auth import UserResponse
from sqlalchemy.ext.asyncio import AsyncSession

@router.get(
    "/{device_id}",
    response_model=DeviceResponse,
    summary="Get device by ID",
    description="""
    Retrieve a single device by ID.
    
    Only returns devices from the authenticated user's school.
    """,
    responses={
        200: {"description": "Device found"},
        404: {"description": "Device not found"},
        403: {"description": "Device belongs to different school"},
    },
)
async def get_device(
    device_id: int = Path(..., description="Device ID"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a device by ID.
    
    - **Authentication**: Required (JWT token)
    - **Authorization**: Only returns devices from user's school
    """
    from device_service.services.device_service import DeviceService
    
    device_service = DeviceService(db)
    
    device = await device_service.get_device_by_id(
        device_id=device_id,
        school_id=current_user.school_id
    )
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found",
        )
    
    return DeviceResponse.model_validate(device)
```

### Dependencies

- Task 029 (Create device API - service layer exists)
- Task 028 (Device schemas must exist)

## Visual Testing

### Before State
- Cannot retrieve single device via API
- No device detail endpoint

### After State
- Can GET `/api/v1/devices/{id}` for device details
- Returns 404 for non-existent devices
- Enforces school-level authorization

### Testing Steps

1. Test without token - verify 401 error
2. Test with valid token and valid device ID - verify device returned
3. Test with invalid device ID - verify 404 error
4. Test with device from different school - verify 403 error
5. Verify device data structure correct

## Definition of Done

- [x] Code written and follows standards
- [x] Unit tests written and passing
- [x] Authorization verified (school-level access control)
- [x] 404 handling tested
- [x] 403 handling tested
- [x] API documented
- [x] Code reviewed
- [x] Tested with Postman/curl

## Time Estimate

2-3 hours

## Notes

- Service layer should check school_id before returning device
- 403 vs 404: Distinguish between "not found" and "belongs to different school"
- Consider returning soft-deleted devices or not (based on requirements)

