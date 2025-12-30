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

1. [x] `AdminAccountFormSimple` reusable component created (can be used independently)
2. [x] Form appears as Step 2 in registration flow
3. [x] Form includes: first name, last name, email, password, confirm password
4. [x] Password strength indicator works with animated progress bar
5. [x] Password requirements validated (uppercase, lowercase, number, special char, min 8 chars)
6. [x] Password confirmation validation works
7. [x] Password visibility toggle works (eye icon)
8. [x] Form submission sends both school and admin data in single API call
9. [x] Success screen shown after account creation (displays both school and admin info)
10. [x] Automatic redirect to login page after 3 seconds
11. [x] Field-level error handling implemented
12. [x] Form is accessible and responsive
13. [x] Component is reusable for future admin creation features

## Technical Details

### Files to Create/Modify

```
frontend/components/features/auth/AdminAccountFormSimple.tsx (reusable component)
frontend/app/(auth)/register/page.tsx (two-step registration flow)
frontend/lib/api/schools.ts (combined registration endpoint)
frontend/lib/validations/school.ts (combined validation schema)
frontend/lib/validations/user.ts (admin account validation)
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

- Task 004 (User model and service must exist)
- Task 002 (Combined registration API endpoint)
- Framer Motion for animations
- Zod for validation
- shadcn/ui components (Button, Input, Label, Alert)

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

- [x] Code written and follows standards
- [x] Component is reusable (can be used independently)
- [ ] Component tests written and passing
- [x] Password strength indicator works with real-time updates
- [x] Form validation works correctly (client and server)
- [x] Transaction rollback tested (if admin creation fails, school is not created)
- [x] Response validation before commit (prevents inconsistent state)
- [x] Responsive design verified
- [x] Accessibility verified
- [x] Code reviewed
- [x] Tested in browser

## Time Estimate

6-8 hours

## Notes

- Password strength indicator should be visual and clear
- Show password requirements clearly
- Consider password visibility toggle
- Ensure secure password transmission (HTTPS)

