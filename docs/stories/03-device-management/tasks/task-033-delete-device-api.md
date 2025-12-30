# Task 033: Delete Device API

## Story/Phase
- **Story**: Story 03: Device Management
- **Phase**: Phase 1: Device Registration

## Description

Create the API endpoint for soft-deleting devices with authorization checks.

## Type
- [x] Backend
- [ ] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Acceptance Criteria

1. [ ] DELETE `/api/v1/devices/{device_id}` endpoint exists
2. [ ] Endpoint requires authentication (JWT token)
3. [ ] Only deletes devices from user's school
4. [ ] Uses soft delete (sets is_deleted = true)
5. [ ] Returns 204 No Content on success
6. [ ] Returns 404 if device not found
7. [ ] Returns 401 if not authenticated
8. [ ] Soft-deleted devices excluded from list/get endpoints
9. [ ] API endpoint is documented

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
from shared.schemas.auth import UserResponse
from sqlalchemy.ext.asyncio import AsyncSession

@router.delete(
    "/{device_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete device",
    description="""
    Soft-delete a device (sets is_deleted = true).
    
    Only devices from the authenticated user's school can be deleted.
    Soft-deleted devices are excluded from list and get operations.
    """,
    responses={
        204: {"description": "Device deleted successfully"},
        404: {"description": "Device not found"},
    },
)
async def delete_device(
    device_id: int = Path(..., description="Device ID"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a device (soft delete).
    
    - **Authentication**: Required (JWT token)
    - **Authorization**: Only deletes devices from user's school
    """
    from device_service.services.device_service import DeviceService
    
    device_service = DeviceService(db)
    
    success = await device_service.delete_device(
        device_id=device_id,
        school_id=current_user.school_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found",
        )
    
    return None  # 204 No Content
```

### Dependencies

- Task 032 (Update device API - service layer exists)
- Task 028 (Device schemas must exist)

## Visual Testing

### Before State
- Cannot delete devices via API
- No delete endpoint

### After State
- Can DELETE `/api/v1/devices/{id}` to delete device
- Device soft-deleted (is_deleted = true)
- Deleted devices excluded from lists

### Testing Steps

1. Test without token - verify 401 error
2. Test with valid token - verify device deleted (204 response)
3. Test invalid device ID - verify 404 error
4. Test device from different school - verify 403/404 error
5. Verify device excluded from list after deletion
6. Verify device not returned by get endpoint after deletion

## Definition of Done

- [ ] Code written and follows standards
- [ ] Unit tests written and passing
- [ ] Soft delete tested (is_deleted flag set)
- [ ] Authorization verified
- [ ] Excluded from list/get tested
- [ ] API documented
- [ ] Code reviewed
- [ ] Tested with Postman/curl

## Time Estimate

2-3 hours

## Notes

- Use soft delete (not hard delete) to preserve data integrity
- Consider if devices with active enrollments should be deletable
- Consider restore functionality (future enhancement)
- Update timestamps (updated_at) on soft delete

