# Phase 1: School Registration

## Goal

Enable schools to register in the system through a two-step web form (school info + admin account), creating the foundation for multi-tenant architecture. Both school and admin are created in a single atomic transaction.

## Duration Estimate

3-5 days

## Prerequisites

- ✅ Database schema designed
- ✅ Database migrations set up (Alembic)
- ✅ API Gateway service running
- ✅ Frontend application structure created
- ✅ Basic routing configured

## Technical Components

### Backend Changes

- [x] Create `School` model with required fields
- [x] Create database migration for `schools` table
- [x] Create `SchoolCreate` Pydantic schema
- [x] Create POST `/api/v1/schools/register` endpoint (combined with admin creation)
- [x] Implement school code uniqueness validation
- [x] Add input validation and sanitization
- [x] Implement atomic transaction for school + admin creation
- [x] Add response validation before commit (prevents inconsistent state)
- [x] Implement transaction rollback on any failure
- [ ] Create unit tests for registration logic
- [ ] Create integration tests for API endpoint

### Frontend Changes

- [x] Create registration page route (`/register`)
- [x] Create `SchoolRegistrationFormSimple` reusable component
- [x] Create two-step registration flow (school info → admin account)
- [x] Create step progress indicator component
- [x] Create step header component with animations
- [x] Create form validation logic (client-side)
- [x] Create form submission handler (single API call for both)
- [x] Add loading states during submission
- [x] Add success screen component with registered data
- [x] Add error message display with field-level errors
- [x] Add form field components (input, textarea, label)
- [x] Create responsive layout with gradient background
- [x] Add form accessibility features (ARIA labels, keyboard navigation)
- [x] Add placeholder text to all form fields

### DevOps/Infrastructure

- [ ] Environment variables for database connection
- [ ] Ensure database is accessible from backend services
- [ ] Configure CORS for registration endpoint (if needed)

## Tasks Breakdown

See [tasks/](tasks/) folder:
- [Task 001: School Database Model](tasks/task-001-school-model.md)
- [Task 002: School Registration API](tasks/task-002-school-api.md)
- [Task 003: School Registration Form](tasks/task-003-school-form.md)

## Visual Checkpoints

At the end of this phase, you should be able to:

### 1. Access Registration Page
- Navigate to `/register`
- See a clean registration form
- See welcome message and instructions

### 2. Fill Registration Form
- Enter school name (required field)
- Enter school code (required, unique identifier)
- Enter address (optional)
- Enter phone number (optional, formatted)
- Enter email (optional, validated)

### 3. Submit School Information
- Click "Next: Admin Account" button
- See loading indicator during validation
- Progress to Step 2 (Admin Account) if validation passes
- See error messages for validation failures
- See error message if school code already exists (after admin step submission)

### 4. Complete Registration (Step 2)
- Fill admin account form (first name, last name, email, password, confirm password)
- See password strength indicator update in real-time
- Toggle password visibility
- Click "Complete Registration" button
- See loading state with spinner
- See success screen with school name and admin email
- Automatically redirected to login page after 3 seconds

### 5. Verify Data
- Check database to confirm both school and admin user records created
- Verify school and admin are created in single transaction (atomic)
- Verify timestamps (created_at, updated_at) are set
- Verify is_deleted is false for both
- Verify admin.school_id matches school.id

### Success Screenshots

1. **Registration Form** - Clean form with all fields visible
2. **Success Message** - Green success banner after registration
3. **Validation Errors** - Red error messages for invalid inputs
4. **Duplicate Code Error** - Specific error for duplicate school code

## Testing This Phase

### Manual Testing Steps

1. **Happy Path**
   - Navigate to `/register`
   - Fill all required fields with valid data
   - Submit form
   - ✅ Verify success message appears
   - ✅ Verify form clears or redirects
   - ✅ Check database for new school record

2. **Validation Testing**
   - Submit empty form
   - ✅ Verify all required field errors appear
   - Enter invalid email format
   - ✅ Verify email validation error
   - Enter very long text in fields
   - ✅ Verify max length validation

3. **Uniqueness Testing**
   - Register school with code "TEST-001"
   - Try to register another school with same code
   - ✅ Verify duplicate code error message

4. **UI/UX Testing**
   - Test on different screen sizes (desktop, tablet, mobile)
   - ✅ Verify form is responsive
   - ✅ Verify all text is readable
   - ✅ Verify form is accessible (keyboard navigation, screen readers)

### Automated Tests

- [ ] Unit tests for school model validation
- [ ] Unit tests for school code uniqueness check
- [ ] API integration tests for registration endpoint
- [ ] Frontend component tests for form validation
- [ ] E2E test for complete registration flow

## Demo Script for This Phase

### Setup (1 minute)
1. Open browser to registration page
2. Explain: "This is where schools first register in the system"

### Demonstration (2 minutes)

1. **Show the Form** (30 seconds)
   - Point out all fields
   - Explain school code uniqueness
   - Mention optional vs required fields

2. **Fill School Information (Step 1)** (30 seconds)
   - Fill form with sample data:
     - Name: "Greenfield Academy"
     - Code: "GFA-001"
     - Address: "Nairobi, Kenya" (optional)
     - Phone: "+254 712 345 678" (optional)
     - Email: "admin@greenfield.ac.ke" (optional)
   - Click "Next: Admin Account"
   - Show progress indicator moving to step 2

3. **Fill Admin Account (Step 2)** (30 seconds)
   - Fill admin form:
     - First Name: "John"
     - Last Name: "Doe"
     - Email: "admin@greenfield.ac.ke"
     - Password: "SecurePass123!"
     - Confirm Password: "SecurePass123!"
   - Show password strength indicator
   - Click "Complete Registration"
   - Show success screen with both school and admin info
   - Explain atomic transaction (both created together or neither)

3. **Show Validation** (30 seconds)
   - Try submitting empty form
   - Show validation errors
   - Try duplicate code
   - Show uniqueness error

### Talking Points

- "Registration is a simple two-step process"
- "Each school gets a unique code for identification"
- "All data is validated before saving"
- "School and admin are created together in a single transaction - if anything fails, nothing is saved"
- "This ensures data consistency and prevents orphaned records"
- "This creates the foundation for the school's isolated data"

### Expected Questions

**Q: What happens after registration?**  
A: The admin account is created during registration. After the success screen, they're automatically redirected to the login page where they can log in with their credentials.

**Q: Can schools change their code later?**  
A: School code should remain stable, but we'll add ability to update other information in Phase 4.

**Q: Is there a limit on number of schools?**  
A: No, the system is designed to scale to many schools.

## Next Phase

**Phase 2: Admin User Creation** - After a school is registered, we need to create an admin account so they can log in and access their dashboard. This phase will add the user creation step to the registration flow.

