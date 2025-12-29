# Task 007: Dashboard UI

## Story/Phase
- **Story**: Story 01: School Setup
- **Phase**: Phase 3: Dashboard Setup

## Description

Create the dashboard page component that displays school information, quick stats, and provides navigation to other features.

## Type
- [ ] Backend
- [x] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Acceptance Criteria

1. [ ] Dashboard page route exists at `/dashboard`
2. [ ] Dashboard is protected (requires authentication)
3. [ ] `SchoolDashboard` component created
4. [ ] School information card displays correctly
5. [ ] Quick stats cards show zeros (empty state)
6. [ ] Loading state shown while fetching data
7. [ ] Error state handled gracefully
8. [ ] Dashboard is responsive
9. [ ] Dashboard is accessible

## Technical Details

### Files to Create/Modify

```
frontend/app/(dashboard)/dashboard/page.tsx
frontend/app/components/features/dashboard/SchoolDashboard.tsx
frontend/app/components/features/dashboard/SchoolInfoCard.tsx
frontend/app/components/features/dashboard/QuickStats.tsx
frontend/app/lib/hooks/useAuth.ts
```

### Key Code Patterns

```typescript
// components/features/dashboard/SchoolDashboard.tsx
'use client';

import { useQuery } from '@tanstack/react-query';
import { SchoolInfoCard } from './SchoolInfoCard';
import { QuickStats } from './QuickStats';

export function SchoolDashboard() {
  const { data: school, isLoading, error } = useQuery({
    queryKey: ['school', 'me'],
    queryFn: () => schoolsApi.getMySchool(),
  });

  if (isLoading) return <DashboardSkeleton />;
  if (error) return <ErrorState />;

  return (
    <div className="space-y-6">
      <h1>Dashboard</h1>
      <SchoolInfoCard school={school} />
      <QuickStats />
    </div>
  );
}
```

### Dependencies

- Task 006 (Dashboard API must exist)
- Task 008 (Navigation menu)
- TanStack Query
- Authentication state management

## Visual Testing

### Before State
- No dashboard page exists
- Cannot view school information after login

### After State
- Can navigate to `/dashboard`
- See school information
- See quick stats (empty state)
- See navigation menu

### Testing Steps

1. Login and verify redirect to dashboard
2. Check school information displays correctly
3. Verify quick stats show zeros
4. Test responsive design
5. Test without authentication - verify redirect

## Definition of Done

- [ ] Code written and follows standards
- [ ] Component tests written and passing
- [ ] Loading states work
- [ ] Error states handled
- [ ] Responsive design verified
- [ ] Accessibility verified
- [ ] Code reviewed
- [ ] Tested in browser

## Time Estimate

8-10 hours

## Notes

- Use TanStack Query for data fetching
- Implement proper loading and error states
- Empty states should guide users on next steps
- Consider adding skeleton loaders for better UX

