# Phase 1: School Registration

## Goal

Enable schools to register in the system through a web form, creating the foundation for multi-tenant architecture.

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

- [ ] Create `School` model with required fields
- [ ] Create database migration for `schools` table
- [ ] Create `SchoolCreate` Pydantic schema
- [ ] Create POST `/api/v1/schools/register` endpoint
- [ ] Implement school code uniqueness validation
- [ ] Add input validation and sanitization
- [ ] Create unit tests for registration logic
- [ ] Create integration tests for API endpoint

### Frontend Changes

- [ ] Create registration page route (`/register`)
- [ ] Create `SchoolRegistrationForm` component
- [ ] Create form validation logic
- [ ] Create form submission handler
- [ ] Add loading states during submission
- [ ] Add success/error message display
- [ ] Add form field components (input, textarea)
- [ ] Create responsive layout
- [ ] Add form accessibility features

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

### 3. Submit Form
- Click "Register" button
- See loading indicator during submission
- See success message on successful registration
- See error messages for validation failures
- See error message if school code already exists

### 4. Verify Data
- Check database to confirm school record created
- Verify timestamps (created_at, updated_at) are set
- Verify is_deleted is false

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

2. **Fill and Submit** (1 minute)
   - Fill form with sample data:
     - Name: "Greenfield Academy"
     - Code: "GFA-001"
     - Address: "Nairobi, Kenya"
     - Phone: "+254 712 345 678"
     - Email: "admin@greenfield.ac.ke"
   - Click "Register"
   - Show success message
   - Explain what happens in the background

3. **Show Validation** (30 seconds)
   - Try submitting empty form
   - Show validation errors
   - Try duplicate code
   - Show uniqueness error

### Talking Points

- "Registration takes less than a minute"
- "Each school gets a unique code for identification"
- "All data is validated before saving"
- "This creates the foundation for the school's isolated data"

### Expected Questions

**Q: What happens after registration?**  
A: The next phase adds admin account creation, then they can log in.

**Q: Can schools change their code later?**  
A: School code should remain stable, but we'll add ability to update other information in Phase 4.

**Q: Is there a limit on number of schools?**  
A: No, the system is designed to scale to many schools.

## Next Phase

**Phase 2: Admin User Creation** - After a school is registered, we need to create an admin account so they can log in and access their dashboard. This phase will add the user creation step to the registration flow.

