# Task 068: Frontend Enrollment API Integration

## Story/Phase
- **Story**: Story 04: Automated Enrollment
- **Phase**: Phase 2: Device Control

## Description

Connect the enrollment form to the backend API endpoint and handle API responses (success and errors).

## Type
- [ ] Backend
- [x] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Duration Estimate
1 day

## Prerequisites

- ✅ Task 067 complete (enrollment API endpoint)
- ✅ Task 064 complete (enrollment form)

## Acceptance Criteria

1. [ ] API client function created (`startEnrollment()`)
2. [ ] Form submission calls API
3. [ ] Loading state shown during API call
4. [ ] Success response handled
5. [ ] Error responses handled gracefully
6. [ ] Error messages displayed to user
7. [ ] Success redirects to progress screen (placeholder for Phase 3)

## Implementation Details

### Frontend Changes

1. **frontend/lib/api/enrollment.ts**
   - Create enrollment API client
   - Add `startEnrollment()` function
   - Add error handling

2. **frontend/app/(dashboard)/dashboard/enrollment/page.tsx**
   - Integrate API call
   - Add loading/error states
   - Handle API responses

### Key Code Patterns

```typescript
// frontend/lib/api/enrollment.ts
import axios from '@/lib/api/axios-instance';

export interface EnrollmentStartRequest {
  student_id: number;
  device_id: number;
  finger_id: number;
}

export interface EnrollmentStartResponse {
  session_id: string;
  student_id: number;
  device_id: number;
  finger_id: number;
  status: string;
  started_at: string;
}

export async function startEnrollment(
  request: EnrollmentStartRequest
): Promise<EnrollmentStartResponse> {
  const response = await axios.post<EnrollmentStartResponse>(
    '/api/v1/enrollment/start',
    request
  );
  return response.data;
}
```

```typescript
// frontend/app/(dashboard)/dashboard/enrollment/page.tsx
const handleStartEnrollment = async () => {
  if (!isFormValid) return;
  
  setIsSubmitting(true);
  setError('');
  
  try {
    const response = await startEnrollment({
      student_id: selectedStudent!.id,
      device_id: selectedDevice!.id,
      finger_id: selectedFinger,
    });
    
    // TODO: Phase 3 - Navigate to progress screen
    toast.success('Enrollment started successfully');
    console.log('Enrollment session:', response.session_id);
    
  } catch (err: unknown) {
    if (err instanceof Error) {
      setError(err.message);
      toast.error(err.message);
    } else {
      setError('Failed to start enrollment. Please try again.');
      toast.error('Failed to start enrollment');
    }
  } finally {
    setIsSubmitting(false);
  }
};
```

## Testing

### Manual Testing

1. **Form Submission**
   - Fill form and submit
   - ✅ Verify API call made
   - ✅ Verify loading state shown
   - ✅ Verify success handled

2. **Error Handling**
   - Submit with offline device
   - ✅ Verify error message shown
   - ✅ Verify error is user-friendly

## Definition of Done

- [ ] API client function created
- [ ] Form connected to API
- [ ] Loading states work
- [ ] Error handling works
- [ ] Success handling works
- [ ] No console errors

## Next Phase

**Phase 3: Real-time Progress** - Now that enrollment can be started, we need to add WebSocket-based real-time progress updates.
