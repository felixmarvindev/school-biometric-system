# Phase 4: Settings and Configuration

## Goal

Allow school admins to update their school's information and manage basic settings.

## Duration Estimate

2-3 days

## Prerequisites

- ✅ Phase 3 complete (dashboard working)
- ✅ School update API endpoint ready

## Technical Components

### Backend Changes

- [x] Create PUT `/api/v1/schools/me` endpoint
- [x] Add update validation
- [x] Prevent school code changes (immutable)
- [x] Support clearing optional fields (None values)
- [x] Create unit tests
- [x] Create integration tests

### Frontend Changes

- [x] Create settings page (`/dashboard/settings`)
- [x] Create settings form component
- [x] Pre-populate form with current data
- [x] Add form validation
- [x] Add save/cancel buttons
- [x] Show success/error messages with animations
- [x] Add loading states
- [x] Use Next.js layout structure

### DevOps/Infrastructure

- [ ] (No changes needed)

## Tasks Breakdown

See [tasks/](tasks/) folder:
- [Task 009: Settings API](tasks/task-009-settings-api.md)
- [Task 010: Settings UI](tasks/task-010-settings-ui.md)

## Visual Checkpoints

At the end of this phase, you should be able to:

### 1. Access Settings
- Click "Settings" in navigation
- See settings page
- See form pre-populated with current school data

### 2. Update Information
- Edit school name, address, phone, email
- See school code is read-only (cannot edit)
- Click "Save Changes"
- See success message
- See updated data reflected immediately

### 3. Cancel Changes
- Make changes to form
- Click "Cancel"
- See form reset to original values

### Success Screenshots

1. **Settings Page** - Form with current school data
2. **Read-only Code Field** - School code displayed but disabled
3. **Success Message** - Green banner after successful update

## Testing This Phase

### Manual Testing Steps

1. **Update Flow**
   - Navigate to settings
   - Update school name
   - Save changes
   - ✅ Verify success message
   - ✅ Verify dashboard shows updated name

2. **Validation**
   - Try to clear required fields
   - ✅ Verify validation errors
   - Try invalid email format
   - ✅ Verify email validation

3. **Immutable Code**
   - Try to edit school code field
   - ✅ Verify field is disabled/read-only

### Automated Tests

- [ ] Unit tests for update endpoint
- [ ] Integration tests
- [ ] Frontend form tests
- [ ] E2E test for update flow

## Demo Script for This Phase

### Demonstration (1-2 minutes)

1. **Show Settings** (30 seconds)
   - Navigate to settings
   - Show form with current data
   - Point out read-only school code

2. **Update Information** (1 minute)
   - Change school phone number
   - Save changes
   - Show success message
   - Navigate to dashboard to show updated info

### Talking Points

- "Admins can keep their school information up to date"
- "School code remains stable for system integrity"
- "Changes are saved immediately"

## Story Complete

This completes Story 01: School Setup. Schools can now:
- ✅ Register in the system
- ✅ Create admin accounts
- ✅ Log in and view dashboard
- ✅ Update school information

**Next Story**: Story 02: Student Management - Now that schools are set up, we can start adding students.

