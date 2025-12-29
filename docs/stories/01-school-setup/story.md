# Story 01: School Setup

## User Story

**As a** school administrator,  
**I want to** register my school and create my admin account,  
**So that** I can start using the biometric system to manage my school's attendance.

## Business Value

The School Setup story is the foundation of the entire system. Without schools registered in the system, no other features can function. This story enables:

- **Multi-tenant architecture** - Each school has isolated data and configuration
- **School branding** - Schools can customize their experience
- **Admin user management** - Secure access control per school
- **System foundation** - All other features depend on schools existing

**Impact**: Critical - Blocks all other stories  
**Stakeholders**: School administrators, System administrators  
**Users Affected**: School admins (primary), Super admins (secondary)

## User Journey

### Step 1: Initial Access
1. School administrator navigates to the registration page
2. Sees a clean, professional registration form
3. Reads the welcome message explaining the system

### Step 2: School Registration
1. Fills in school details:
   - School name
   - School code (unique identifier)
   - Address
   - Contact information (phone, email)
2. Submits the form
3. Sees a success message confirming registration
4. Receives a confirmation email (future phase)

### Step 3: Admin Account Creation
1. System prompts for admin user details:
   - Full name
   - Email address
   - Password (with strength requirements)
   - Confirm password
2. Submits admin account details
3. Sees success message
4. Receives welcome email with login credentials

### Step 4: First Login
1. Navigates to login page
2. Enters credentials
3. Successfully logs in
4. Sees the school dashboard with:
   - School information display
   - Quick stats (empty state)
   - Navigation menu
   - Welcome message

### Step 5: Dashboard Overview
1. Views school dashboard
2. Sees school name, code, and contact information
3. Notes empty states for:
   - Students (0 students)
   - Devices (0 devices)
   - Attendance (No records)
4. Can navigate to settings to update school information

## Success Criteria

### Visual Indicators
- ✅ School registration form is accessible and functional
- ✅ Admin can successfully register a school
- ✅ Admin can create their admin account
- ✅ Admin can log in with their credentials
- ✅ Admin sees a personalized dashboard with their school's information
- ✅ Navigation menu is visible and functional
- ✅ Empty states are displayed for future features

### Functional Requirements
- ✅ School data is stored securely in the database
- ✅ School code is unique across the system
- ✅ Admin user is associated with the school
- ✅ Authentication works correctly (JWT tokens)
- ✅ Authorization restricts admin to their school's data
- ✅ All form validations work correctly

### Non-Functional Requirements
- ✅ Form submission completes in < 2 seconds
- ✅ Dashboard loads in < 1 second
- ✅ All text is readable and accessible
- ✅ Responsive design works on desktop and tablet
- ✅ Error messages are clear and helpful

## Dependencies

### Prerequisites
- ✅ Database schema defined and migrated
- ✅ Authentication system (JWT) implemented
- ✅ API Gateway with routing configured
- ✅ Frontend application structure set up

### Blocks
- **Story 02: Student Management** - Cannot add students without schools
- **Story 03: Device Management** - Cannot register devices without schools
- **All other stories** - All depend on schools existing

### Parallel Work Opportunities
- Frontend components can be built while backend API is developed
- Database schema can be designed in parallel with API design
- UI/UX designs can be created independently

## Phases Overview

### Phase 1: School Registration (Foundation)
**Goal**: Enable schools to register in the system  
**Duration**: 3-5 days  
**Value**: Creates the foundation for multi-tenancy

**Key Deliverables**:
- School registration form (frontend)
- School registration API endpoint
- School model and database table
- School code uniqueness validation

### Phase 2: Admin User Creation (Access Control)
**Goal**: Enable admin account creation during registration  
**Duration**: 2-3 days  
**Value**: Provides secure access to the system

**Key Deliverables**:
- Admin user creation during registration flow
- User model with school association
- Password hashing and validation
- User authentication setup

### Phase 3: Dashboard Setup (User Experience)
**Goal**: Provide a personalized dashboard after login  
**Duration**: 3-4 days  
**Value**: Gives admins a home base and shows system value

**Key Deliverables**:
- School dashboard page
- School information display
- Navigation menu
- Empty state components for future features
- Welcome message and quick stats

