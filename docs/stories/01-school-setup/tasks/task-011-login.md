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

1. [ ] Login page route exists at `/login`
2. [ ] POST `/api/v1/auth/login` endpoint exists
3. [ ] Login form component created
4. [ ] Form includes: email, password
5. [ ] Form validation works
6. [ ] Login API call works
7. [ ] JWT token stored after successful login
8. [ ] Redirect to dashboard after login
9. [ ] Error messages displayed for invalid credentials
10. [ ] "Remember me" option (optional)

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
@router.post("/login")
async def login(credentials: LoginCredentials):
    user = await user_service.authenticate(
        credentials.email,
        credentials.password
    )
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": user.id})
    return {"access_token": token, "token_type": "bearer", "user": user}
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

- [ ] Code written and follows standards
- [ ] Unit tests written and passing
- [ ] Integration tests for login flow
- [ ] Frontend component tests
- [ ] Authentication flow works end-to-end
- [ ] Error handling comprehensive
- [ ] Code reviewed
- [ ] Tested in browser

## Time Estimate

6-8 hours

## Notes

- Store JWT token securely (consider HTTP-only cookies)
- Implement token refresh if needed
- Add rate limiting to prevent brute force
- Log login attempts for security
- Consider adding "Forgot Password" link (future phase)

