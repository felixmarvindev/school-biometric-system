"""Service for broadcasting attendance events via WebSocket."""

import logging
from typing import Dict, Set
from datetime import datetime
from fastapi import WebSocket
from collections import defaultdict

logger = logging.getLogger(__name__)


class AttendanceBroadcaster:
    """Manages WebSocket connections and broadcasts attendance events.

    Clients connect to ``/ws/attendance?token=<jwt>`` and receive live
    attendance events for their school.
    """

    def __init__(self):
        self._connections: Dict[int, Set[WebSocket]] = defaultdict(set)

    def register(self, websocket: WebSocket, school_id: int):
        """Register an already-accepted WebSocket for a school."""
        self._connections[school_id].add(websocket)
        logger.info(
            "Attendance WS registered for school %d (total: %d)",
            school_id,
            len(self._connections[school_id]),
        )

    def disconnect(self, websocket: WebSocket, school_id: int):
        """Unregister a WebSocket connection."""
        if school_id in self._connections:
            self._connections[school_id].discard(websocket)
            if not self._connections[school_id]:
                del self._connections[school_id]

    async def broadcast_events(
        self,
        school_id: int,
        events: list[dict],
    ):
        """
        Broadcast a batch of attendance events to all connected clients.

        Args:
            school_id: School ID.
            events: List of enriched event dicts (id, student_name, admission_number,
                    class_name, device_name, event_type, occurred_at).
        """
        if not events:
            return

        if school_id not in self._connections:
            logger.debug(
                "No attendance WS clients for school %d — skip %d events",
                school_id,
                len(events),
            )
            return

        message = {
            "type": "attendance_events",
            "events": [
                {
                    "id": e["id"],
                    "student_id": e.get("student_id"),
                    "student_name": e.get("student_name"),
                    "admission_number": e.get("admission_number"),
                    "class_name": e.get("class_name"),
                    "device_id": e.get("device_id"),
                    "device_name": e.get("device_name"),
                    "event_type": e.get("event_type"),
                    "occurred_at": e["occurred_at"].isoformat() if hasattr(e["occurred_at"], "isoformat") else str(e["occurred_at"]),
                }
                for e in events
            ],
            "count": len(events),
            "timestamp": datetime.utcnow().isoformat(),
        }

        disconnected: Set[WebSocket] = set()

        for ws in self._connections[school_id]:
            try:
                await ws.send_json(message)
            except Exception as exc:
                logger.warning("Error sending attendance event: %s", exc)
                disconnected.add(ws)

        for ws in disconnected:
            self.disconnect(ws, school_id)

        active = len(self._connections.get(school_id, set()))
        logger.debug(
            "Broadcast %d attendance events to %d clients (school %d)",
            len(events),
            active,
            school_id,
        )

    def get_connection_count(self, school_id: int | None = None) -> int:
        """Get the number of active connections."""
        if school_id is not None:
            return len(self._connections.get(school_id, set()))
        return sum(len(c) for c in self._connections.values())


# Global broadcaster instance
attendance_broadcaster = AttendanceBroadcaster()
