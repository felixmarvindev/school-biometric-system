# Phase 3: Dashboard Setup

## Goal

Provide a personalized dashboard for school admins after login, showing school information and navigation to other features.

## Duration Estimate

3-4 days

## Prerequisites

- ✅ Phase 2 complete (admin account creation working)
- ✅ Authentication system working (login endpoint)
- ✅ JWT token generation and validation
- ✅ Frontend authentication state management

## Technical Components

### Backend Changes

- [ ] Create GET `/api/v1/schools/me` endpoint
- [ ] Add authentication middleware
- [ ] Create school data serializer
- [ ] Add authorization (ensure user can only see their school)
- [ ] Create unit tests for endpoint
- [ ] Create integration tests with authentication

### Frontend Changes

- [ ] Create dashboard page route (`/dashboard`)
- [ ] Create authentication guard/protection
- [ ] Create `SchoolDashboard` component
- [ ] Create `SchoolInfoCard` component
- [ ] Create navigation menu component
- [ ] Create empty state components
- [ ] Add loading state
- [ ] Add error handling
- [ ] Create layout wrapper with navigation

### DevOps/Infrastructure

- [ ] Configure JWT token storage (HTTP-only cookies or localStorage)
- [ ] Set up protected route middleware

## Tasks Breakdown

See [tasks/](tasks/) folder:
- [Task 006: Dashboard API](tasks/task-006-dashboard-api.md)
- [Task 007: Dashboard UI](tasks/task-007-dashboard-ui.md)
- [Task 008: Navigation Menu](tasks/task-008-navigation.md)

## Visual Checkpoints

At the end of this phase, you should be able to:

### 1. Login and Redirect
- Enter credentials on login page
- Submit login form
- Be redirected to `/dashboard`
- See dashboard content

### 2. View Dashboard
- See school name and logo (if available)
- See school information card with:
  - School name
  - School code
  - Address
  - Contact information
- See navigation menu with links to:
  - Dashboard (current, highlighted)
  - Students (placeholder)
  - Devices (placeholder)
  - Settings
- See quick stats cards showing zeros:
  - Total Students: 0
  - Total Devices: 0
  - Today's Attendance: 0

### 3. Navigation
- Click navigation menu items
- See active state on current page
- Navigation works smoothly

### Success Screenshots

1. **Dashboard Layout** - Full dashboard with school info and navigation
2. **School Information Card** - Clean display of school details
3. **Empty States** - Empty state cards for future features
4. **Navigation Menu** - Clear navigation with active state

## Testing This Phase

### Manual Testing Steps

1. **Login Flow**
   - Enter valid credentials
   - Submit login form
   - ✅ Verify redirect to dashboard
   - ✅ Verify dashboard loads with school data

2. **Dashboard Display**
   - Check all school information displays correctly
   - Check navigation menu is visible
   - Check quick stats show zeros
   - ✅ Verify all data matches registered school

3. **Navigation**
   - Click each navigation item
   - ✅ Verify active state updates
   - ✅ Verify navigation doesn't break

4. **Authentication**
   - Try to access dashboard without login
   - ✅ Verify redirect to login
   - ✅ Verify protected routes work

### Automated Tests

- [ ] Unit tests for dashboard API endpoint
- [ ] Integration tests with authentication
- [ ] Frontend component tests
- [ ] E2E test for login → dashboard flow

## Demo Script for This Phase

### Demonstration (2-3 minutes)

1. **Login** (30 seconds)
   - Show login page
   - Enter credentials
   - Submit and show redirect

2. **Dashboard Tour** (1-2 minutes)
   - Show school information card
   - Explain what each stat represents
   - Show navigation menu
   - Explain empty states ("This is where students will appear")

3. **Navigation** (30 seconds)
   - Click through navigation items
   - Show active states
   - Explain where each section leads

### Talking Points

- "Admins see a personalized dashboard after login"
- "School information is prominently displayed"
- "Navigation makes all features easily accessible"
- "Empty states guide users on next steps"

### Expected Questions

**Q: Can admins customize the dashboard?**  
A: Not yet, but we can add customization in future phases.

**Q: What do the stats show?**  
A: Quick overview of key metrics. They'll populate as data is added.

**Q: Can multiple admins log in?**  
A: Currently one admin per school, but we'll add multi-admin support later.

## Next Phase

**Phase 4: Settings and Configuration** - Allow admins to update their school's information and manage account settings.

