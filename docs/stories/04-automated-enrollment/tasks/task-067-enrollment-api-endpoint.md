# Task 067: Enrollment API Endpoint

## Story/Phase
- **Story**: Story 04: Automated Enrollment
- **Phase**: Phase 2: Device Control

## Description

Create REST API endpoint (`POST /api/v1/enrollment/start`) to start enrollment from the frontend.

## Type
- [x] Backend
- [ ] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Duration Estimate
1 day

## Prerequisites

- ✅ Task 066 complete (enrollment command handler)
- ✅ FastAPI routing working

## Acceptance Criteria

1. [ ] POST `/api/v1/enrollment/start` endpoint created
2. [ ] Endpoint accepts: student_id, device_id, finger_id
3. [ ] Endpoint validates input
4. [ ] Endpoint calls enrollment service
5. [ ] Endpoint returns enrollment session info
6. [ ] Error responses are clear and helpful
7. [ ] Authentication required
8. [ ] Authorization checks (school_id)
9. [ ] API documented (OpenAPI/Swagger)

## Implementation Details

### Backend Changes

1. **backend/device_service/api/routes/enrollment.py**
   - Create enrollment router
   - Add POST `/start` endpoint
   - Add error handling
   - Add authentication/authorization

2. **backend/shared/schemas/enrollment.py**
   - Add EnrollmentStartRequest schema
   - Add EnrollmentStartResponse schema

3. **backend/device_service/main.py**
   - Include enrollment router

### Key Code Patterns

```python
# backend/device_service/api/routes/enrollment.py
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from shared.schemas.user import UserResponse
from shared.schemas.enrollment import EnrollmentStartRequest, EnrollmentStartResponse
from device_service.api.dependencies import get_current_user, get_db
from device_service.services.enrollment_service import EnrollmentService

router = APIRouter(prefix="/api/v1/enrollment", tags=["enrollment"])

@router.post(
    "/start",
    response_model=EnrollmentStartResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start enrollment",
    description="""
    Start fingerprint enrollment for a student on a device.
    
    This endpoint:
    1. Validates student and device exist
    2. Checks device is online
    3. Creates enrollment session
    4. Sends enrollment command to device
    5. Returns session information
    """,
    responses={
        201: {"description": "Enrollment started successfully"},
        400: {"description": "Invalid request"},
        404: {"description": "Student or device not found"},
        503: {"description": "Device is offline"},
    },
)
async def start_enrollment(
    request: EnrollmentStartRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Start enrollment for a student."""
    enrollment_service = EnrollmentService(db)
    
    try:
        enrollment_session = await enrollment_service.start_enrollment(
            student_id=request.student_id,
            device_id=request.device_id,
            finger_id=request.finger_id,
            school_id=current_user.school_id,
        )
        
        return EnrollmentStartResponse(
            session_id=enrollment_session.session_id,
            student_id=enrollment_session.student_id,
            device_id=enrollment_session.device_id,
            finger_id=enrollment_session.finger_id,
            status=enrollment_session.status,
            started_at=enrollment_session.started_at,
        )
        
    except DeviceOfflineError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except EnrollmentError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
```

## Testing

### Manual Testing

1. **API Call**
   - Call POST `/api/v1/enrollment/start`
   - ✅ Verify returns 201 with session info
   - ✅ Verify enrollment session created in DB

2. **Error Cases**
   - Call with offline device
   - ✅ Verify returns 503
   - ✅ Verify error message is clear

## Definition of Done

- [ ] API endpoint created
- [ ] Input validation works
- [ ] Error handling works
- [ ] Authentication/authorization works
- [ ] API documented
- [ ] Tests pass

## Next Task

**Task 068: Frontend Enrollment API Integration** - Connect frontend form to enrollment API.
