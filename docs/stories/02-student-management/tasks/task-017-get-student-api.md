# Task 017: Get Student by ID API

## Story/Phase
- **Story**: Story 02: Student Management
- **Phase**: Phase 2: CRUD Operations

## Description

Create the API endpoint for retrieving a single student by ID with proper authorization.

## Type
- [x] Backend
- [ ] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Acceptance Criteria

1. [x] GET `/api/v1/students/{id}` endpoint exists
2. [x] Endpoint requires authentication (JWT token)
3. [x] Returns student only if belongs to user's school
4. [x] Returns 200 with student data
5. [x] Returns 404 if student not found
6. [x] Returns 404 if student belongs to different school
7. [x] Returns 401 if not authenticated
8. [x] API endpoint is documented

## Technical Details

### Files to Create/Modify

```
backend/school_service/api/routes/students.py
backend/school_service/services/student_service.py
backend/school_service/repositories/student_repository.py
```

### Key Code Patterns

```python
# routes/students.py
@router.get(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Get student by ID",
    description="""
    Get a specific student by ID.
    
    The student must belong to the authenticated user's school.
    """,
)
async def get_student(
    student_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a student by ID.
    
    - **Authentication**: Required (JWT token)
    - **Authorization**: Student must belong to user's school
    """
    student_service = StudentService(db)
    
    student = await student_service.get_student_by_id(
        student_id=student_id,
        school_id=current_user.school_id,
    )
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )
    
    return StudentResponse.model_validate(student)
```

### Dependencies

- Task 015 (Create student endpoint should exist)
- Task 011 (Authentication must work)

## Visual Testing

### Before State
- No endpoint to get individual student
- Cannot retrieve student details via API

### After State
- Can GET `/api/v1/students/{id}` with student ID
- Receives student data
- Authorization enforced

### Testing Steps

1. Test without token - verify 401 error
2. Test with valid token - verify student returned
3. Test with non-existent ID - verify 404 error
4. Test with student from different school - verify 404 error
5. Verify student data structure

## Definition of Done

- [x] Code written and follows standards
- [x] Unit tests written and passing
- [x] Integration tests with authentication
- [x] Authorization verified (user can only access their school's students)
- [x] API documented
- [x] Error handling comprehensive
- [x] Code reviewed
- [x] Tested with Postman/curl

## Time Estimate

2-3 hours

## Notes

- Student must belong to authenticated user's school
- Soft-deleted students should return 404
- Consider including related data (class, stream) in response

