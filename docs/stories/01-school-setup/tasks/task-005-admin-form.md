# Task 005: Admin Account Form

## Story/Phase
- **Story**: Story 01: School Setup
- **Phase**: Phase 2: Admin User Creation

## Description

Create the admin account creation form component that appears after school registration, with password strength validation and confirmation.

## Type
- [ ] Backend
- [x] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Acceptance Criteria

1. [ ] Admin account form component created
2. [ ] Form appears after school registration
3. [ ] Form includes: full name, email, password, confirm password
4. [ ] Password strength indicator works
5. [ ] Password requirements are displayed
6. [ ] Password confirmation validation works
7. [ ] Form submission creates user account
8. [ ] Success message shown after account creation
9. [ ] Form is accessible and responsive

## Technical Details

### Files to Create/Modify

```
frontend/app/components/features/auth/AdminAccountForm.tsx
frontend/app/(auth)/register/page.tsx (update to include form)
frontend/app/lib/api/auth.ts
frontend/app/lib/validations/user.ts
```

### Key Code Patterns

```typescript
// components/features/auth/AdminAccountForm.tsx
'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';

const passwordSchema = z.object({
  password: z.string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Password must contain an uppercase letter')
    .regex(/[a-z]/, 'Password must contain a lowercase letter')
    .regex(/[0-9]/, 'Password must contain a number'),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

export function AdminAccountForm({ schoolId }: { schoolId: number }) {
  const [passwordStrength, setPasswordStrength] = useState(0);
  
  // Calculate password strength
  // Submit form
  // Show success/error
}
```

### Dependencies

- Task 004 (User model and API must exist)
- React Hook Form
- Zod
- shadcn/ui components

## Visual Testing

### Before State
- No admin account form exists
- Cannot create admin accounts from frontend

### After State
- Form appears after school registration
- Can create admin account
- Password strength indicator works

### Testing Steps

1. Complete school registration
2. See admin account form
3. Enter weak password - verify strength indicator
4. Enter mismatched passwords - verify error
5. Submit valid data - verify success

## Definition of Done

- [ ] Code written and follows standards
- [ ] Component tests written and passing
- [ ] Password strength indicator works
- [ ] Form validation works correctly
- [ ] Responsive design verified
- [ ] Accessibility verified
- [ ] Code reviewed
- [ ] Tested in browser

## Time Estimate

6-8 hours

## Notes

- Password strength indicator should be visual and clear
- Show password requirements clearly
- Consider password visibility toggle
- Ensure secure password transmission (HTTPS)

