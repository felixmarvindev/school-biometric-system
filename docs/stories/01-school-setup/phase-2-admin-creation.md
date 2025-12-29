# Phase 2: Admin User Creation

## Goal

Enable admin account creation during the school registration flow, providing secure access to the system.

## Duration Estimate

2-3 days

## Prerequisites

- ✅ Phase 1 complete (school registration working)
- ✅ User authentication system (JWT) configured
- ✅ Password hashing library available (bcrypt/passlib)

## Technical Components

### Backend Changes

- [ ] Create `User` model with school association
- [ ] Create database migration for `users` table
- [ ] Create `UserCreate` Pydantic schema
- [ ] Add password hashing utility
- [ ] Add password strength validation
- [ ] Update registration endpoint to create user
- [ ] Add user creation to registration flow
- [ ] Create unit tests for user creation
- [ ] Create integration tests

### Frontend Changes

- [ ] Add admin account creation step to registration flow
- [ ] Create `AdminAccountForm` component
- [ ] Add password strength indicator
- [ ] Add password confirmation field
- [ ] Add password visibility toggle
- [ ] Update form submission to include user data
- [ ] Add validation for password match
- [ ] Update success message to mention login

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
- After school registration, see admin account creation step
- Form includes: full name, email, password, confirm password
- Password strength indicator visible
- Submit button to complete registration

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
   - Complete school registration
   - Fill admin account form with valid data
   - Submit form
   - ✅ Verify success message
   - ✅ Check database for user record
   - ✅ Verify user.school_id matches school.id

2. **Password Validation**
   - Enter weak password
   - ✅ Verify strength indicator shows weak
   - ✅ Verify password requirements are listed
   - Enter passwords that don't match
   - ✅ Verify match error message

3. **Security Testing**
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
   - Fill form with sample data
   - Show password strength indicator updating
   - Submit form
   - Show success message

3. **Explain Security** (30 seconds)
   - Explain password hashing
   - Explain JWT authentication
   - Mention secure storage

### Talking Points

- "Admins create their account during registration"
- "Passwords are securely hashed before storage"
- "Password strength helps ensure account security"
- "Each school has isolated admin accounts"

## Next Phase

**Phase 3: Dashboard Setup** - Now that schools can register and admins can create accounts, we need to provide a dashboard for admins to see their school's information and navigate the system.

