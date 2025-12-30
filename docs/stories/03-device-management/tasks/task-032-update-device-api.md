# Task 032: Update Device API

## Story/Phase
- **Story**: Story 03: Device Management
- **Phase**: Phase 1: Device Registration

## Description

Create the API endpoint for updating device information with validation and authorization.

## Type
- [x] Backend
- [ ] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Acceptance Criteria

1. [ ] PUT `/api/v1/devices/{device_id}` endpoint exists
2. [ ] PATCH `/api/v1/devices/{device_id}` endpoint exists (or just PATCH)
3. [ ] Endpoint requires authentication (JWT token)
4. [ ] Only updates devices from user's school
5. [ ] Validates IP/port uniqueness if changed
6. [ ] Validates serial number uniqueness if changed
7. [ ] Returns 200 with updated device data
8. [ ] Returns 404 if device not found
9. [ ] Returns 409 for duplicate IP/port or serial number
10. [ ] Returns 401 if not authenticated
11. [ ] API endpoint is documented

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
from shared.schemas.device import DeviceUpdate, DeviceResponse
from shared.schemas.auth import UserResponse
from sqlalchemy.ext.asyncio import AsyncSession

@router.patch(
    "/{device_id}",
    response_model=DeviceResponse,
    summary="Update device",
    description="""
    Update device information (partial update supported).
    
    If IP/port or serial number is changed, uniqueness is validated.
    Only devices from the authenticated user's school can be updated.
    """,
    responses={
        200: {"description": "Device updated successfully"},
        404: {"description": "Device not found"},
        409: {"description": "Duplicate IP/port or serial number"},
    },
)
async def update_device(
    device_id: int = Path(..., description="Device ID"),
    device_data: DeviceUpdate = ...,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a device.
    
    - **Authentication**: Required (JWT token)
    - **Authorization**: Only updates devices from user's school
    """
    from device_service.services.device_service import DeviceService
    
    device_service = DeviceService(db)
    
    try:
        device = await device_service.update_device(
            device_id=device_id,
            device_data=device_data,
            school_id=current_user.school_id
        )
        
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device with ID {device_id} not found",
            )
        
        return DeviceResponse.model_validate(device)
    except ValueError as e:
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

- Task 031 (Get device API - service layer exists)
- Task 028 (Device schemas must exist)

## Visual Testing

### Before State
- Cannot update devices via API
- No update endpoint

### After State
- Can PATCH `/api/v1/devices/{id}` to update device
- Partial updates work (only provided fields updated)
- Uniqueness validation works

### Testing Steps

1. Test without token - verify 401 error
2. Test with valid token - verify device updated
3. Test partial update - verify only provided fields changed
4. Test duplicate IP/port - verify 409 error
5. Test duplicate serial number - verify 409 error
6. Test invalid device ID - verify 404 error
7. Test device from different school - verify 403 error

## Definition of Done

- [ ] Code written and follows standards
- [ ] Unit tests written and passing
- [ ] Partial update tested
- [ ] Uniqueness validation tested
- [ ] Authorization verified
- [ ] API documented
- [ ] Code reviewed
- [ ] Tested with Postman/curl

## Time Estimate

3-4 hours

## Notes

- Use PATCH for partial updates (not PUT for full replacement)
- Validate uniqueness only if IP/port or serial number is being changed
- Update timestamps automatically (updated_at)
- Consider if status can be updated manually or only via health checks

