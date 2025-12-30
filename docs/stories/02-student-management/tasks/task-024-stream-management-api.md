# Task 024: Stream Management API

## Story/Phase
- **Story**: Story 02: Student Management
- **Phase**: Phase 3: Class Assignment

## Description

Create API endpoints for managing streams (create, list, update, delete) within classes.

## Type
- [x] Backend
- [ ] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Acceptance Criteria

1. [x] POST `/api/v1/streams` endpoint exists
2. [x] GET `/api/v1/streams` endpoint exists (list, filtered by class)
3. [x] GET `/api/v1/streams/{id}` endpoint exists
4. [x] PUT `/api/v1/streams/{id}` endpoint exists
5. [x] DELETE `/api/v1/streams/{id}` endpoint exists (soft delete)
6. [x] Endpoints require authentication
7. [x] Streams are scoped to authenticated user's school
8. [x] Stream name uniqueness validated per class
9. [x] Class ownership validated (stream belongs to user's school class)
10. [x] Returns appropriate status codes
11. [x] API endpoints are documented

## Technical Details

### Files to Create/Modify

```
backend/school_service/api/routes/streams.py
backend/school_service/services/stream_service.py
backend/school_service/repositories/stream_repository.py
backend/school_service/tests/test_stream_api.py
```

### Key Code Patterns

```python
# routes/streams.py
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional
from school_service.api.routes.auth import get_current_user
from shared.schemas.stream_schema import StreamCreate, StreamUpdate, StreamResponse

router = APIRouter(prefix="/api/v1/streams", tags=["streams"])

@router.post(
    "/",
    response_model=StreamResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new stream",
)
async def create_stream(
    stream_data: StreamCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new stream within a class.
    
    - **Authentication**: Required (JWT token)
    - **Authorization**: Class must belong to user's school
    """
    stream_service = StreamService(db)
    
    # Verify class belongs to user's school
    class_obj = await class_service.get_class_by_id(
        class_id=stream_data.class_id,
        school_id=current_user.school_id,
    )
    
    if not class_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found",
        )
    
    try:
        stream = await stream_service.create_stream(stream_data)
        return StreamResponse.model_validate(stream)
    except ValueError as e:
        if "name" in str(e).lower() and "unique" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e),
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

@router.get(
    "/",
    response_model=List[StreamResponse],
    summary="List streams",
)
async def list_streams(
    class_id: Optional[int] = Query(None, description="Filter by class ID"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List streams, optionally filtered by class.
    
    Only returns streams from classes in the authenticated user's school.
    """
    stream_service = StreamService(db)
    
    # If class_id provided, verify it belongs to user's school
    if class_id:
        class_obj = await class_service.get_class_by_id(
            class_id=class_id,
            school_id=current_user.school_id,
        )
        if not class_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Class not found",
            )
    
    streams = await stream_service.list_streams(
        school_id=current_user.school_id,
        class_id=class_id,
    )
    return [StreamResponse.model_validate(s) for s in streams]
```

### Dependencies

- Task 013 (Stream model must exist)
- Task 014 (Stream schemas must exist)
- Task 023 (Class management API should exist)
- Task 011 (Authentication must work)

## Visual Testing

### Before State
- No endpoints to manage streams
- Cannot create streams via API

### After State
- Can create, list, update, delete streams
- Streams scoped to user's school classes
- Name uniqueness enforced per class

### Testing Steps

1. Test create stream - verify success
2. Test duplicate name in same class - verify 409 error
3. Test duplicate name in different class - verify success
4. Test list streams - verify filtering works
5. Test update stream - verify success
6. Test delete stream - verify soft delete

## Definition of Done

- [x] Code written and follows standards
- [x] Unit tests written and passing
- [x] Integration tests with authentication
- [x] Authorization verified
- [x] API documented
- [x] Error handling comprehensive
- [x] Code reviewed
- [x] Tested with Postman/curl

## Time Estimate

4-6 hours

## Notes

- Stream names are unique per class (not per school)
- Streams must belong to a class
- Class must belong to user's school
- Soft delete preserves data
- Consider cascade behavior for students when stream deleted

