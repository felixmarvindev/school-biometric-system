# Task 002: School Registration API

## Story/Phase
- **Story**: Story 01: School Setup
- **Phase**: Phase 1: School Registration

## Description

Create the API endpoint for school registration with validation, error handling, and proper response formatting.

## Type
- [x] Backend
- [ ] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Acceptance Criteria

1. [x] POST `/api/v1/schools/register` endpoint exists
2. [x] Endpoint accepts school registration data
3. [x] Input validation works (required fields, formats)
4. [x] School code uniqueness is validated
5. [x] Successful registration returns 201 with school data
6. [x] Validation errors return 422 with clear messages
7. [x] Duplicate code returns 409 with specific error
8. [x] API endpoint is documented (OpenAPI)

## Technical Details

### Files to Create/Modify

```
backend/school_service/api/routes/schools.py
backend/shared/schemas/school.py
backend/school_service/services/school_service.py
```

### Key Code Patterns

```python
# schemas/school.py
from pydantic import BaseModel, EmailStr, Field, validator

class SchoolCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    code: str = Field(..., min_length=3, max_length=50, regex=r'^[A-Z0-9-]+$')
    address: str | None = Field(None, max_length=500)
    phone: str | None = Field(None, regex=r'^\+?[0-9]{10,15}$')
    email: EmailStr | None = None

# routers/schools.py
from fastapi import APIRouter, HTTPException, status
from backend.shared.schemas.school import SchoolCreate, SchoolResponse

router = APIRouter(prefix="/schools", tags=["schools"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_school(school_data: SchoolCreate):
    # Check for duplicate code
    existing = await school_service.get_by_code(school_data.code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"School code '{school_data.code}' already exists"
        )
    
    # Create school
    school = await school_service.create(school_data)
    return SchoolResponse.from_orm(school)
```

### Dependencies

- Task 001 (School model must exist)
- FastAPI installed
- Pydantic for validation

## Visual Testing

### Before State
- API endpoint doesn't exist
- Cannot register schools via API

### After State
- Can POST to `/api/v1/schools/register`
- Receives proper responses
- Validation errors are clear

### Testing Steps

1. Test with valid data: POST valid school data, verify 201 response
2. Test required fields: POST without name, verify 422 error
3. Test duplicate code: POST with existing code, verify 409 error
4. Test email validation: POST with invalid email, verify 422 error
5. Check OpenAPI docs: Verify endpoint appears in `/docs`

## Definition of Done

- [x] Code written and follows standards
- [x] Unit tests written and passing
- [x] Integration tests written and passing
- [x] API documented in OpenAPI/Swagger
- [x] Error handling comprehensive
- [ ] Code reviewed
- [x] Tested with Postman/curl

## Time Estimate

6-8 hours

## Notes

- Use HTTP status codes correctly (201 for creation, 409 for conflict)
- Error messages should be user-friendly
- Consider rate limiting for registration endpoint
- Log registration attempts for security

