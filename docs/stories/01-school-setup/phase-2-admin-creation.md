# Phase 2: Admin User Creation

## Goal

Enable admin account creation as part of the school registration flow (Step 2), providing secure access to the system. School and admin are created together in a single atomic transaction.

## Duration Estimate

2-3 days

## Prerequisites

- ✅ Phase 1 complete (school registration form working)
- ✅ User authentication system (JWT) configured
- ✅ Password hashing library available (bcrypt/passlib)
- ✅ User model and repository created

## Technical Components

### Backend Changes

- [x] Create `User` model with school association
- [x] Create database migration for `users` table
- [x] Create `UserCreate` Pydantic schema
- [x] Add password hashing utility (bcrypt)
- [x] Add password strength validation
- [x] Update registration endpoint to create both school and admin in one call
- [x] Implement `create_school_with_admin()` service method with transaction
- [x] Add `create_without_commit()` methods to repositories for transaction support
- [x] Implement response validation before commit (prevents inconsistent state)
- [x] Implement transaction rollback if user creation fails
- [ ] Create unit tests for user creation
- [ ] Create integration tests

### Frontend Changes

- [x] Add admin account creation as Step 2 in registration flow
- [x] Create `AdminAccountFormSimple` reusable component (can be used independently)
- [x] Create `SchoolRegistrationFormSimple` reusable component
- [x] Create `StepProgressIndicator` component
- [x] Create `StepHeader` component with animations
- [x] Create `RegistrationSuccessScreen` component
- [x] Add password strength indicator with animated progress bar
- [x] Add password confirmation field with validation
- [x] Add password visibility toggle (eye icon)
- [x] Update form submission to send both school and admin data in single API call
- [x] Add validation for password match
- [x] Add field-level error handling
- [x] Update success screen to show both school name and admin email
- [x] Add automatic redirect to login page after 3 seconds

### DevOps/Infrastructure

- [ ] Ensure JWT secret key is configured
- [ ] Configure password hashing settings

## Tasks Breakdown

See [tasks/](tasks/) folder:
- [Task 004: User Model and Authentication](tasks/task-004-user-model.md)
- [Task 005: Admin Account Form](tasks/task-005-admin-form.md)

## Visual Checkpoints

At the end of this phase, you should be able to:

### 1. Complete Registration Flow
- After Step 1 (school info), automatically see Step 2 (admin account)
- Progress indicator shows both steps with current step highlighted
- Step header shows icon, title, and description for current step
- Form includes: first name, last name, email, password, confirm password
- Password strength indicator visible and updates in real-time
- "Back" button to return to Step 1
- "Complete Registration" button to submit both school and admin together

### 2. Password Validation
- See password requirements listed
- Password strength indicator updates as you type
- Confirm password field validates match
- Clear error messages for validation failures

### 3. Account Creation
- Submit admin account details
- See success message
- User record created in database
- User associated with school

### Success Screenshots

1. **Admin Account Form** - Clean form with password fields
2. **Password Strength Indicator** - Visual feedback as user types
3. **Validation Errors** - Clear messages for password requirements
4. **Success Message** - Confirmation with next steps

## Testing This Phase

### Manual Testing Steps

1. **Happy Path**
   - Complete Step 1 (school registration)
   - Progress to Step 2 (admin account)
   - Fill admin account form with valid data
   - Submit form (creates both school and admin in one API call)
   - ✅ Verify success screen shows both school name and admin email
   - ✅ Verify automatic redirect to login page after 3 seconds
   - ✅ Check database for both school and user records
   - ✅ Verify user.school_id matches school.id
   - ✅ Verify both created in single transaction (check timestamps are identical)

2. **Password Validation**
   - Enter weak password
   - ✅ Verify strength indicator shows weak
   - ✅ Verify password requirements are listed
   - Enter passwords that don't match
   - ✅ Verify match error message

3. **Transaction Testing**
   - Create school with valid data but invalid admin email (duplicate)
   - ✅ Verify transaction rollback - no school record created
   - Create school with valid data but weak password
   - ✅ Verify transaction rollback - no school record created
   - Verify atomicity: both succeed or both fail

4. **Security Testing**
   - Verify password is hashed in database (not plain text)
   - Test with SQL injection attempts in form fields
   - ✅ Verify passwords are properly hashed
   - ✅ Verify input sanitization

### Automated Tests

- [ ] Unit tests for password hashing
- [ ] Unit tests for password validation
- [ ] Integration tests for user creation
- [ ] E2E test for complete registration flow

## Demo Script for This Phase

### Demonstration (2 minutes)

1. **Show Admin Form** (30 seconds)
   - After school registration, show admin account step
   - Point out password requirements
   - Show password strength indicator

2. **Create Account** (1 minute)
   - Show Step 2 form (admin account)
   - Fill form with sample data
   - Show password strength indicator updating in real-time
   - Toggle password visibility
   - Submit form
   - Show success screen with school and admin information
   - Show automatic redirect countdown

3. **Explain Security** (30 seconds)
   - Explain password hashing
   - Explain JWT authentication
   - Mention secure storage

### Talking Points

- "Admins create their account as part of registration (Step 2)"
- "School and admin are created together in a single transaction"
- "If anything fails, nothing is saved - ensuring data consistency"
- "Passwords are securely hashed before storage"
- "Password strength indicator helps ensure account security"
- "Each school has isolated admin accounts"
- "The admin form component is reusable for future admin creation features"

## Next Phase

**Phase 3: Dashboard Setup** - Now that schools can register and admins can create accounts, we need to provide a dashboard for admins to see their school's information and navigate the system.

