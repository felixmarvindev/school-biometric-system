# Task 011: Login Page and Authentication Flow

## Story/Phase
- **Story**: Story 01: School Setup
- **Phase**: Phase 3: Dashboard Setup (Prerequisite)

## Description

Create the login page and authentication flow that allows admins to log in and access the dashboard.

## Type
- [x] Backend
- [x] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Acceptance Criteria

1. [ ] Login page route exists at `/login` (Frontend)
2. [x] POST `/api/v1/auth/login` endpoint exists (Backend ✅)
3. [x] POST `/api/v1/auth/login/json` endpoint exists (Backend ✅)
4. [ ] Login form component created (Frontend)
5. [ ] Form includes: email, password (Frontend)
6. [x] Form validation works (Backend ✅ - tested)
7. [x] Login API call works (Backend ✅ - tested)
8. [ ] JWT token stored after successful login (Frontend)
9. [ ] Redirect to dashboard after login (Frontend)
10. [x] Error messages displayed for invalid credentials (Backend ✅ - tested)
11. [ ] "Remember me" option (optional) (Frontend)

## Technical Details

### Files to Create/Modify

```
frontend/app/(auth)/login/page.tsx
frontend/app/components/features/auth/LoginForm.tsx
frontend/app/lib/api/auth.ts
backend/school_service/api/routes/auth.py (add login endpoint)
frontend/app/lib/store/authStore.ts (Zustand store)
```

### Key Code Patterns

```typescript
// components/features/auth/LoginForm.tsx
'use client';

import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';

export function LoginForm() {
  const router = useRouter();
  const { login } = useAuthStore();

  const onSubmit = async (data: LoginFormData) => {
    try {
      const response = await authApi.login(data);
      login(response.token, response.user);
      router.push('/dashboard');
    } catch (error) {
      // Show error message
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      {/* Email and password fields */}
    </form>
  );
}

// backend routes/auth.py
@router.post("/login/json")
async def login_json(login_data: UserLogin):
    user = await user_service.authenticate_user(
        login_data.email,
        login_data.password
    )
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    # Token includes user details (source of truth)
    token = create_access_token({
        "sub": str(user.id),
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "school_id": user.school_id,
        "role": user.role,
    })
    return {"access_token": token, "token_type": "bearer"}
```

### Dependencies

- Task 004 (User model and authentication must exist)
- JWT token generation working
- Password verification working

## Visual Testing

### Before State
- No login page exists
- Cannot authenticate users

### After State
- Can navigate to `/login`
- Can log in with credentials
- Redirected to dashboard after login

### Testing Steps

1. Navigate to `/login`
2. Enter invalid credentials - verify error
3. Enter valid credentials - verify login and redirect
4. Test token storage
5. Test protected routes require login

## Definition of Done

- [x] Code written and follows standards (Backend ✅)
- [x] Unit tests written and passing (Backend ✅ - `test_auth_login_api.py`)
- [x] Integration tests for login flow (Backend ✅)
- [ ] Frontend component tests (Frontend)
- [ ] Authentication flow works end-to-end (Frontend + Backend integration)
- [x] Error handling comprehensive (Backend ✅ - tested)
- [ ] Code reviewed
- [ ] Tested in browser (Frontend)

## Backend Test Coverage

Comprehensive test suite created in `backend/school_service/tests/test_auth_login_api.py`:

### Test Cases (20 tests total)

#### JSON Login Endpoint (`/api/v1/auth/login/json`)
- ✅ `test_login_json_success` - Successful login with valid credentials
- ✅ `test_login_json_invalid_email` - 401 for non-existent email
- ✅ `test_login_json_invalid_password` - 401 for wrong password
- ✅ `test_login_json_inactive_user` - 401 for inactive user
- ✅ `test_login_json_missing_email` - 422 for missing email field
- ✅ `test_login_json_missing_password` - 422 for missing password field
- ✅ `test_login_json_invalid_email_format` - 422 for invalid email format
- ✅ `test_login_json_case_insensitive_email` - Email matching is case-insensitive

#### Form Login Endpoint (`/api/v1/auth/login`)
- ✅ `test_login_form_success` - Successful login with form data
- ✅ `test_login_form_invalid_credentials` - 401 for invalid credentials
- ✅ `test_login_form_missing_fields` - 422 for missing fields

#### Token Validation
- ✅ `test_login_token_contains_user_info` - Token contains user ID, email, school_id, role
- ✅ `test_login_token_expiration` - Token has expiration claim

#### API Documentation
- ✅ `test_login_json_api_documented` - OpenAPI docs for JSON endpoint
- ✅ `test_login_form_api_documented` - OpenAPI docs for form endpoint

#### Edge Cases
- ✅ `test_login_empty_request_body` - 422 for empty body
- ✅ `test_login_deleted_user` - 401 for soft-deleted user
- ✅ `test_login_both_endpoints_same_result` - Both endpoints return consistent format

### Test Fixtures
- `test_school` - Creates a test school in database
- `test_user` - Creates an active test user with hashed password
- `inactive_user` - Creates an inactive test user

### Running Tests
```bash
cd backend
pytest school_service/tests/test_auth_login_api.py -v
```

## Time Estimate

6-8 hours

## Notes

- Store JWT token securely (consider HTTP-only cookies)
- Implement token refresh if needed
- Add rate limiting to prevent brute force
- Log login attempts for security
- Consider adding "Forgot Password" link (future phase)

