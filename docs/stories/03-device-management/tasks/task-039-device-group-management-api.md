# Task 039: Device Group Management API

## Story/Phase
- **Story**: Story 03: Device Management
- **Phase**: Phase 2: Device Groups

## Description

Create CRUD API endpoints for device group management with validation and authorization.

## Type
- [x] Backend
- [ ] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Acceptance Criteria

1. [x] POST `/api/v1/device-groups` endpoint exists (create)
2. [x] GET `/api/v1/device-groups` endpoint exists (list)
3. [x] GET `/api/v1/device-groups/{id}` endpoint exists (get)
4. [x] PATCH `/api/v1/device-groups/{id}` endpoint exists (update)
5. [x] DELETE `/api/v1/device-groups/{id}` endpoint exists (delete)
6. [x] All endpoints require authentication
7. [x] All operations scoped to user's school
8. [x] Name uniqueness validated per school
9. [x] Returns appropriate status codes
10. [x] All endpoints documented

## Technical Details

### Files to Create/Modify

```
backend/device_service/api/routes/device_groups.py
backend/device_service/services/device_group_service.py
backend/device_service/repositories/device_group_repository.py
```

### Key Code Patterns

```python
# routes/device_groups.py
from fastapi import APIRouter, HTTPException, status, Depends, Path, Query
from device_service.api.dependencies import get_current_user, get_db
from shared.schemas.device_group import (
    DeviceGroupCreate,
    DeviceGroupUpdate,
    DeviceGroupResponse,
    DeviceGroupListResponse,
)
from shared.schemas.auth import UserResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

router = APIRouter(prefix="/api/v1/device-groups", tags=["device-groups"])

@router.post(
    "/",
    response_model=DeviceGroupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create device group",
)
async def create_device_group(
    group_data: DeviceGroupCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new device group."""
    from device_service.services.device_group_service import DeviceGroupService
    
    service = DeviceGroupService(db)
    
    try:
        group = await service.create_device_group(
            group_data=group_data,
            school_id=current_user.school_id
        )
        return DeviceGroupResponse.model_validate(group)
    except ValueError as e:
        if "already exists" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get(
    "/",
    response_model=DeviceGroupListResponse,
    summary="List device groups",
)
async def list_device_groups(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List device groups for user's school."""
    from device_service.services.device_group_service import DeviceGroupService
    
    service = DeviceGroupService(db)
    result = await service.list_device_groups(
        school_id=current_user.school_id,
        page=page,
        page_size=page_size,
    )
    
    return DeviceGroupListResponse(
        items=[DeviceGroupResponse.model_validate(g) for g in result.items],
        total=result.total,
        page=page,
        page_size=page_size,
        pages=(result.total + page_size - 1) // page_size,
    )

@router.get(
    "/{group_id}",
    response_model=DeviceGroupResponse,
    summary="Get device group by ID",
)
async def get_device_group(
    group_id: int = Path(..., description="Device group ID"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a device group by ID."""
    from device_service.services.device_group_service import DeviceGroupService
    
    service = DeviceGroupService(db)
    group = await service.get_device_group_by_id(
        group_id=group_id,
        school_id=current_user.school_id
    )
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device group with ID {group_id} not found",
        )
    
    return DeviceGroupResponse.model_validate(group)

@router.patch(
    "/{group_id}",
    response_model=DeviceGroupResponse,
    summary="Update device group",
)
async def update_device_group(
    group_id: int = Path(..., description="Device group ID"),
    group_data: DeviceGroupUpdate = ...,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a device group."""
    from device_service.services.device_group_service import DeviceGroupService
    
    service = DeviceGroupService(db)
    
    try:
        group = await service.update_device_group(
            group_id=group_id,
            group_data=group_data,
            school_id=current_user.school_id
        )
        
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device group with ID {group_id} not found",
            )
        
        return DeviceGroupResponse.model_validate(group)
    except ValueError as e:
        if "already exists" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete(
    "/{group_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete device group",
)
async def delete_device_group(
    group_id: int = Path(..., description="Device group ID"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete a device group."""
    from device_service.services.device_group_service import DeviceGroupService
    
    service = DeviceGroupService(db)
    success = await service.delete_device_group(
        group_id=group_id,
        school_id=current_user.school_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device group with ID {group_id} not found",
        )
    
    return None
```

### Dependencies

- Task 037 (DeviceGroup model must exist)
- Task 038 (DeviceGroup schemas must exist)
- Task 011 (Authentication must work)

## Visual Testing

### Before State
- No device group API endpoints
- Cannot manage device groups via API

### After State
- All CRUD endpoints work
- Device groups can be created, listed, updated, deleted
- School-level authorization enforced

### Testing Steps

1. Test create device group - verify success
2. Test duplicate name - verify 409 error
3. Test list device groups - verify pagination
4. Test get device group - verify response
5. Test update device group - verify changes
6. Test delete device group - verify soft delete
7. Verify only user's school groups accessible

## Definition of Done

- [x] Code written and follows standards
- [x] All CRUD endpoints implemented
- [x] Unit tests written and passing
- [x] Authorization verified
- [x] Uniqueness validation tested
- [x] API documented
- [x] Code reviewed
- [x] Tested with Postman/curl

## Time Estimate

4-5 hours

## Notes

- Follow same patterns as device CRUD endpoints
- Name uniqueness is per-school (not global)
- Soft delete preserves data integrity
- Device count computed dynamically in response
- Consider if groups with devices should be deletable (for now, allow it)

