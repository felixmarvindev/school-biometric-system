# Task 030: List Devices API

## Story/Phase
- **Story**: Story 03: Device Management
- **Phase**: Phase 1: Device Registration

## Description

Create the API endpoint for listing devices with filtering, search, and pagination.

## Type
- [x] Backend
- [ ] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Acceptance Criteria

1. [ ] GET `/api/v1/devices` endpoint exists
2. [ ] Endpoint requires authentication (JWT token)
3. [ ] Returns only devices from authenticated user's school
4. [ ] Supports pagination (page, page_size)
5. [ ] Supports search by name, IP address, or serial number
6. [ ] Supports filtering by status (online, offline, unknown)
7. [ ] Supports filtering by device group (if provided)
8. [ ] Returns paginated response with metadata
9. [ ] Default page size is 50
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
from fastapi import APIRouter, Query, Depends
from device_service.api.dependencies import get_current_user, get_db
from shared.schemas.device import DeviceListResponse, DeviceStatus
from shared.schemas.auth import UserResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

@router.get(
    "/",
    response_model=DeviceListResponse,
    summary="List devices",
    description="""
    Get a paginated list of devices for the authenticated user's school.
    
    Supports search, filtering by status and group, and pagination.
    """,
)
async def list_devices(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by name, IP, or serial number"),
    status: Optional[DeviceStatus] = Query(None, description="Filter by device status"),
    device_group_id: Optional[int] = Query(None, description="Filter by device group"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List devices with pagination and filtering.
    
    - **Authentication**: Required (JWT token)
    - **Authorization**: Only returns devices from user's school
    """
    from device_service.services.device_service import DeviceService
    
    device_service = DeviceService(db)
    
    result = await device_service.list_devices(
        school_id=current_user.school_id,
        page=page,
        page_size=page_size,
        search=search,
        status=status,
        device_group_id=device_group_id,
    )
    
    return DeviceListResponse(
        items=[DeviceResponse.model_validate(d) for d in result.items],
        total=result.total,
        page=page,
        page_size=page_size,
        pages=(result.total + page_size - 1) // page_size,
    )
```

### Dependencies

- Task 029 (Create device API - service layer exists)
- Task 028 (Device schemas must exist)

## Visual Testing

### Before State
- Cannot list devices via API
- No pagination or filtering

### After State
- Can GET `/api/v1/devices` with pagination
- Can search and filter devices
- Only returns devices from user's school

### Testing Steps

1. Test without token - verify 401 error
2. Test with valid token - verify devices returned
3. Test pagination - verify page/page_size works
4. Test search - verify name/IP/serial search works
5. Test status filter - verify filtering works
6. Test group filter - verify group filtering works
7. Verify only user's school devices returned

## Definition of Done

- [ ] Code written and follows standards
- [ ] Unit tests written and passing
- [ ] Pagination tested
- [ ] Search functionality tested
- [ ] Filtering tested
- [ ] Authorization verified
- [ ] API documented
- [ ] Code reviewed
- [ ] Tested with Postman/curl

## Time Estimate

4-5 hours

## Notes

- Search should match name, IP address, or serial number (case-insensitive)
- Status filter uses enum values (online, offline, unknown)
- Group filter only works if device groups exist (Phase 2)
- Default page size of 50, maximum 100
- Results sorted by created_at descending (newest first)

