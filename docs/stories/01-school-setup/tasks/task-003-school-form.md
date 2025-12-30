# Task 003: School Registration Form

## Story/Phase
- **Story**: Story 01: School Setup
- **Phase**: Phase 1: School Registration

## Description

Create the frontend registration form component with validation, error handling, and user-friendly UI for school registration.

## Type
- [ ] Backend
- [x] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Acceptance Criteria

1. [x] Registration page route exists at `/register`
2. [x] `SchoolRegistrationFormSimple` reusable component created
3. [x] Two-step registration flow implemented (school info → admin account)
4. [x] Step progress indicator component created
5. [x] Step header component with animations created
6. [x] Form includes all required fields (name, code) and optional fields (address, phone, email)
7. [x] Client-side validation works for all fields
8. [x] Form submission sends both school and admin data in single API call
9. [x] Loading state shown during submission
10. [x] Success screen component displays both school and admin information
11. [x] Error messages displayed for validation failures (field-level)
12. [x] Form is responsive (desktop, tablet, mobile)
13. [x] Form is accessible (keyboard navigation, screen readers)
14. [x] Placeholder text added to all form fields

## Technical Details

### Files to Create/Modify

```
frontend/app/(auth)/register/page.tsx
frontend/components/features/school/SchoolRegistrationFormSimple.tsx
frontend/components/features/auth/AdminAccountFormSimple.tsx
frontend/components/features/auth/StepProgressIndicator.tsx
frontend/components/features/auth/StepHeader.tsx
frontend/components/features/auth/RegistrationSuccessScreen.tsx
frontend/lib/api/schools.ts
frontend/lib/validations/school.ts
```

### Key Code Patterns

```typescript
// components/features/school/SchoolRegistrationForm.tsx
'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';

const schoolSchema = z.object({
  name: z.string().min(1, 'School name is required').max(200),
  code: z.string()
    .min(3, 'Code must be at least 3 characters')
    .max(50, 'Code must be less than 50 characters')
    .regex(/^[A-Z0-9-]+$/, 'Code can only contain uppercase letters, numbers, and hyphens'),
  address: z.string().max(500).optional(),
  phone: z.string().regex(/^\+?[0-9]{10,15}$/, 'Invalid phone number').optional(),
  email: z.string().email('Invalid email address').optional().or(z.literal('')),
});

export function SchoolRegistrationForm() {
  const form = useForm({
    resolver: zodResolver(schoolSchema),
  });

  const onSubmit = async (data: z.infer<typeof schoolSchema>) => {
    // Call API
    // Show success/error
  };

  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      {/* Form fields */}
    </form>
  );
}
```

### Dependencies

- Task 002 (API endpoint must exist - combined school + admin registration)
- Framer Motion for animations
- Zod for validation
- shadcn/ui components (Button, Input, Textarea, Label, Card, Alert)

## Visual Testing

### Before State
- No registration page exists
- Cannot register schools from frontend

### After State
- Can navigate to `/register`
- See clean registration form
- Can submit form and see results

### Testing Steps

1. Navigate to `/register`
2. Try submitting empty form - verify validation errors
3. Fill form with valid data - verify submission works
4. Test on different screen sizes - verify responsive design
5. Test keyboard navigation - verify accessibility

## Definition of Done

- [x] Code written and follows standards
- [ ] Component tests written and passing
- [x] Form validation works correctly
- [x] Responsive design verified
- [x] Accessibility verified
- [x] Error handling comprehensive
- [x] Code reviewed
- [x] Tested in browser

## Time Estimate

6-8 hours

## Notes

- Use shadcn/ui components for consistency
- Ensure form is accessible (ARIA labels, keyboard navigation)
- Consider adding form field hints/help text
- Make error messages clear and actionable

