# Cursor AI Prompt: Generate Story-Based Development Documentation

## Context
You are creating comprehensive development documentation for the School Biometric Management System using a story-based, incremental approach. Every feature should be broken down into user stories, which are then divided into phases, and each phase contains specific tasks that can be visually tested and demonstrated.

## Your Mission
Create a complete `/docs` folder structure with the following:

1. **Story Maps** - User journey-based feature narratives
2. **Phase Breakdowns** - Development stages for each story
3. **Task Definitions** - Granular, testable work items
4. **Acceptance Criteria** - Visual validation points
5. **Demo Scenarios** - Step-by-step demonstration guides

## Folder Structure to Create

```
docs/
├── README.md                           # Documentation navigation guide
├── stories/
│   ├── 00-overview.md                 # Story mapping overview and principles
│   ├── 01-school-setup/
│   │   ├── story.md                   # Full story narrative
│   │   ├── phase-1-school-registration.md
│   │   ├── phase-2-admin-creation.md
│   │   ├── phase-3-dashboard-setup.md
│   │   ├── tasks/
│   │   │   ├── task-001-school-model.md
│   │   │   ├── task-002-school-api.md
│   │   │   ├── task-003-school-form.md
│   │   │   └── ...
│   │   ├── acceptance-criteria.md
│   │   └── demo-script.md
│   │
│   ├── 02-student-management/
│   │   ├── story.md
│   │   ├── phase-1-student-model.md
│   │   ├── phase-2-crud-operations.md
│   │   ├── phase-3-class-assignment.md
│   │   ├── phase-4-parent-contacts.md
│   │   ├── tasks/
│   │   ├── acceptance-criteria.md
│   │   └── demo-script.md
│   │
│   ├── 03-device-management/
│   │   ├── story.md
│   │   ├── phase-1-device-registration.md
│   │   ├── phase-2-device-groups.md
│   │   ├── phase-3-device-monitoring.md
│   │   ├── phase-4-simulation-mode.md
│   │   ├── tasks/
│   │   ├── acceptance-criteria.md
│   │   └── demo-script.md
│   │
│   ├── 04-automated-enrollment/        # THE KILLER FEATURE
│   │   ├── story.md
│   │   ├── phase-1-enrollment-ui.md
│   │   ├── phase-2-device-control.md
│   │   ├── phase-3-realtime-progress.md
│   │   ├── phase-4-template-storage.md
│   │   ├── phase-5-bulk-enrollment.md
│   │   ├── tasks/
│   │   ├── acceptance-criteria.md
│   │   └── demo-script.md
│   │
│   ├── 05-attendance-tracking/
│   │   ├── story.md
│   │   ├── phase-1-event-capture.md
│   │   ├── phase-2-entry-exit-logic.md
│   │   ├── phase-3-attendance-display.md
│   │   ├── phase-4-realtime-updates.md
│   │   ├── tasks/
│   │   ├── acceptance-criteria.md
│   │   └── demo-script.md
│   │
│   ├── 06-parent-notifications/
│   │   ├── story.md
│   │   ├── phase-1-sms-integration.md
│   │   ├── phase-2-notification-triggers.md
│   │   ├── phase-3-delivery-tracking.md
│   │   ├── tasks/
│   │   ├── acceptance-criteria.md
│   │   └── demo-script.md
│   │
│   └── 07-reporting-analytics/
│       ├── story.md
│       ├── phase-1-daily-reports.md
│       ├── phase-2-student-history.md
│       ├── phase-3-class-summaries.md
│       ├── tasks/
│       ├── acceptance-criteria.md
│       └── demo-script.md
│
├── workflows/
│   ├── enrollment-workflow.md          # Detailed enrollment flow diagrams
│   ├── attendance-workflow.md          # Attendance capture and processing
│   ├── notification-workflow.md        # SMS notification pipeline
│   └── sync-workflow.md               # Device synchronization process
│
├── testing/
│   ├── visual-testing-guide.md        # How to visually test each phase
│   ├── demo-data-setup.md             # Creating realistic demo data
│   ├── simulation-scenarios.md         # Device simulation test cases
│   └── acceptance-checklists.md        # Phase completion validation
│
└── implementation-order.md             # Recommended build sequence
```

## Story Template Format

Each story should follow this structure:

### story.md
```markdown
# Story [Number]: [Feature Name]

## User Story
As a [user type],
I want to [action],
So that [benefit].

## Business Value
[Why this matters for schools, parents, and administrators]

## User Journey
[Step-by-step narrative of how the user experiences this feature]

## Success Criteria
[What makes this story "done" - with visual indicators]

## Dependencies
[What must be completed before starting this story]

## Phases Overview
[List of phases with brief descriptions]

## Visual Outcomes
[Screenshots/wireframes showing the completed feature]

## Demo Highlights
[Key moments to show stakeholders]
```

