# Story 01: School Setup - Acceptance Criteria

## Story-Level Acceptance Criteria

### School Registration
- [x] School can be registered through two-step web form
- [x] School code is unique across system
- [x] All required fields are validated (client and server)
- [x] Registration completes in < 2 seconds
- [x] Success screen appears after registration (shows both school and admin)
- [x] School data is stored in database
- [x] Registration uses atomic transaction (school + admin together)

### Admin Account Creation
- [x] Admin account is created as Step 2 in registration flow
- [x] Admin account form is reusable component
- [x] Password meets strength requirements (validated client and server)
- [x] Password strength indicator shows real-time feedback
- [x] Password is hashed before storage (bcrypt)
- [x] Admin is associated with school (school_id foreign key)
- [x] Account creation completes successfully
- [x] Both school and admin created in single atomic transaction
- [x] Transaction rolls back if admin creation fails (no orphaned school)
- [x] Response validation happens before commit (prevents inconsistent state)

### Dashboard Access
- [ ] Admin can log in with credentials
- [ ] Dashboard loads after successful login
- [ ] School information displays correctly
- [ ] Navigation menu is visible and functional
- [ ] Empty states show for future features

### Settings Management
- [ ] Admin can access settings page
- [ ] School information can be updated
- [ ] School code cannot be changed
- [ ] Updates save successfully
- [ ] Success feedback appears after update

## Phase 1: School Registration

### Visual Criteria
- [x] Registration form is accessible at `/register`
- [x] Two-step registration flow with progress indicator
- [x] Step 1: School information form
- [x] Step 2: Admin account form
- [x] Form fields are clearly labeled with placeholders
- [x] Required fields are marked with asterisk
- [x] Form has proper spacing and layout with gradient background
- [x] Error messages are visible and clear (field-level)
- [x] Success screen appears after submission (shows both school and admin)
- [x] Automatic redirect to login page after 3 seconds

### Functional Criteria
- [x] School name is required
- [x] School code is required and unique
- [x] Email format is validated (optional field)
- [x] Phone format is validated (optional field)
- [x] Form submission creates both school and admin in single API call
- [x] Database stores all fields correctly
- [x] Atomic transaction ensures both succeed or both fail

### Performance Criteria
- [ ] Form loads in < 500ms
- [ ] Form submission completes in < 2s
- [ ] Validation errors appear instantly

## Phase 2: Admin User Creation

### Visual Criteria
- [x] Admin form appears as Step 2 after school registration (Step 1)
- [x] Step progress indicator shows both steps
- [x] Step header with icon, title, and description
- [x] Password strength indicator is visible with animated progress bar
- [x] Password strength updates in real-time as user types
- [x] Password requirements validated (uppercase, lowercase, number, special char)
- [x] Password confirmation field validates match
- [x] Password visibility toggle (eye icon)
- [x] Error messages appear for validation failures (field-level)
- [x] "Back" button to return to Step 1
- [x] Success screen shows both school name and admin email

### Functional Criteria
- [x] First name is required
- [x] Last name is required
- [x] Email is required and validated
- [x] Email uniqueness validated (no duplicate admin emails)
- [x] Password meets minimum strength (8 chars, mixed case, numbers, special char)
- [x] Password confirmation must match
- [x] Password is hashed with bcrypt before storage
- [x] User record is created in database
- [x] User.school_id matches school.id
- [x] Both school and user created in single atomic transaction
- [x] Transaction rolls back if user creation fails
- [x] Response validation before commit prevents inconsistent state

### Security Criteria
- [ ] Password is never stored in plain text
- [ ] Password is hashed with salt
- [ ] Input is sanitized to prevent XSS

## Phase 3: Dashboard Setup

### Visual Criteria
- [ ] Dashboard is accessible at `/dashboard`
- [ ] School information card displays all school data
- [ ] Navigation menu is visible
- [ ] Quick stats cards show zeros
- [ ] Layout is responsive (desktop, tablet)
- [ ] Active navigation item is highlighted

### Functional Criteria
- [ ] Dashboard requires authentication
- [ ] School data loads correctly
- [ ] Navigation links work (even if pages don't exist yet)
- [ ] Empty states display appropriate messages
- [ ] Dashboard loads in < 1 second

### Data Criteria
- [ ] School name displays correctly
- [ ] School code displays correctly
- [ ] Address displays correctly
- [ ] Contact information displays correctly

## Phase 4: Settings and Configuration

### Visual Criteria
- [ ] Settings page is accessible at `/settings`
- [ ] Form is pre-populated with current data
- [ ] School code field is read-only
- [ ] Save button is visible
- [ ] Cancel button resets form
- [ ] Success message appears after save

### Functional Criteria
- [ ] School information can be updated
- [ ] School code cannot be changed
- [ ] Updates are validated
- [ ] Changes are saved to database
- [ ] Updated data appears immediately
- [ ] Audit timestamps are updated

## Cross-Phase Criteria

### Authentication
- [ ] JWT tokens are generated on login
- [ ] Tokens are validated on protected routes
- [ ] Expired tokens redirect to login
- [ ] Invalid tokens are rejected

### Error Handling
- [ ] Network errors show user-friendly messages
- [ ] Validation errors are specific and helpful
- [ ] Server errors don't expose sensitive information
- [ ] Error messages are visually distinct

### Accessibility
- [ ] All forms are keyboard navigable
- [ ] Screen readers can access all content
- [ ] Color contrast meets WCAG AA standards
- [ ] Form labels are properly associated

### Responsiveness
- [ ] All pages work on desktop (1920px, 1366px)
- [ ] All pages work on tablet (768px, 1024px)
- [ ] Forms remain usable on smaller screens
- [ ] Navigation is accessible on all screen sizes

## Definition of Done

### Code Quality
- [ ] Code follows project style guide
- [ ] All functions have docstrings/comments
- [ ] No console.log or debug code
- [ ] Error handling is comprehensive

### Testing
- [ ] Unit tests written and passing (>80% coverage)
- [ ] Integration tests written and passing
- [ ] E2E tests for critical flows
- [ ] Manual testing completed

### Documentation
- [ ] API endpoints documented (OpenAPI/Swagger)
- [ ] Component props/types documented
- [ ] README updated if needed
- [ ] Database schema documented

### Visual Validation
- [ ] All screenshots captured
- [ ] Demo video recorded (optional)
- [ ] UI reviewed and approved
- [ ] Cross-browser tested (Chrome, Firefox, Safari)

---

**Note**: All acceptance criteria must be met before marking the story as complete. Use this checklist during code review and QA testing.

