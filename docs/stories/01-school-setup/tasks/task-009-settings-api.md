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

1. [x] PUT `/api/v1/schools/me` endpoint exists
2. [x] Endpoint requires authentication
3. [x] Endpoint allows updating: name, address, phone, email
4. [x] School code cannot be updated (immutable)
5. [x] Input validation works
6. [x] Returns 200 with updated school data
7. [x] Returns 401 if not authenticated
8. [x] Returns 404 if school not found
9. [x] API endpoint is documented
10. [x] Optional fields can be cleared (set to None)

## Technical Details

### Files to Create/Modify

```
backend/school_service/api/routes/schools.py (add PUT /me endpoint) ✅
backend/shared/schemas/school.py (SchoolUpdate schema already exists) ✅
backend/school_service/services/school_service.py (update_school method already exists) ✅
backend/school_service/repositories/school_repository.py (update method enhanced to support None values) ✅
backend/school_service/tests/test_school_update_api.py (comprehensive test suite) ✅
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

- [x] Code written and follows standards
- [x] Unit tests written and passing (`test_school_update_api.py`)
- [x] Integration tests with authentication
- [x] Code immutability verified
- [x] API documented (OpenAPI/Swagger)
- [x] Error handling comprehensive (401, 404, 422)
- [x] Optional fields can be cleared (None values supported)
- [ ] Code reviewed
- [ ] Tested with Postman/curl

## Time Estimate

4-6 hours

## Notes

- School code should remain immutable for data integrity ✅
- Log updates for audit trail
- Consider versioning if needed
- Validate all inputs before updating ✅
- Optional fields (address, phone, email) can be cleared by setting to `None` ✅

## Test Coverage

Comprehensive test suite created in `backend/school_service/tests/test_school_update_api.py`:

### Test Cases (20+ tests)
- ✅ `test_update_school_success` - Full update with all fields
- ✅ `test_update_school_partial` - Partial update (only some fields)
- ✅ `test_update_school_empty_fields` - Clearing optional fields (set to None)
- ✅ `test_update_school_without_token` - 401 when no token
- ✅ `test_update_school_with_invalid_token` - 401 with invalid token
- ✅ `test_update_school_with_expired_token` - 401 with expired token
- ✅ `test_update_school_invalid_name` - Validation for name
- ✅ `test_update_school_invalid_phone` - Validation for phone format
- ✅ `test_update_school_invalid_email` - Validation for email format
- ✅ `test_update_school_address_too_long` - Validation for address length
- ✅ `test_update_school_code_ignored` - Code immutability verified
- ✅ `test_update_school_not_found` - 404 when school doesn't exist
- ✅ `test_update_school_authorization` - User can only update their own school
- ✅ `test_update_school_api_documented` - OpenAPI documentation check

### Running Tests
```bash
cd backend
pytest school_service/tests/test_school_update_api.py -v
```

