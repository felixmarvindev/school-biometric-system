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

1. [ ] GET `/api/v1/schools/me` endpoint exists
2. [ ] Endpoint requires authentication (JWT token)
3. [ ] Endpoint returns current user's school data
4. [ ] Authorization ensures user can only see their school
5. [ ] Returns 401 if not authenticated
6. [ ] Returns 404 if school not found
7. [ ] Response includes school information
8. [ ] API endpoint is documented

## Technical Details

### Files to Create/Modify

```
backend/school_service/api/routes/schools.py (add GET /me endpoint)
backend/school_service/api/dependencies.py (add get_current_user)
backend/school_service/core/security.py (add token validation)
```

### Key Code Patterns

```python
# dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = await user_service.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# routes/schools.py
@router.get("/me", response_model=SchoolResponse)
async def get_my_school(
    current_user: User = Depends(get_current_user)
):
    school = await school_service.get_by_id(current_user.school_id)
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    return SchoolResponse.from_orm(school)
```

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

- [ ] Code written and follows standards
- [ ] Unit tests written and passing
- [ ] Integration tests with authentication
- [ ] Authorization verified
- [ ] API documented
- [ ] Error handling comprehensive
- [ ] Code reviewed
- [ ] Tested with Postman/curl

## Time Estimate

6-8 hours

## Notes

- Ensure proper authentication middleware
- Verify authorization (user can only access their school)
- Consider caching school data if frequently accessed
- Log access for security auditing