### Phase 4: Settings and Configuration (Polish)
**Goal**: Allow admins to update school information  
**Duration**: 2-3 days  
**Value**: Enables schools to keep their information current

**Key Deliverables**:
- Settings page
- School information update form
- Update API endpoint
- Success/error feedback

## Visual Outcomes

### Registration Flow

```
+------------------------------------------+
|         School Registration              |
+------------------------------------------+
|                                          |
|  Welcome to School Biometric System     |
|  Please register your school to begin   |
|                                          |
|  ┌──────────────────────────────────┐   |
|  │ School Name: [_______________]   │   |
|  │ School Code: [_______________]   │   |
|  │ Address:     [_______________]   │   |
|  │ Phone:       [_______________]   │   |
|  │ Email:       [_______________]   │   |
|  │                                  │   |
|  │ [Cancel]        [Continue →]    │   |
|  └──────────────────────────────────┘   |
|                                          |
+------------------------------------------+
```

### Dashboard (Empty State)

```
+------------------------------------------+
|  [Logo]  Greenfield Academy      [User] |
+------------------------------------------+
|  Dashboard | Students | Devices | ...   |
+------------------------------------------+
|                                          |
|  Welcome back, John Doe                 |
|                                          |
|  School Information                      |
|  ┌──────────────────────────────────┐   |
|  │ Name: Greenfield Academy         │   |
|  │ Code: GFA-001                    │   |
|  │ Address: Nairobi, Kenya          │   |
|  │ Phone: +254 712 345 678          │   |
|  └──────────────────────────────────┘   |
|                                          |
|  Quick Stats                             |
|  ┌──────┐ ┌──────┐ ┌──────┐            |
|  │  0   │ │  0   │ │  0   │            |
|  │Students│Devices│Attendance│          |
|  └──────┘ └──────┘ └──────┘            |
|                                          |
|  [Get Started: Add Your First Student]  |
|                                          |
+------------------------------------------+
```

## Demo Highlights

### Key Moments to Show Stakeholders

1. **Clean Registration Experience** (30 seconds)
   - Show the registration form
   - Demonstrate form validation
   - Submit and show success

2. **Seamless Account Creation** (30 seconds)
   - Show admin account creation step
   - Demonstrate password requirements
   - Show success message

3. **Personalized Dashboard** (1 minute)
   - Show dashboard with school information
   - Highlight empty states (opportunity to explain future features)
   - Show navigation menu
   - Explain what's coming next

4. **Security and Isolation** (30 seconds)
   - Explain multi-tenant architecture
   - Show how each school's data is isolated
   - Mention authentication and authorization

### Talking Points

- "Schools can register in under 2 minutes"
- "Each school's data is completely isolated and secure"
- "The dashboard gives admins a clear view of their school's status"
- "Empty states guide users on what to do next"
- "This foundation enables all other features"

### Expected Questions

**Q: Can schools have multiple admins?**  
A: Yes, that will be added in a future phase. For now, each school has one primary admin.

**Q: What if a school code is already taken?**  
A: The system validates uniqueness and shows a clear error message.

**Q: Can schools change their information later?**  
A: Yes, Phase 4 adds a settings page for this.

**Q: Is there a super admin?**  
A: Yes, super admin functionality will be added separately for system-wide management.

## Technical Notes

### Database Schema
- Schools table with unique code constraint
- Users table with school_id foreign key
- Soft delete support (is_deleted flag)
- Audit timestamps (created_at, updated_at)

### API Design
- RESTful endpoints
- Input validation using Pydantic
- Error responses with clear messages
- JWT authentication for subsequent requests

### Frontend Architecture
- Next.js App Router
- Server components for initial data
- Client components for forms
- Form validation (client and server)
- Loading and error states

## Next Steps

After completing this story:
1. Move to **Story 02: Student Management** to enable admins to add students
2. Or move to **Story 03: Device Management** if device setup is priority
3. Consider adding **email verification** as an enhancement
4. Consider adding **super admin dashboard** for system management

---

**Story Status**: 📋 Planned  
**Estimated Total Duration**: 10-15 days  
**Priority**: 🔴 Critical (Blocks all other stories)

