# Phase 1: Enrollment UI

## Goal

Build the enrollment user interface with student selector, device selector, finger selector, and start button. This provides the foundation for the enrollment experience.

## Duration Estimate

4-5 days

## Prerequisites

- ✅ Story 02 complete (students exist)
- ✅ Story 03 complete (devices exist)
- ✅ Frontend routing and navigation working

## Technical Components

### Backend Changes

- [ ] Create GET `/api/v1/students` endpoint (for student list)
- [ ] Create GET `/api/v1/devices` endpoint (for device list)
- [ ] Add filtering for available devices (online devices)
- [ ] Create enrollment session model (optional, for Phase 2)

### Frontend Changes

- [ ] Create enrollment page route (`/enrollment`)
- [ ] Create `EnrollmentWizard` component
- [ ] Create `StudentSelector` component
- [ ] Create `DeviceSelector` component
- [ ] Create `FingerSelector` component
- [ ] Create `EnrollmentButton` component
- [ ] Add student search functionality
- [ ] Add device status indicators
- [ ] Create responsive layout
- [ ] Add form validation

### DevOps/Infrastructure

- [ ] (No changes needed in this phase)

## Tasks Breakdown

See [tasks/](tasks/) folder:
- Task 011: Student Selector Component
- Task 012: Device Selector Component
- Task 013: Enrollment Form Layout
- Task 014: Form Validation

## Visual Checkpoints

At the end of this phase, you should be able to:

### 1. Access Enrollment Page
- Navigate to `/enrollment`
- See enrollment interface
- See three main sections: Student, Device, Finger

### 2. Select Student
- See list of students (or search field)
- Can search students by name or admission number
- Can select a student from list
- Selected student is highlighted
- Student details show (name, admission number, class)

### 3. Select Device
- See list of available devices
- Devices show status (online/offline)
- Can select an online device
- Selected device is highlighted
- Device details show (name, location, status)

### 4. Select Finger
- See finger selector dropdown
- Options: Thumb (0), Index (1), Middle (2), Ring (3), Pinky (4), etc.
- Default selection is Index Finger (most common)
- Selected finger is shown

### 5. Start Enrollment
- "Start Enrollment" button is visible
- Button is enabled when all selections are made
- Button shows loading state on click
- Form validates before submission

### Success Screenshots

1. **Enrollment Page** - Clean layout with all selectors visible
2. **Student Selection** - Search functionality with selected student highlighted
3. **Device Selection** - List with online/offline indicators
4. **Complete Form** - All fields filled, ready to start

## Testing This Phase

### Manual Testing Steps

1. **Page Load**
   - Navigate to `/enrollment`
   - ✅ Verify page loads without errors
   - ✅ Verify all sections are visible

2. **Student Selection**
   - Type in student search field
   - ✅ Verify search filters students
   - ✅ Verify student list updates
   - Click a student
   - ✅ Verify student is selected and highlighted

3. **Device Selection**
   - View device list
   - ✅ Verify online/offline indicators show correctly
   - ✅ Verify only online devices are selectable (or show warning for offline)
   - Click a device
   - ✅ Verify device is selected and highlighted

4. **Form Validation**
   - Try to click "Start Enrollment" without selections
   - ✅ Verify button is disabled or shows validation error
   - Make all selections
   - ✅ Verify button becomes enabled
   - ✅ Verify form is ready to submit

5. **Responsive Design**
   - Test on different screen sizes
   - ✅ Verify layout works on desktop
   - ✅ Verify layout works on tablet
   - ✅ Verify all elements are accessible

### Automated Tests

- [ ] Unit tests for student selector component
- [ ] Unit tests for device selector component
- [ ] Unit tests for form validation
- [ ] Integration tests for API calls
- [ ] E2E test for complete form flow

## Demo Script for This Phase

### Demonstration (2 minutes)

1. **Show Enrollment Interface** (30 seconds)
   - Navigate to enrollment page
   - Point out three main sections
   - Explain the flow: Select student → Select device → Select finger → Start

2. **Demonstrate Selection** (1 minute)
   - Search for a student (type "John")
   - Show filtered results
   - Select a student
   - Show device list with status indicators
   - Select an online device
   - Show finger selector (explain index finger is most common)
   - Point out "Start Enrollment" button

3. **Show Validation** (30 seconds)
   - Try clicking "Start Enrollment" without selections
   - Show button is disabled or error message
   - Complete all selections
   - Show button becomes enabled

### Talking Points

- "The enrollment interface is intuitive and guided"
- "Student search makes it easy to find students quickly"
- "Device status indicators ensure we only enroll on available devices"
- "All selections are validated before starting enrollment"

### Expected Questions

**Q: Can we enroll multiple students at once?**  
A: Bulk enrollment will be added in Phase 5. For now, we enroll one at a time.

**Q: What if a device is offline?**  
A: Offline devices are clearly marked. We'll add better handling in Phase 2.

**Q: Can we change selections after starting?**  
A: Once enrollment starts, it should complete or be cancelled. You can start a new enrollment after.

## Next Phase

**Phase 2: Device Control** - Now that we have the UI, we need to actually communicate with devices to start enrollment. This phase adds the backend logic to send enrollment commands to devices and handle responses.