### Phase Template (phase-X-name.md)
```markdown
# Phase X: [Phase Name]

## Goal
[What this phase achieves]

## Duration Estimate
[Realistic time estimate]

## Prerequisites
[What must exist before starting this phase]

## Technical Components

### Backend Changes
- [ ] Database migrations
- [ ] API endpoints
- [ ] Business logic
- [ ] Tests

### Frontend Changes
- [ ] Components
- [ ] Pages
- [ ] API integration
- [ ] Tests

### DevOps/Infrastructure
- [ ] Environment variables
- [ ] Docker updates
- [ ] Deployment changes

## Tasks Breakdown
[Link to specific tasks in tasks/ folder]

## Visual Checkpoints
[What you should be able to SEE and CLICK at the end of this phase]

### Success Screenshots
1. [Description of screenshot 1]
2. [Description of screenshot 2]
3. [Description of screenshot 3]

## Testing This Phase

### Manual Testing Steps
1. [Step 1 with expected visual result]
2. [Step 2 with expected visual result]
3. [Step 3 with expected visual result]

### Automated Tests
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] E2E tests pass

## Demo Script for This Phase
[Exact steps to demonstrate this phase to stakeholders]

## Next Phase
[What comes after this and why]
```

### Task Template (task-XXX-name.md)
```markdown
# Task XXX: [Task Name]

## Story/Phase
- **Story**: [Story number and name]
- **Phase**: [Phase number and name]

## Description
[Detailed description of what needs to be built]

## Type
- [ ] Backend
- [ ] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Acceptance Criteria
1. [ ] [Specific criterion with visual indicator]
2. [ ] [Specific criterion with visual indicator]
3. [ ] [Specific criterion with visual indicator]

## Technical Details

### Files to Create/Modify
```
path/to/file1.py
path/to/file2.tsx
path/to/file3.sql
```

### Key Code Patterns
[Specific patterns or approaches to use]

### Dependencies
- Task XXX (must be completed first)
- Library/Package needed

## Visual Testing

### Before State
[What the UI looks like before this task]

### After State
[What the UI looks like after this task]

### Testing Steps
1. Navigate to [URL/page]
2. Click [element]
3. Verify [visual outcome]
4. Check [specific detail]

## Definition of Done
- [ ] Code written and follows standards
- [ ] Unit tests written and passing
- [ ] Integration tests written and passing
- [ ] Code reviewed
- [ ] Visually tested in browser/UI
- [ ] Screenshots/video captured
- [ ] Documentation updated

## Time Estimate
[Realistic hours/days]

## Notes
[Any additional context or gotchas]
```

## Key Principles for All Documentation

### 1. **Visual-First Approach**
Every task, phase, and story must answer: "What will I SEE when this is done?"
- Include wireframes, mockups, or screenshot descriptions
- Describe button states, loading indicators, success messages
- Show error states and edge cases visually

### 2. **Incremental and Testable**
Each phase must be:
- Independently deployable
- Visually demonstrable
- Testable without subsequent phases
- Valuable on its own (even if limited)

### 3. **Demo-Ready Mindset**
Every phase should include:
- A 2-5 minute demo script
- Sample data to make the demo realistic
- Key talking points for stakeholders
- Expected questions and answers

### 4. **Story-Driven Development**
- Start with user narrative, not technical implementation
- Each story solves a real problem
- Stories can be explained to non-technical stakeholders
- Stories align with business value

### 5. **Clear Dependencies**
- Explicitly state what must be built first
- Identify blocking tasks
- Show parallel work opportunities
- Plan for integration points

## Specific Story Instructions

### Story 01: School Setup
**Focus**: Getting a school into the system for the first time
**Visual Outcome**: A school admin can log in and see their school dashboard
**Key Phases**:
1. School registration form
2. Admin user creation
3. Dashboard with school info
4. Settings and configuration

### Story 02: Student Management
**Focus**: Registering and organizing students
**Visual Outcome**: Admin can add students, assign to classes, and see student list
**Key Phases**:
1. Student data model and API
2. Student registration form
3. Class/stream assignment
4. Student list and search

### Story 03: Device Management
**Focus**: Registering and monitoring biometric devices
**Visual Outcome**: Admin can see all devices, their status (online/offline), and group them
**Key Phases**:
1. Device registration
2. Device groups
3. Real-time status monitoring
4. Simulation mode toggle

