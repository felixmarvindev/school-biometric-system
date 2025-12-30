# Task 016: List Students API

## Story/Phase
- **Story**: Story 02: Student Management
- **Phase**: Phase 2: CRUD Operations

## Description

Create the API endpoint for listing students with pagination, filtering, and search capabilities.

## Type
- [x] Backend
- [ ] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Acceptance Criteria

1. [ ] GET `/api/v1/students` endpoint exists
2. [ ] Endpoint requires authentication (JWT token)
3. [ ] Returns only students from authenticated user's school
4. [ ] Pagination support (page, page_size)
5. [ ] Filtering by class_id (optional)
6. [ ] Filtering by stream_id (optional)
7. [ ] Search by name (optional)
8. [ ] Search by admission_number (optional)
9. [ ] Returns paginated response with metadata
10. [ ] Returns 401 if not authenticated
11. [ ] API endpoint is documented

## Technical Details

### Files to Create/Modify

```
backend/school_service/api/routes/students.py
backend/school_service/services/student_service.py
backend/school_service/repositories/student_repository.py
backend/shared/schemas/student.py (add pagination schemas)
```

### Key Code Patterns

```python
# routes/students.py
from fastapi import Query
from typing import Optional

@router.get(
    "/",
    response_model=PaginatedStudentResponse,
    summary="List students",
    description="""
    Get a paginated list of students from the authenticated user's school.
    
    Supports filtering by class, stream, and searching by name or admission number.
    """,
)
async def list_students(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    class_id: Optional[int] = Query(None, description="Filter by class ID"),
    stream_id: Optional[int] = Query(None, description="Filter by stream ID"),
    search: Optional[str] = Query(None, min_length=1, description="Search by name or admission number"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List students with pagination and filtering.
    
    - **Authentication**: Required (JWT token)
    - **Authorization**: Only returns students from user's school
    """
    student_service = StudentService(db)
    
    result = await student_service.list_students(
        school_id=current_user.school_id,
        page=page,
        page_size=page_size,
        class_id=class_id,
        stream_id=stream_id,
        search=search,
    )
    
    return result
```

### Pagination Response Schema

```python
# schemas/student.py
from typing import List

class PaginatedStudentResponse(BaseModel):
    """Paginated response for student list."""
    items: List[StudentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
```

### Dependencies

- Task 015 (Create student endpoint should exist)
- Task 011 (Authentication must work)

## Visual Testing

### Before State
- No endpoint to list students
- Cannot retrieve student list via API

### After State
- Can GET `/api/v1/students` with pagination
- Can filter by class/stream
- Can search by name/admission number
- Receives paginated response

### Testing Steps

1. Test without token - verify 401 error
2. Test with valid token - verify student list
3. Test pagination - verify page/page_size work
4. Test filtering - verify class_id and stream_id filters work
5. Test search - verify name and admission_number search work
6. Verify only user's school students returned

## Definition of Done

- [ ] Code written and follows standards
- [ ] Unit tests written and passing
- [ ] Integration tests with authentication
- [ ] Pagination tested
- [ ] Filtering tested
- [ ] Search tested
- [ ] Authorization verified
- [ ] API documented
- [ ] Code reviewed
- [ ] Tested with Postman/curl

## Time Estimate

4-6 hours

## Notes

- Default page size: 50 items
- Maximum page size: 100 items
- Search should be case-insensitive
- Search should match both first_name and last_name
- Only active (non-deleted) students returned by default
- Consider adding sorting options (by name, admission_number, created_at)

