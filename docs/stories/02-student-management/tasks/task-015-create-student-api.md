# Task 015: Create Student API

## Story/Phase
- **Story**: Story 02: Student Management
- **Phase**: Phase 2: CRUD Operations

## Description

Create the API endpoint for creating new students with validation, error handling, and proper authorization.

## Type
- [x] Backend
- [ ] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Acceptance Criteria

1. [x] POST `/api/v1/students` endpoint exists
2. [x] Endpoint requires authentication (JWT token)
3. [x] Endpoint validates all required fields
4. [x] Admission number uniqueness validated per school
5. [x] Student is associated with authenticated user's school
6. [x] Returns 201 with created student data
7. [x] Returns 422 for validation errors
8. [x] Returns 409 for duplicate admission number
9. [x] Returns 401 if not authenticated
10. [x] API endpoint is documented

## Technical Details

### Files to Create/Modify

```
backend/school_service/api/routes/students.py
backend/school_service/services/student_service.py
backend/school_service/repositories/student_repository.py
backend/school_service/tests/test_student_api.py
```

### Key Code Patterns

```python
# routes/students.py
from fastapi import APIRouter, HTTPException, status, Depends
from school_service.api.routes.auth import get_current_user
from shared.schemas.student import StudentCreate, StudentResponse

router = APIRouter(prefix="/api/v1/students", tags=["students"])

@router.post(
    "/",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new student",
    description="""
    Create a new student in the authenticated user's school.
    
    The admission number must be unique within the school.
    """,
)
async def create_student(
    student_data: StudentCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new student.
    
    - **Authentication**: Required (JWT token)
    - **Authorization**: Student is automatically associated with user's school
    """
    student_service = StudentService(db)
    
    # Ensure student is created for the authenticated user's school
    student_data.school_id = current_user.school_id
    
    try:
        student = await student_service.create_student(student_data)
        return StudentResponse.model_validate(student)
    except ValueError as e:
        # Handle validation errors (duplicate admission number, etc.)
        error_msg = str(e)
        if "admission number" in error_msg.lower():
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

- Task 012 (Student model must exist)
- Task 014 (Student schemas must exist)
- Task 011 (Authentication must work)

## Visual Testing

### Before State
- No endpoint to create students
- Cannot add students via API

### After State
- Can POST to `/api/v1/students` with student data
- Student created successfully
- Admission number uniqueness enforced

### Testing Steps

1. Test without token - verify 401 error
2. Test with valid token - verify student created
3. Test duplicate admission number - verify 409 error
4. Test validation errors - verify 422 error
5. Verify student associated with correct school

## Definition of Done

- [x] Code written and follows standards
- [x] Unit tests written and passing
- [x] Integration tests with authentication
- [x] Authorization verified (user can only create students in their school)
- [x] API documented (OpenAPI/Swagger)
- [x] Error handling comprehensive
- [x] Code reviewed
- [x] Tested with Postman/curl

## Time Estimate

4-6 hours

## Notes

- Admission number uniqueness is per-school (not global)
- Student is automatically associated with authenticated user's school
- Class and stream assignment is optional (can be done later)
- Parent contact information is optional but recommended