### Story 04: Automated Enrollment (CRITICAL - Most Detail Here)
**Focus**: Enrolling student fingerprints remotely from the web interface
**Visual Outcome**: Admin clicks "Enroll", student places finger on device, progress shows in real-time, success confirmation appears
**Key Phases**:
1. Enrollment UI (student selector, device selector, start button)
2. Device control (send CMD_STARTENROLL to device)
3. Real-time progress updates (WebSocket showing 0%, 33%, 66%, 100%)
4. Template storage (save fingerprint data)
5. Bulk enrollment (enroll multiple students at once)

**This is your DIFFERENTIATOR - make this story VERY detailed with:
- Step-by-step user experience
- Every screen state (idle, enrolling, success, error)
- WebSocket message flows
- Device communication sequences
- Simulation vs real device behavior
- Error handling scenarios

### Story 05: Attendance Tracking
**Focus**: Capturing and displaying attendance events
**Visual Outcome**: When a student taps their finger, attendance appears instantly on dashboard
**Key Phases**:
1. Event capture from device
2. Entry/Exit determination logic
3. Real-time attendance display
4. Attendance history view

### Story 06: Parent Notifications
**Focus**: Automatically notifying parents via SMS
**Visual Outcome**: Parent receives SMS within seconds of student check-in
**Key Phases**:
1. Africa's Talking SMS integration
2. Notification triggers (on attendance event)
3. Delivery tracking and retry logic

### Story 07: Reporting & Analytics
**Focus**: Viewing attendance patterns and reports
**Visual Outcome**: Admin can generate daily attendance reports, student history, class summaries
**Key Phases**:
1. Daily attendance report
2. Student attendance history
3. Class-level summaries

## Implementation Order Document

Create `implementation-order.md` with:
- Recommended sequence of stories
- Rationale for the order
- Parallel work opportunities
- Integration points
- Demo milestones (when to show stakeholders)

Suggested order:
1. Story 01: School Setup (foundation)
2. Story 02: Student Management (core data)
3. Story 03: Device Management (infrastructure)
4. Story 04: Automated Enrollment (killer feature - build in simulation mode first!)
5. Story 05: Attendance Tracking (primary use case)
6. Story 06: Parent Notifications (value multiplier)
7. Story 07: Reporting (polish and insights)

## Visual Testing Guide

Create `testing/visual-testing-guide.md` with:
- How to set up demo data for visual testing
- Browser DevTools usage for testing responsive design
- Screenshot capture procedures
- Video recording for demo purposes
- Simulation mode testing procedures
- Real device testing checklist

## Demo Data Setup

Create `testing/demo-data-setup.md` with:
- SQL scripts for realistic demo data
- Fixture files for testing
- Realistic student names, admission numbers
- Sample device configurations
- Pre-enrolled students for attendance demos

## Additional Requirements

### Wireframes/Mockups
For critical UI components, include ASCII art or descriptions:
```
+------------------------------------------+
|  [School Logo]    Greenfield Academy     |
+------------------------------------------+
|  Dashboard  |  Students  |  Devices      |
+------------------------------------------+
|                                          |
|  Enrollment Progress                     |
|  ┌────────────────────────────────┐     |
|  │ Student: John Doe              │     |
|  │ Device: Main Gate Scanner      │     |
|  │                                │     |
|  │ Progress: ████████░░░░ 60%     │     |
|  │ Status: Place finger on sensor │     |
|  │                                │     |
|  │ [Cancel Enrollment]            │     |
|  └────────────────────────────────┘     |
|                                          |
+------------------------------------------+
```

### Error Scenarios
Each phase must document:
- Happy path (everything works)
- Error states (device offline, enrollment failed, network error)
- Edge cases (duplicate student, invalid data, concurrent operations)
- Recovery procedures

### Performance Targets
Include in relevant phases:
- API response time expectations
- WebSocket latency targets
- Page load time goals
- Database query performance

## Final Deliverable

Generate a complete, professional documentation suite that:
1. ✅ Tells a compelling story for each feature
2. ✅ Breaks work into small, testable increments
3. ✅ Provides clear visual validation for every phase
4. ✅ Includes demo scripts for stakeholder presentations
5. ✅ Follows a logical implementation order
6. ✅ Balances technical detail with user narrative
7. ✅ Makes the project feel achievable and well-planned

The documentation should be so clear that:
- A new developer can pick up any story and start coding
- A project manager can track progress visually
- A stakeholder can understand the value of each phase
- A tester can validate completion without ambiguity
- A sales person can demonstrate the system confidently

---

**Now create the complete `/docs` folder structure with all stories, phases, tasks, and supporting documentation following these guidelines. Start with Story 04 (Automated Enrollment) as the most detailed example, since it's the system's key differentiator.**
