# Phase 1: Event Capture

## Goal

Capture attendance events from biometric devices as students use them.

## Duration Estimate

4-5 days

## Prerequisites

- ✅ Story 04 complete (students enrolled on devices)

## Technical Components

### Backend Changes

- [ ] Set up device event listening
- [ ] Implement EF_ATTLOG event handler
- [ ] Parse attendance events from devices
- [ ] Match events to students (via enrollment)
- [ ] Store raw attendance events
- [ ] Emit events via WebSocket

### Frontend Changes

- [ ] (None in this phase - events captured, display in Phase 3)

## Visual Checkpoints

- [ ] Events are captured from devices
- [ ] Events are matched to students
- [ ] Events are stored in database
- [ ] Events are emitted via WebSocket

## Next Phase

**Phase 2: Entry/Exit Logic** - Determine whether events are IN or OUT.

