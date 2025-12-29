# Story 02: Student Management

## User Story

**As a** school administrator,  
**I want to** register students, organize them into classes and streams, and manage their information,  
**So that** I can enroll them in the biometric system and track their attendance.

## Business Value

Student Management is the core data foundation for the attendance system. Without students registered, there's nothing to track. This story enables:

- **Student registration** - Admins can add students to the system
- **Academic organization** - Students are organized into classes and streams
- **Data management** - Complete student profiles with parent contact information
- **Foundation for enrollment** - Students must exist before fingerprint enrollment
- **Attendance tracking** - Student records enable attendance events

**Impact**: Critical - Required for enrollment and attendance  
**Stakeholders**: School administrators, Teachers  
**Users Affected**: School admins (primary), Teachers (viewers)

## User Journey

### Step 1: Create Class Structure
1. Admin navigates to Students section
2. Sees option to create classes
3. Creates classes (e.g., "Grade 1", "Grade 2", "Form 1")
4. Creates streams within classes (e.g., "A", "B", "C")

### Step 2: Add Student
1. Clicks "Add Student" button
2. Fills student registration form:
   - Admission number (unique)
   - Personal information (name, DOB, gender)
   - Class and stream assignment
   - Parent contact information
   - Photo upload (optional)
3. Submits form
4. Sees success message
5. Student appears in student list

### Step 3: View Student List
1. Views list of all students
2. Can filter by class, stream, or search by name
3. Can click student to see details
4. Can edit student information
5. Can deactivate student (soft delete)

### Step 4: Manage Student Information
1. Opens student detail page
2. Views complete student profile
3. Can update information
4. Can view enrollment status (which devices enrolled)
5. Can view attendance history (future story)

## Success Criteria

### Visual Indicators
- ✅ Admin can create classes and streams
- ✅ Admin can add students through form
- ✅ Student list displays all students
- ✅ Student search and filtering works
- ✅ Student detail page shows complete information
- ✅ Student information can be updated
- ✅ Students can be deactivated

### Functional Requirements
- ✅ Student data is stored correctly
- ✅ Admission numbers are unique per school
- ✅ Students can be assigned to classes/streams
- ✅ Parent contact information is stored
- ✅ Soft delete preserves data history
- ✅ All validations work correctly

## Dependencies

### Prerequisites
- ✅ Story 01 complete (schools must exist)
- ✅ Authentication working
- ✅ Database schema defined

### Blocks
- **Story 04: Automated Enrollment** - Students must exist before enrollment
- **Story 05: Attendance Tracking** - Students needed for attendance records

## Phases Overview

### Phase 1: Student Data Model
**Goal**: Create database schema for students, classes, and streams  
**Duration**: 2-3 days

### Phase 2: CRUD Operations
**Goal**: Implement API endpoints for student management  
**Duration**: 3-4 days

### Phase 3: Class Assignment
**Goal**: Enable assigning students to classes and streams  
**Duration**: 2-3 days

### Phase 4: Parent Contacts
**Goal**: Add parent/guardian contact information  
**Duration**: 2 days

## Visual Outcomes

### Student List View

```
+------------------------------------------+
|  Students                        [+ Add] |
+------------------------------------------+
|  [Search...]  Class: [All ▼]  Stream: [All ▼] |
+------------------------------------------+
|  Admission | Name        | Class | Stream | Status |
|  ────────────────────────────────────────|
|  001       | John Doe    | Form 1|   A    | Active |
|  002       | Jane Smith  | Form 1|   B    | Active |
|  003       | Bob Johnson | Grade 3|  A    | Active |
+------------------------------------------+
```

### Student Form

```
+------------------------------------------+
|  Add Student                             |
+------------------------------------------+
|  Personal Information                    |
|  ┌──────────────────────────────────┐   |
|  │ Admission #: [_________]         │   |
|  │ First Name:  [_________]         │   |
|  │ Last Name:   [_________]         │   |
|  │ Date of Birth: [__/__/____]      │   |
|  │ Gender: [Male ▼]                 │   |
|  └──────────────────────────────────┘   |
|                                          |
|  Academic Assignment                     |
|  ┌──────────────────────────────────┐   |
|  │ Class: [Form 1 ▼]                │   |
|  │ Stream: [A ▼]                    │   |
|  └──────────────────────────────────┘   |
|                                          |
|  Parent Information                      |
|  ┌──────────────────────────────────┐   |
|  │ Phone: [+254 _________]          │   |
|  │ Email: [_____________]           │   |
|  └──────────────────────────────────┘   |
|                                          |
|  [Cancel]              [Save Student]   |
+------------------------------------------+
```

## Demo Highlights

1. **Create Class Structure** - Show how classes and streams are organized
2. **Add Student** - Demonstrate complete student registration
3. **Student List** - Show filtering and search capabilities
4. **Student Details** - Show complete student profile

---

**Story Status**: 📋 Planned  
**Estimated Total Duration**: 9-12 days  
**Priority**: 🔴 Critical (Required for enrollment)

