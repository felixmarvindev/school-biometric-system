# Task 010: Settings UI

## Story/Phase
- **Story**: Story 01: School Setup
- **Phase**: Phase 4: Settings and Configuration

## Description

Create the settings page component that allows admins to update their school's information.

## Type
- [ ] Backend
- [x] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Acceptance Criteria

1. [x] Settings page route exists at `/dashboard/settings`
2. [x] Settings page is protected (requires authentication via layout)
3. [x] Settings form component created
4. [x] Form is pre-populated with current school data
5. [x] School code field is read-only/disabled
6. [x] Form validation works
7. [x] Save button updates school information
8. [x] Cancel button resets form
9. [x] Success message shown after update
10. [x] Form is responsive and accessible

## Technical Details

### Files to Create/Modify

```
frontend/app/(dashboard)/dashboard/settings/page.tsx ✅
frontend/app/(dashboard)/layout.tsx ✅ (shared layout for all dashboard routes)
frontend/lib/api/schools.ts (updateMySchool function) ✅
frontend/components/layouts/DashboardLayout.tsx ✅ (reusable layout component)
```

### Key Code Patterns

```typescript
// components/features/settings/SchoolSettingsForm.tsx
'use client';

import { useForm } from 'react-hook-form';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

export function SchoolSettingsForm() {
  const queryClient = useQueryClient();
  
  const { data: school } = useQuery({
    queryKey: ['school', 'me'],
    queryFn: () => schoolsApi.getMySchool(),
  });

  const form = useForm({
    defaultValues: school,
  });

  const updateMutation = useMutation({
    mutationFn: schoolsApi.updateMySchool,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['school', 'me'] });
      // Show success message
    },
  });

  return (
    <form onSubmit={form.handleSubmit(updateMutation.mutate)}>
      <Input
        {...form.register('code')}
        disabled
        label="School Code (cannot be changed)"
      />
      {/* Other fields */}
      <Button type="submit">Save Changes</Button>
      <Button type="button" onClick={() => form.reset()}>Cancel</Button>
    </form>
  );
}
```

### Dependencies

- Task 009 (Settings API must exist)
- Task 007 (Dashboard must exist for navigation)
- TanStack Query
- React Hook Form

## Visual Testing

### Before State
- No settings page exists
- Cannot update school information from frontend

### After State
- Can navigate to `/settings`
- See form with current data
- Can update school information
- Code field is disabled

### Testing Steps

1. Navigate to settings page
2. Verify form is pre-populated
3. Verify code field is disabled
4. Update information and save
5. Verify success message
6. Verify dashboard shows updated data

## Definition of Done

- [x] Code written and follows standards
- [x] Form validation works (client-side and server-side)
- [x] Update functionality works (integrated with PUT /api/v1/schools/me)
- [x] Responsive design verified
- [x] Accessibility verified (ARIA labels, keyboard navigation)
- [x] Uses Next.js layout structure (app/(dashboard)/layout.tsx)
- [x] Success/error messages with animations
- [x] Loading states implemented
- [ ] Component tests written and passing
- [ ] Code reviewed
- [ ] Tested in browser

## Time Estimate

6-8 hours

## Notes

- Pre-populate form with current data
- Show clear indication that code cannot be changed
- Consider optimistic updates for better UX
- Add confirmation dialog if needed

