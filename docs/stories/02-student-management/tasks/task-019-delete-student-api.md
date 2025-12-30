# Task 019: Delete Student API (Soft Delete)

## Story/Phase
- **Story**: Story 02: Student Management
- **Phase**: Phase 2: CRUD Operations

## Description

Create the API endpoint for soft-deleting students (deactivation) with proper authorization.

## Type
- [x] Backend
- [ ] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Acceptance Criteria

1. [x] DELETE `/api/v1/students/{id}` endpoint exists
2. [x] Endpoint requires authentication (JWT token)
3. [x] Performs soft delete (sets is_deleted = true)
4. [x] Student data is preserved (not hard deleted)
5. [x] Returns 204 No Content on success
6. [x] Returns 401 if not authenticated
7. [x] Returns 404 if student not found
8. [x] Returns 404 if student belongs to different school
9. [x] API endpoint is documented

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
@router.delete(
    "/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete student (soft delete)",
    description="""
    Soft delete a student (deactivate).
    
    The student data is preserved but marked as deleted.
    This is a soft delete - the student record remains in the database.
    """,
)
async def delete_student(
    student_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Soft delete a student.
    
    - **Authentication**: Required (JWT token)
    - **Authorization**: Student must belong to user's school
    - **Operation**: Soft delete (sets is_deleted = true)
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
    
    await student_service.delete_student(student_id=student_id)
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)
```

### Dependencies

- Task 017 (Get student endpoint should exist)
- Task 011 (Authentication must work)

## Visual Testing

### Before State
- No endpoint to delete students
- Cannot deactivate students via API

### After State
- Can DELETE `/api/v1/students/{id}`
- Student is soft-deleted
- Student data preserved

### Testing Steps

1. Test without token - verify 401 error
2. Test with valid token - verify soft delete works
3. Test with non-existent ID - verify 404 error
4. Test with student from different school - verify 404 error
5. Verify student is soft-deleted (is_deleted = true)
6. Verify student still exists in database
7. Verify deleted student doesn't appear in list

## Definition of Done

- [x] Code written and follows standards
- [x] Unit tests written and passing
- [x] Integration tests with authentication
- [x] Authorization verified
- [x] Soft delete verified (data preserved)
- [x] API documented
- [x] Error handling comprehensive
- [x] Code reviewed
- [x] Tested with Postman/curl

## Time Estimate

2-3 hours

## Notes

- Soft delete preserves data for audit/history
- Deleted students should not appear in list queries
- Consider adding restore functionality later
- Consider adding hard delete for GDPR compliance (future)

