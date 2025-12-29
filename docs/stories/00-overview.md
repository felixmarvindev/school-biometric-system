# Story Mapping Overview

## What is Story Mapping?

Story mapping is a visual technique for organizing and prioritizing user stories. In this documentation, we use story maps to break down features into:

1. **Stories** - High-level user journeys that deliver business value
2. **Phases** - Development stages that deliver incremental value
3. **Tasks** - Granular, implementable work items

## Our Story Map Structure

```
Story (User Journey)
├── Phase 1 (First Increment)
│   ├── Task 001 (Specific Work Item)
│   ├── Task 002
│   └── Task 003
├── Phase 2 (Second Increment)
│   └── ...
└── Phase N (Final Increment)
```

## Core Principles

### 1. User-Centric Narrative

Every story starts with a user story format:
- **As a** [user type]
- **I want to** [action]
- **So that** [benefit]

### 2. Visual Outcomes First

Before writing code, we define:
- What the user will see
- What they can click
- What feedback they receive
- What states the UI can be in

### 3. Incremental Value

Each phase should:
- Be independently deployable
- Provide visible value to users
- Be testable without later phases
- Build toward the complete story

### 4. Testability

Every task includes:
- Visual acceptance criteria
- Manual testing steps
- Expected outcomes
- Screenshot descriptions

## Story Lifecycle

### 1. Story Definition
- Write user story narrative
- Define business value
- Outline user journey
- Identify dependencies

### 2. Phase Breakdown
- Break story into phases
- Define phase goals
- Estimate duration
- Identify technical components

### 3. Task Creation
- Create granular tasks
- Define acceptance criteria
- Specify files to create/modify
- Add visual testing steps

### 4. Implementation
- Complete tasks sequentially
- Test visually at each step
- Validate against acceptance criteria
- Update progress

### 5. Validation
- Complete acceptance criteria checklist
- Run demo script
- Capture screenshots/video
- Mark phase as complete

## Phase Structure

Each phase follows this structure:

### Phase Header
- Goal statement
- Duration estimate
- Prerequisites

### Technical Components
- Backend changes (database, API, logic)
- Frontend changes (components, pages, integration)
- DevOps changes (env vars, Docker, deployment)

### Visual Checkpoints
- What users can see
- What users can click
- UI states (loading, success, error)
- Success screenshots to capture

### Testing
- Manual testing steps with expected results
- Automated test requirements
- Edge cases to verify

### Demo Script
- Step-by-step demonstration guide
- Sample data needed
- Key talking points
- Expected questions and answers

## Task Structure

Each task includes:

### Metadata
- Story and phase association
- Task type (Backend/Frontend/Database/DevOps)
- Time estimate

### Requirements
- Detailed description
- Acceptance criteria (with visual indicators)
- Dependencies

### Implementation Details
- Files to create/modify
- Key code patterns
- Technical approach

### Testing
- Before/after visual states
- Step-by-step testing procedure
- Validation checkpoints

### Definition of Done
- Code written and reviewed
- Tests passing
- Visually tested
- Screenshots captured
- Documentation updated

## Visual-First Development

### Why Visual-First?

1. **Shared Understanding** - Everyone can see what "done" looks like
2. **Early Validation** - Catch UX issues before implementation
3. **Demo Ready** - Each phase can be demonstrated
4. **Progress Tracking** - Visual checkpoints show real progress

### Visual Documentation Includes:

- **Wireframes** - ASCII art or descriptions of UI layout
- **State Diagrams** - All possible UI states (idle, loading, success, error)
- **User Flows** - Step-by-step user interactions
- **Success Screenshots** - What to capture when complete
- **Error States** - How errors are displayed

## Demo-Ready Mindset

Every phase should be demo-ready, meaning:

### Before Demo
- All acceptance criteria met
- Realistic demo data available
- Error scenarios handled
- Performance acceptable

### During Demo
- 2-5 minute demonstration script
- Clear talking points
- Expected questions prepared
- Realistic user journey shown

### After Demo
- Feedback captured
- Improvements documented
- Next steps identified

## Dependencies and Sequencing

### Dependency Types

1. **Technical Dependencies**
   - Database schema must exist before API
   - API must exist before frontend integration
   - Authentication required before protected routes

2. **Business Dependencies**
   - Schools must exist before students
   - Students must exist before enrollment
   - Enrollment must exist before attendance

3. **Feature Dependencies**
   - Device management before enrollment
   - Enrollment before attendance
   - Attendance before notifications

### Parallel Work Opportunities

Some work can be done in parallel:
- Frontend components while API is developed
- Database schema design with API design
- Unit tests while implementing features
- Documentation while coding

## Acceptance Criteria Format

Every acceptance criterion should be:
- **Specific** - Clear and unambiguous
- **Visual** - Can be validated by looking at the screen
- **Testable** - Can be verified without interpretation
- **Independent** - Not dependent on other criteria

### Good Examples:
✅ "User sees a green success message after submitting the form"
✅ "Progress bar shows 0%, 33%, 66%, 100% during enrollment"
✅ "Device status indicator shows 'Online' in green when device is connected"

### Bad Examples:
❌ "Form works correctly"
❌ "Enrollment process is smooth"
❌ "Device connection is reliable"

## Story Status Tracking

Track story progress using:

- 📋 **Planned** - Story defined but not started
- 🔄 **In Progress** - One or more phases in progress
- ✅ **Completed** - All phases complete
- 🚧 **Blocked** - Waiting on dependencies
- 📝 **Review** - Ready for stakeholder review

## Best Practices

### Writing Stories
1. Start with the user's problem, not the solution
2. Keep stories focused on one user journey
3. Make stories independently valuable
4. Write in non-technical language

### Breaking Down Phases
1. Each phase should take 1-3 days
2. Phases should be independently deployable
3. Early phases should provide the most value
4. Later phases add polish and advanced features

### Creating Tasks
1. Tasks should take 2-8 hours
2. Tasks should be testable independently
3. Include clear acceptance criteria
4. Specify exact files to modify

### Testing
1. Test visually first (manual)
2. Then automate tests
3. Test happy path and error cases
4. Test with realistic data

## Next Steps

1. Review the [Implementation Order](../implementation-order.md) to see recommended sequence
2. Read a complete story (e.g., [Story 01: School Setup](01-school-setup/story.md))
3. Follow the story through its phases and tasks
4. Use this as a template for future stories

---

**Remember**: Story mapping is about delivering value incrementally while maintaining a clear vision of the complete feature. Each phase should be valuable, testable, and demo-ready!

