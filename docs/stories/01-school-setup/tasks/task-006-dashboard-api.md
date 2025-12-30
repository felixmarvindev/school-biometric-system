# Task 006: Dashboard API

## Story/Phase
- **Story**: Story 01: School Setup
- **Phase**: Phase 3: Dashboard Setup

## Description

Create the API endpoint to fetch school information for the authenticated user's dashboard, with proper authentication and authorization.

## Type
- [x] Backend
- [ ] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Acceptance Criteria

1. [x] GET `/api/v1/schools/me` endpoint exists
2. [x] Endpoint requires authentication (JWT token)
3. [x] Endpoint returns current user's school data
4. [x] Authorization ensures user can only see their school
5. [x] Returns 401 if not authenticated
6. [x] Returns 404 if school not found
7. [x] Response includes school information
8. [x] API endpoint is documented

## Technical Details

### Files to Create/Modify

```
backend/school_service/api/routes/schools.py (add GET /me endpoint) ✅
backend/school_service/api/routes/auth.py (get_current_user already exists) ✅
backend/school_service/core/security.py (token validation already exists) ✅
```

### Key Code Patterns

**Implementation:**
```python
# routes/schools.py
from school_service.api.routes.auth import get_current_user
from shared.schemas.user import UserResponse

@router.get("/me", response_model=SchoolResponse)
async def get_my_school(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    school_service = SchoolService(db)
    school = await school_service.get_school_by_id(current_user.school_id)
    
    if not school or school.is_deleted:
        raise HTTPException(status_code=404, detail="School not found")
    
    return SchoolResponse.model_validate(school)
```

**Note:** `get_current_user` dependency already exists in `backend/school_service/api/routes/auth.py` and handles:
- JWT token extraction and validation
- User lookup from database
- Active user check
- Returns `UserResponse` with `school_id` for authorization

### Dependencies

- Task 004 (Authentication must work)
- Task 001 (School model must exist)
- JWT token validation working

## Visual Testing

### Before State
- No endpoint to get current user's school
- Cannot fetch school data for dashboard

### After State
- Can GET `/api/v1/schools/me` with token
- Receives school data
- Unauthorized requests return 401

### Testing Steps

1. Test without token - verify 401 error
2. Test with invalid token - verify 401 error
3. Test with valid token - verify 200 with school data
4. Verify user can only see their own school

## Definition of Done

- [x] Code written and follows standards
- [x] Unit tests written and passing (`test_dashboard_api.py`)
- [x] Integration tests with authentication
- [x] Authorization verified (user can only access their school via school_id)
- [x] API documented (OpenAPI/Swagger docs auto-generated)
- [x] Error handling comprehensive (401, 404)
- [ ] Code reviewed
- [ ] Tested with Postman/curl

## Test Coverage

Comprehensive test suite created in `backend/school_service/tests/test_dashboard_api.py`:

### Test Cases
- ✅ `test_get_my_school_success` - Successful retrieval with valid token
- ✅ `test_get_my_school_without_token` - 401 when no token provided
- ✅ `test_get_my_school_with_invalid_token` - 401 with invalid token
- ✅ `test_get_my_school_with_expired_token` - 401 with expired token
- ✅ `test_get_my_school_not_found` - 404 when school doesn't exist
- ✅ `test_get_my_school_deleted` - 404 when school is soft-deleted
- ✅ `test_get_my_school_authorization` - User can only see their own school
- ✅ `test_get_my_school_inactive_user` - 403 when user is inactive
- ✅ `test_get_my_school_api_documented` - OpenAPI documentation check

### Test Fixtures
- `test_school` - Creates a test school in database
- `test_user` - Creates a test user with hashed password
- `auth_token` - Generates JWT token for test user
- `authenticated_client` - Test client with authentication override

### Running Tests
```bash
cd backend
pytest school_service/tests/test_dashboard_api.py -v
```

## Time Estimate

6-8 hours

## Notes

- Ensure proper authentication middleware
- Verify authorization (user can only access their school)
- Consider caching school data if frequently accessed
- Log access for security auditing

