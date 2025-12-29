# Phase 2: Entry/Exit Logic

## Goal

Automatically determine whether an attendance event is an IN (entry) or OUT (exit) based on the student's previous attendance record.

## Duration Estimate

3-4 days

## Prerequisites

- ✅ Phase 1 complete (events being captured)

## Technical Components

### Backend Changes

- [ ] Implement entry/exit determination logic
- [ ] Query last attendance record for student
- [ ] Apply rules:
  - No previous record → IN
  - Last was IN and > 30 mins ago → OUT
  - Last was OUT → IN
  - Last < 30 mins ago → Duplicate (ignore)
- [ ] Store event_type (IN/OUT) with attendance record
- [ ] Handle edge cases

## Visual Checkpoints

- [ ] First tap of day is IN
- [ ] Subsequent taps alternate IN/OUT
- [ ] Duplicate taps within 30 mins are ignored
- [ ] Logic works correctly for all scenarios

## Next Phase

**Phase 3: Attendance Display** - Show attendance in real-time dashboard.

