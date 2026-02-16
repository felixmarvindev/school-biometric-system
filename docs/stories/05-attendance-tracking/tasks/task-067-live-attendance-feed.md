# Task 067: Live Attendance Feed Component

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

Build the real-time live attendance feed that shows events as they arrive via WebSocket. This is the content of the "Live Feed" tab on the attendance page.

## Acceptance Criteria

1. [x] Subscribes to `attendance_events` WebSocket messages on mount, unsubscribes on unmount.
2. [x] New events slide in at the top of the list with a fade-in animation.
3. [x] Each event row shows: IN/OUT badge (green/amber), student name, admission number, class, device name, timestamp.
4. [x] Events have a colored left border accent (green for IN, amber for OUT, gray for UNKNOWN).
5. [x] New events prepend to top (newest first).
6. [x] "Pause" toggle button to pause live event prepending.
7. [ ] Device filter dropdown ("All Devices" / specific device). — Follow-up.
8. [x] Pulsing green dot in header indicating live WebSocket connection.
9. [x] Connection lost banner (amber) when WebSocket disconnects, with reconnect indicator.
10. [x] Empty state when no events yet: icon + message.
11. [x] Loads recent events from API on initial mount (last ~50 for today) as seed data.
12. [x] Responsive and works in dark mode.

## Notes

- Check existing WebSocket hook patterns in the enrollment feature (`useEnrollmentProgress`).
- Events should be deduplicated client-side (by `id`) in case of reconnection replays.
- Keep a max of ~200 events in memory to prevent memory growth.
