# Task 066: Attendance Page Layout & Stats Cards

## Story/Phase
- **Story**: Story 05: Attendance Tracking
- **Phase**: Phase 3: Attendance Display

## Task Type
- [ ] Backend
- [x] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Description

Create the main attendance page at `/dashboard/attendance` with the page shell, summary stat cards, and tab switcher (Live Feed / History). This is the container that the live feed and history components plug into.

## Acceptance Criteria

1. [x] Page exists at `/dashboard/attendance` and renders inside the dashboard layout.
2. [x] Four summary stat cards at the top: Total Events, Checked In, Checked Out, Present Rate.
3. [x] Stats load from `GET /api/v1/attendance/stats` on mount and refresh on new WS events.
4. [x] Tab bar below stats with two tabs: "Live Feed" (default) and "History".
5. [x] Tab switching is smooth (AnimatePresence, no full page reload).
6. [x] Page uses standard dashboard animations (fadeInUp, staggered cards).
7. [x] Responsive: stat cards stack 2×2 on mobile.
8. [x] Follows project color system and glassmorphism card styles.

## Notes

- Stats should animate when values change (count-up effect).
- The Live Feed and History tab content are separate components (Tasks 067 and 068).
- Follow the same page structure pattern as the Students list page.
