# Task 009: Settings API

## Story/Phase
- **Story**: Story 01: School Setup
- **Phase**: Phase 4: Settings and Configuration

## Description

Create the API endpoint to update school information, with validation and proper authorization.

## Type
- [x] Backend
- [ ] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Acceptance Criteria

1. [ ] PUT `/api/v1/schools/me` endpoint exists
2. [ ] Endpoint requires authentication
3. [ ] Endpoint allows updating: name, address, phone, email
4. [ ] School code cannot be updated (immutable)
5. [ ] Input validation works
6. [ ] Returns 200 with updated school data
7. [ ] Returns 401 if not authenticated
8. [ ] Returns 404 if school not found
9. [ ] API endpoint is documented

## Technical Details

### Files to Create/Modify

```
backend/school_service/api/routes/schools.py (add PUT /me endpoint)
backend/school_service/schemas/school.py (add SchoolUpdate schema)
backend/school_service/services/school_service.py (add update method)
```

### Key Code Patterns

```python
# schemas/school.py
class SchoolUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    address: str | None = Field(None, max_length=500)
    phone: str | None = Field(None, regex=r'^\+?[0-9]{10,15}$')
    email: EmailStr | None = None
    # Note: code is not included (immutable)

# routes/schools.py
@router.put("/me", response_model=SchoolResponse)
async def update_my_school(
    school_data: SchoolUpdate,
    current_user: User = Depends(get_current_user)
):
    school = await school_service.get_by_id(current_user.school_id)
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    
    updated_school = await school_service.update(school.id, school_data)
    return SchoolResponse.from_orm(updated_school)
```

### Dependencies

- Task 006 (Authentication must work)
- Task 001 (School model must exist)

## Visual Testing

### Before State
- No endpoint to update school information
- Cannot modify school data

### After State
- Can PUT to `/api/v1/schools/me` with updates
- School data updates correctly
- Code field cannot be changed

### Testing Steps

1. Test without token - verify 401 error
2. Test with valid token - verify update works
3. Try to update code - verify it's ignored/blocked
4. Test validation - verify errors for invalid data
5. Verify updated_at timestamp changes

## Definition of Done

- [ ] Code written and follows standards
- [ ] Unit tests written and passing
- [ ] Integration tests with authentication
- [ ] Code immutability verified
- [ ] API documented
- [ ] Error handling comprehensive
- [ ] Code reviewed
- [ ] Tested with Postman/curl

## Time Estimate

4-6 hours

## Notes

- School code should remain immutable for data integrity
- Log updates for audit trail
- Consider versioning if needed
- Validate all inputs before updating

