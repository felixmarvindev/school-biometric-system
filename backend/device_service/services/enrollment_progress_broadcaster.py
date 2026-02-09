"""Service for broadcasting enrollment progress updates via WebSocket."""

import logging
from typing import Dict, Set, Optional
from datetime import datetime
from fastapi import WebSocket
from collections import defaultdict

logger = logging.getLogger(__name__)


class EnrollmentProgressBroadcaster:
    """Manages WebSocket connections and broadcasts enrollment progress updates."""
    
    def __init__(self):
        """Initialize the broadcaster."""
        # Store active WebSocket connections grouped by school_id
        self._connections: Dict[int, Set[WebSocket]] = defaultdict(set)
    
    def register(self, websocket: WebSocket, school_id: int):
        """
        Register an already-accepted WebSocket connection for a school.
        
        Args:
            websocket: WebSocket connection (must be already accepted)
            school_id: School ID to filter updates
        """
        self._connections[school_id].add(websocket)
        logger.info(f"Enrollment WebSocket registered for school {school_id} (total: {len(self._connections[school_id])})")
    
    def disconnect(self, websocket: WebSocket, school_id: int):
        """
        Unregister a WebSocket connection.
        
        Args:
            websocket: WebSocket connection to remove
            school_id: School ID
        """
        if school_id in self._connections:
            self._connections[school_id].discard(websocket)
            if not self._connections[school_id]:
                del self._connections[school_id]
            logger.info(f"Enrollment WebSocket disconnected for school {school_id} (remaining: {len(self._connections.get(school_id, []))})")
    
    async def broadcast_progress(
        self,
        school_id: int,
        session_id: str,
        progress: int,  # 0, 33, 66, 100
        status: str,  # "ready", "placing", "capturing", "processing", "complete"
        message: str,
    ):
        """
        Broadcast enrollment progress update to all connected clients for a school.
        
        Args:
            school_id: School ID
            session_id: Enrollment session ID
            progress: Progress percentage (0, 33, 66, 100)
            status: Enrollment status ("ready", "placing", "capturing", "processing", "complete")
            message: Status message
        """
        if school_id not in self._connections:
            logger.debug(
                f"No WebSocket clients for school {school_id} - skip broadcast "
                f"(session={session_id}, status={status})"
            )
            return

        event = {
            "type": "enrollment_progress",
            "session_id": session_id,
            "progress": progress,
            "status": status,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        # Collect disconnected websockets to remove
        disconnected: Set[WebSocket] = set()
        
        # Send to all connected clients for this school
        for websocket in self._connections[school_id]:
            try:
                await websocket.send_json(event)
            except Exception as e:
                logger.warning(f"Error sending enrollment progress update: {e}")
                disconnected.add(websocket)
        
        # Clean up disconnected clients
        for ws in disconnected:
            self.disconnect(ws, school_id)
        
        logger.info(
            f"Broadcast enrollment progress: school={school_id}, "
            f"session={session_id}, progress={progress}%, status={status} "
            f"(sent to {len(self._connections[school_id]) - len(disconnected)} clients, "
            f"total connections: {len(self._connections[school_id])})"
        )
    
    async def broadcast_completion(
        self,
        school_id: int,
        session_id: str,
        message: str = "Enrollment completed successfully",
        quality_score: Optional[int] = None,
    ):
        """
        Broadcast enrollment completion event.
        
        Args:
            school_id: School ID
            session_id: Enrollment session ID
            message: Completion message
            quality_score: Optional quality score (0-100)
        """
        if school_id not in self._connections:
            return
        
        event = {
            "type": "enrollment_complete",
            "session_id": session_id,
            "progress": 100,
            "status": "complete",
            "message": message,
            "quality_score": quality_score,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        disconnected: Set[WebSocket] = set()
        
        for websocket in self._connections[school_id]:
            try:
                await websocket.send_json(event)
            except Exception as e:
                logger.warning(f"Error sending enrollment completion: {e}")
                disconnected.add(websocket)
        
        for ws in disconnected:
            self.disconnect(ws, school_id)
        
        logger.info(
            f"Broadcast enrollment completion: school={school_id}, "
            f"session={session_id} "
            f"(sent to {len(self._connections[school_id]) - len(disconnected)} clients, "
            f"total connections: {len(self._connections[school_id])})"
        )
    
    async def broadcast_cancelled(
        self,
        school_id: int,
        session_id: str,
        message: str = "Enrollment cancelled",
    ):
        """
        Broadcast enrollment cancellation event.

        Args:
            school_id: School ID
            session_id: Enrollment session ID
            message: Cancellation message
        """
        if school_id not in self._connections:
            return

        event = {
            "type": "enrollment_cancelled",
            "session_id": session_id,
            "status": "cancelled",
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
        }

        disconnected: Set[WebSocket] = set()

        for websocket in self._connections[school_id]:
            try:
                await websocket.send_json(event)
            except Exception as e:
                logger.warning(f"Error sending enrollment cancellation: {e}")
                disconnected.add(websocket)

        for ws in disconnected:
            self.disconnect(ws, school_id)

        logger.info(
            f"Broadcast enrollment cancelled: school={school_id}, "
            f"session={session_id} "
            f"(sent to {len(self._connections[school_id]) - len(disconnected)} clients)"
        )

    async def broadcast_error(
        self,
        school_id: int,
        session_id: str,
        error_message: str,
    ):
        """
        Broadcast enrollment error event.
        
        Args:
            school_id: School ID
            session_id: Enrollment session ID
            error_message: Error message
        """
        if school_id not in self._connections:
            return
        
        event = {
            "type": "enrollment_error",
            "session_id": session_id,
            "status": "error",
            "error": error_message,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        disconnected: Set[WebSocket] = set()
        
        for websocket in self._connections[school_id]:
            try:
                await websocket.send_json(event)
            except Exception as e:
                logger.warning(f"Error sending enrollment error: {e}")
                disconnected.add(websocket)
        
        for ws in disconnected:
            self.disconnect(ws, school_id)
        
        logger.warning(
            f"Broadcast enrollment error: school={school_id}, "
            f"session={session_id}, error={error_message} "
            f"(sent to {len(self._connections[school_id]) - len(disconnected)} clients, "
            f"total connections: {len(self._connections[school_id])})"
        )
    
    def get_connection_count(self, school_id: Optional[int] = None) -> int:
        """
        Get the number of active connections.
        
        Args:
            school_id: Optional school ID to filter by
        
        Returns:
            Number of active connections
        """
        if school_id is not None:
            return len(self._connections.get(school_id, []))
        return sum(len(conns) for conns in self._connections.values())


# Global broadcaster instance
enrollment_broadcaster = EnrollmentProgressBroadcaster()
