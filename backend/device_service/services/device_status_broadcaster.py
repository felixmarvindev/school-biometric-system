"""Service for broadcasting device status updates via WebSocket."""

import logging
from typing import Dict, Set, Optional
from datetime import datetime
from fastapi import WebSocket
from collections import defaultdict

logger = logging.getLogger(__name__)


class DeviceStatusBroadcaster:
    """Manages WebSocket connections and broadcasts device status updates."""
    
    def __init__(self):
        """Initialize the broadcaster."""
        # Store active WebSocket connections grouped by school_id
        self._connections: Dict[int, Set[WebSocket]] = defaultdict(set)
    
    async def connect(self, websocket: WebSocket, school_id: int):
        """
        Register a WebSocket connection for a school.
        
        NOTE: WebSocket must already be accepted before calling this method.
        
        Args:
            websocket: WebSocket connection (must be already accepted)
            school_id: School ID to filter updates
        """
        # Don't accept here - should be accepted before calling this
        self._connections[school_id].add(websocket)
        logger.info(f"WebSocket registered for school {school_id} (total: {len(self._connections[school_id])})")
    
    def register(self, websocket: WebSocket, school_id: int):
        """
        Register an already-accepted WebSocket connection for a school.
        
        Args:
            websocket: WebSocket connection (must be already accepted)
            school_id: School ID to filter updates
        """
        self._connections[school_id].add(websocket)
        logger.info(f"WebSocket registered for school {school_id} (total: {len(self._connections[school_id])})")
    
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
            logger.info(f"WebSocket disconnected for school {school_id} (remaining: {len(self._connections.get(school_id, []))})")
    
    async def broadcast_device_status(
        self,
        school_id: int,
        device_id: int,
        status: str,
        last_seen: Optional[datetime] = None,
    ):
        """
        Broadcast device status update to all connected clients for a school.
        
        Args:
            school_id: School ID
            device_id: Device ID
            status: Device status ("online", "offline", "unknown")
            last_seen: Optional last_seen timestamp
        """
        if school_id not in self._connections:
            return  # No connected clients for this school
        
        message = {
            "type": "device_status_update",
            "device_id": device_id,
            "status": status,
            "last_seen": last_seen.isoformat() if last_seen else None,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        # Collect disconnected websockets to remove
        disconnected: Set[WebSocket] = set()
        
        # Send to all connected clients for this school
        for websocket in self._connections[school_id]:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.warning(f"Error sending WebSocket message: {e}")
                disconnected.add(websocket)
        
        # Clean up disconnected clients
        for ws in disconnected:
            self.disconnect(ws, school_id)
        
        logger.debug(
            f"Broadcast device status update: school={school_id}, "
            f"device={device_id}, status={status} "
            f"(sent to {len(self._connections[school_id]) - len(disconnected)} clients)"
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
broadcaster = DeviceStatusBroadcaster()

