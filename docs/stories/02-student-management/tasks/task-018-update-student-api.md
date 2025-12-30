# Task 018: Update Student API

## Story/Phase
- **Story**: Story 02: Student Management
- **Phase**: Phase 2: CRUD Operations

## Description

Create the API endpoint for updating student information with validation and proper authorization.

## Type
- [x] Backend
- [ ] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Acceptance Criteria

1. [ ] PUT `/api/v1/students/{id}` endpoint exists
2. [ ] Endpoint requires authentication (JWT token)
3. [ ] Allows updating: name, DOB, gender, class_id, stream_id, parent contacts
4. [ ] Admission number cannot be updated (immutable)
5. [ ] School ID cannot be updated (immutable)
6. [ ] Input validation works
7. [ ] Returns 200 with updated student data
8. [ ] Returns 401 if not authenticated
9. [ ] Returns 404 if student not found
10. [ ] Returns 404 if student belongs to different school
11. [ ] API endpoint is documented

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
@router.put(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Update student",
    description="""
    Update student information.
    
    Admission number and school ID cannot be changed.
    """,
)
async def update_student(
    student_id: int,
    student_data: StudentUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a student.
    
    - **Authentication**: Required (JWT token)
    - **Authorization**: Student must belong to user's school
    - **Immutable Fields**: admission_number, school_id
    """
    student_service = StudentService(db)
    
    # Verify student exists and belongs to user's school
    existing_student = await student_service.get_student_by_id(
        student_id=student_id,
        school_id=current_user.school_id,
    )
    
    if not existing_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )
    
    updated_student = await student_service.update_student(
        student_id=student_id,
        student_data=student_data,
    )
    
    return StudentResponse.model_validate(updated_student)
```

### Dependencies

- Task 017 (Get student endpoint should exist)
- Task 011 (Authentication must work)

## Visual Testing

### Before State
- No endpoint to update students
- Cannot modify student data via API

### After State
- Can PUT to `/api/v1/students/{id}` with updates
- Student data updates correctly
- Immutable fields cannot be changed

### Testing Steps

1. Test without token - verify 401 error
2. Test with valid token - verify update works
3. Test with non-existent ID - verify 404 error
4. Test with student from different school - verify 404 error
5. Test validation - verify errors for invalid data
6. Verify immutable fields cannot be changed

## Definition of Done

- [ ] Code written and follows standards
- [ ] Unit tests written and passing
- [ ] Integration tests with authentication
- [ ] Authorization verified
- [ ] Immutability verified
- [ ] API documented
- [ ] Error handling comprehensive
- [ ] Code reviewed
- [ ] Tested with Postman/curl

## Time Estimate

3-4 hours

## Notes

- Admission number and school_id are immutable
- Class and stream assignment can be updated
- Parent contact information can be updated
- Validation should match create endpoint

