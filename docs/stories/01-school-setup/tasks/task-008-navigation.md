# Task 008: Navigation Menu

## Story/Phase
- **Story**: Story 01: School Setup
- **Phase**: Phase 3: Dashboard Setup

## Description

Create the navigation menu component that appears on all authenticated pages, providing access to different sections of the application.

## Type
- [ ] Backend
- [x] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Acceptance Criteria

1. [ ] Navigation menu component created
2. [ ] Menu appears on all authenticated pages
3. [ ] Menu includes: Dashboard, Students, Devices, Settings
4. [ ] Active page is highlighted
5. [ ] Menu is responsive (collapsible on mobile)
6. [ ] User info/logout button visible
7. [ ] Menu is accessible (keyboard navigation)
8. [ ] Menu styling is consistent

## Technical Details

### Files to Create/Modify

```
frontend/app/components/layout/Navigation.tsx
frontend/app/components/layout/AppLayout.tsx
frontend/app/(dashboard)/layout.tsx
```

### Key Code Patterns

```typescript
// components/layout/Navigation.tsx
'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';

const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: Home },
  { href: '/students', label: 'Students', icon: Users },
  { href: '/devices', label: 'Devices', icon: Fingerprint },
  { href: '/settings', label: 'Settings', icon: Settings },
];

export function Navigation() {
  const pathname = usePathname();
  
  return (
    <nav>
      {navItems.map((item) => (
        <Link
          key={item.href}
          href={item.href}
          className={cn(
            pathname === item.href && 'active'
          )}
        >
          {item.label}
        </Link>
      ))}
    </nav>
  );
}
```

### Dependencies

- Next.js App Router
- shadcn/ui components
- Authentication state

## Visual Testing

### Before State
- No navigation menu exists
- No way to navigate between pages

### After State
- Navigation menu visible on all pages
- Can navigate between sections
- Active page highlighted

### Testing Steps

1. Login and check navigation appears
2. Click each menu item - verify navigation works
3. Check active state highlights current page
4. Test responsive menu (mobile)
5. Test keyboard navigation

## Definition of Done

- [ ] Code written and follows standards
- [ ] Component tests written and passing
- [ ] Navigation works correctly
- [ ] Active state works
- [ ] Responsive design verified
- [ ] Accessibility verified
- [ ] Code reviewed
- [ ] Tested in browser

## Time Estimate

4-6 hours

## Notes

- Use Next.js Link for client-side navigation
- Consider using shadcn/ui sidebar component
- Mobile menu should be collapsible
- Add icons for better visual hierarchy

