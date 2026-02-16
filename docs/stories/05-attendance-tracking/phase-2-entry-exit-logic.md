# Phase 2: Entry/Exit Logic

## Goal

Automatically determine whether an attendance event is an IN (entry) or OUT (exit) based on the student's previous attendance record.

## Duration Estimate

3-4 days

## Prerequisites

- ✅ Phase 1 complete (events being captured)

## Tasks

| # | Task | Description | Status |
|---|------|-------------|--------|
| 060 | [Add event_type to Attendance Model](tasks/task-060-add-event-type-to-attendance-model.md) | Add `event_type` column (IN/OUT/UNKNOWN) to model, schema, and DB | ✅ Done (migration pending) |
| 061 | [Student Matching Service](tasks/task-061-student-matching-service.md) | Resolve `device_user_id` → `student_id` using sync mapping | ✅ Done |
| 062 | [Entry/Exit Determination Service](tasks/task-062-entry-exit-determination-service.md) | Core IN/OUT logic based on previous record + configurable duplicate window | ✅ Done |
| 063 | [Integrate Entry/Exit into Ingestion](tasks/task-063-integrate-entry-exit-into-ingestion.md) | Wire matching + determination into the ingestion pipeline | ✅ Done |

### Task Dependencies

```
060 ──┐
      ├──► 063
061 ──┤
      │
062 ──┘
```

Tasks 060, 061, and 062 can be worked on in parallel. Task 063 depends on all three.

## Entry/Exit Rules

| Scenario | Previous Record | Time Gap | Result |
|---|---|---|---|
| First tap of the day | None | — | **IN** |
| After an IN | IN | > 30 min (configurable) | **OUT** |
| After an OUT | OUT | > 30 min (configurable) | **IN** |
| Rapid re-tap | Any | < 30 min (configurable) | **DUPLICATE** (skip) |
| Unmatched student | — | — | **UNKNOWN** |

## Configuration

| Setting | Default | Description |
|---|---|---|
| `ATTENDANCE_DUPLICATE_WINDOW_MINUTES` | 30 | Minutes within which a re-tap is considered a duplicate |
| `ATTENDANCE_TIMEZONE` | Africa/Nairobi | Timezone for "same day" boundary |

## Visual Checkpoints

- [ ] First tap of day is IN
- [ ] Subsequent taps alternate IN/OUT
- [ ] Duplicate taps within 30 mins are ignored
- [ ] Unmatched device users get UNKNOWN event_type
- [ ] Logic works correctly for all scenarios

## Next Phase

**Phase 3: Attendance Display** - Show attendance in real-time dashboard.
