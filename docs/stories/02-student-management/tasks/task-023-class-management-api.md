# Task 023: Class Management API

## Story/Phase
- **Story**: Story 02: Student Management
- **Phase**: Phase 3: Class Assignment

## Description

Create API endpoints for managing classes (create, list, update, delete) with proper authorization.

## Type
- [x] Backend
- [ ] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Acceptance Criteria

1. [ ] POST `/api/v1/classes` endpoint exists
2. [ ] GET `/api/v1/classes` endpoint exists (list)
3. [ ] GET `/api/v1/classes/{id}` endpoint exists
4. [ ] PUT `/api/v1/classes/{id}` endpoint exists
5. [ ] DELETE `/api/v1/classes/{id}` endpoint exists (soft delete)
6. [ ] Endpoints require authentication
7. [ ] Classes are scoped to authenticated user's school
8. [ ] Class name uniqueness validated per school
9. [ ] Returns appropriate status codes
10. [ ] API endpoints are documented

## Technical Details

### Files to Create/Modify

```
backend/school_service/api/routes/classes.py
backend/school_service/services/class_service.py
backend/school_service/repositories/class_repository.py
backend/school_service/tests/test_class_api.py
```

### Key Code Patterns

```python
# routes/classes.py
from fastapi import APIRouter, HTTPException, status, Depends
from school_service.api.routes.auth import get_current_user
from shared.schemas.class_schema import ClassCreate, ClassUpdate, ClassResponse

router = APIRouter(prefix="/api/v1/classes", tags=["classes"])

@router.post(
    "/",
    response_model=ClassResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new class",
)
async def create_class(
    class_data: ClassCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new class in the authenticated user's school.
    
    - **Authentication**: Required (JWT token)
    - **Authorization**: Class is automatically associated with user's school
    """
    class_service = ClassService(db)
    
    # Ensure class is created for the authenticated user's school
    class_data.school_id = current_user.school_id
    
    try:
        class_obj = await class_service.create_class(class_data)
        return ClassResponse.model_validate(class_obj)
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
    response_model=List[ClassResponse],
    summary="List classes",
)
async def list_classes(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all classes in the authenticated user's school.
    """
    class_service = ClassService(db)
    classes = await class_service.list_classes(school_id=current_user.school_id)
    return [ClassResponse.model_validate(c) for c in classes]
```

### Dependencies

- Task 013 (Class model must exist)
- Task 014 (Class schemas must exist)
- Task 011 (Authentication must work)

## Visual Testing

### Before State
- No endpoints to manage classes
- Cannot create classes via API

### After State
- Can create, list, update, delete classes
- Classes scoped to user's school
- Name uniqueness enforced

### Testing Steps

1. Test create class - verify success
2. Test duplicate name - verify 409 error
3. Test list classes - verify only user's school classes
4. Test update class - verify success
5. Test delete class - verify soft delete

## Definition of Done

- [ ] Code written and follows standards
- [ ] Unit tests written and passing
- [ ] Integration tests with authentication
- [ ] Authorization verified
- [ ] API documented
- [ ] Error handling comprehensive
- [ ] Code reviewed
- [ ] Tested with Postman/curl

## Time Estimate

4-6 hours

## Notes

- Class names are unique per school
- Soft delete preserves data
- Consider cascade behavior for streams when class deleted
- Class name should be descriptive (e.g., "Form 1", "Grade 3")

