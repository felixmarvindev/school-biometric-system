# Task 069: Student Attendance Detail Panel

## Story/Phase
- **Story**: Story 05: Attendance Tracking
- **Phase**: Phase 4: Attendance History

## Task Type
- [x] Backend
- [x] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Description

A slide-out panel (or modal) showing a single student's attendance for a given day. Opens when clicking a student name in the live feed or history table. Includes a vertical timeline of their IN/OUT events and quick stats.

## Acceptance Criteria

1. [ ] Panel slides in from the right (~400px wide) or opens as a modal.
2. [ ] Header: student name, admission number, class, initials avatar.
3. [ ] Vertical timeline of the student's events for the day (green dots for IN, amber for OUT, connecting lines).
4. [ ] Duration labels between events (e.g. "4h 17m").
5. [ ] Quick stats below timeline: total time in school, first check-in, last event.
6. [ ] Loads data from `GET /api/v1/attendance/students/{student_id}?date=YYYY-MM-DD`.
7. [ ] Close button and click-outside-to-close behavior.
8. [ ] Responsive and works in dark mode.

## Notes

- This is a nice-to-have enhancement. If time is tight, it can be deferred.
- The timeline component could be reusable for other contexts (e.g. student profile page).
- Total time calculation: sum durations between consecutive IN→OUT pairs.
