# Task 068: Attendance History Tab

## Story/Phase
- **Story**: Story 05: Attendance Tracking
- **Phase**: Phase 4: Attendance History

## Task Type
- [ ] Backend
- [x] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Description

Build the History tab content for the attendance page. A filterable, paginated data table showing historical attendance records.

## Acceptance Criteria

1. [ ] Filter bar with: date picker (default today), student search (typeahead), class dropdown, device dropdown, event type toggle (All/IN/OUT).
2. [ ] Data table with columns: Time, Student, Admission #, Class, Device, Type (IN/OUT badge).
3. [ ] Table loads from `GET /api/v1/attendance` with applied filters.
4. [ ] Pagination: "Showing 1–50 of N records" with page controls.
5. [ ] Default sort: newest first. Columns sortable by Time, Student, Class.
6. [ ] Summary text above table: "N records found".
7. [ ] Clicking a student name opens the student detail panel (Task 069).
8. [ ] Empty state when no records match filters.
9. [ ] Responsive: table becomes stacked cards on mobile.
10. [ ] Follows project table/card patterns and color system.

## Notes

- Reuse existing patterns for search inputs and dropdowns from the Students list page.
- Date picker can use a simple input[type=date] or a proper calendar component from shadcn.
- Filters should update the URL query params for shareability.
