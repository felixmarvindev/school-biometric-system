# Task 074: Bulk Enrollment API

## Story/Phase
- **Story**: Story 04: Automated Enrollment
- **Phase**: Phase 5: Bulk Enrollment

## Description

Create API endpoint and service to handle bulk enrollment of multiple students sequentially.

## Type
- [x] Backend
- [ ] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Duration Estimate
2 days

## Prerequisites

- ✅ Phase 4 complete (single enrollment working)
- ✅ Enrollment service working

## Acceptance Criteria

1. [ ] POST `/api/v1/enrollment/bulk` endpoint created
2. [ ] Endpoint accepts: student_ids[], device_id, finger_id
3. [ ] Enrollments processed sequentially
4. [ ] Progress tracked for each enrollment
5. [ ] Summary returned with success/failure counts
6. [ ] Failed enrollments don't stop batch
7. [ ] Bulk enrollment session tracked

## Implementation Details

### Backend Changes

1. **backend/device_service/api/routes/enrollment.py**
   - Add POST `/bulk` endpoint

2. **backend/device_service/services/enrollment_service.py**
   - Add `bulk_enroll()` method
   - Add progress tracking

3. **backend/shared/schemas/enrollment.py**
   - Add BulkEnrollmentRequest schema
   - Add BulkEnrollmentResponse schema

### Key Code Patterns

```python
@router.post(
    "/bulk",
    response_model=BulkEnrollmentResponse,
    summary="Bulk enrollment",
    description="Enroll multiple students sequentially on a device.",
)
async def bulk_enroll(
    request: BulkEnrollmentRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Bulk enroll multiple students."""
    enrollment_service = EnrollmentService(db)
    
    results = await enrollment_service.bulk_enroll(
        student_ids=request.student_ids,
        device_id=request.device_id,
        finger_id=request.finger_id,
        school_id=current_user.school_id,
    )
    
    return BulkEnrollmentResponse(
        total=len(request.student_ids),
        successful=sum(1 for r in results if r['status'] == 'completed'),
        failed=sum(1 for r in results if r['status'] == 'failed'),
        results=results,
    )
```

## Testing

### Manual Testing

1. **Bulk Enrollment**
   - Call bulk enrollment API
   - ✅ Verify enrollments process sequentially
   - ✅ Verify summary returned

## Definition of Done

- [ ] Bulk enrollment API created
- [ ] Sequential processing works
- [ ] Progress tracking works
- [ ] Summary returned

## Next Task

**Task 075: Bulk Enrollment UI** - Create frontend UI for bulk enrollment.
