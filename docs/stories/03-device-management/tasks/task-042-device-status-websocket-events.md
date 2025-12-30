# Task 042: Device Status WebSocket Events

## Story/Phase
- **Story**: Story 03: Device Management
- **Phase**: Phase 3: Device Monitoring

## Description

Implement WebSocket events to push real-time device status updates to connected clients.

## Type
- [x] Backend
- [ ] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Acceptance Criteria

1. [ ] WebSocket connection endpoint exists
2. [ ] Clients can subscribe to device status updates
3. [ ] Status updates broadcast when device status changes
4. [ ] Events include device_id, status, last_seen
5. [ ] Authentication required for WebSocket connection
6. [ ] Only broadcasts devices from user's school
7. [ ] Handles client disconnections gracefully
8. [ ] WebSocket events documented

## Technical Details

### Files to Create/Modify

```
backend/device_service/api/routes/websocket.py
backend/device_service/services/device_status_broadcaster.py
backend/device_service/api/dependencies.py (add websocket auth)
```

### Key Code Patterns

```python
# routes/websocket.py
from fastapi import WebSocket, WebSocketDisconnect, Depends
from typing import Dict, Set
from device_service.services.device_status_broadcaster import DeviceStatusBroadcaster
from device_service.api.dependencies import get_current_user_ws
import json

# Store active connections per school
active_connections: Dict[int, Set[WebSocket]] = {}

router = APIRouter()

@router.websocket("/ws/device-status")
async def device_status_websocket(
    websocket: WebSocket,
    current_user = Depends(get_current_user_ws)
):
    """
    WebSocket endpoint for real-time device status updates.
    
    Clients receive events when device status changes.
    """
    await websocket.accept()
    
    school_id = current_user.school_id
    
    # Add connection to active connections
    if school_id not in active_connections:
        active_connections[school_id] = set()
    active_connections[school_id].add(websocket)
    
    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to device status updates",
            "school_id": school_id
        })
        
        # Keep connection alive and handle messages
        while True:
            data = await websocket.receive_text()
            # Handle client messages if needed (ping/pong, etc.)
            
    except WebSocketDisconnect:
        # Remove connection when client disconnects
        if school_id in active_connections:
            active_connections[school_id].discard(websocket)
            if not active_connections[school_id]:
                del active_connections[school_id]

# Broadcast function called by health check service
async def broadcast_device_status(school_id: int, device_id: int, status: str, last_seen: str):
    """Broadcast device status update to connected clients."""
    if school_id not in active_connections:
        return
    
    message = {
        "type": "device_status_update",
        "device_id": device_id,
        "status": status,
        "last_seen": last_seen,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Send to all connected clients for this school
    disconnected = set()
    for websocket in active_connections[school_id]:
        try:
            await websocket.send_json(message)
        except Exception as e:
            # Connection closed, remove it
            disconnected.add(websocket)
    
    # Clean up disconnected clients
    active_connections[school_id] -= disconnected
```

### Dependencies

- Task 041 (Health check service - broadcasts status updates)
- Task 011 (Authentication must work - WebSocket auth)

## Visual Testing

### Before State
- No real-time status updates
- Must refresh page to see status changes

### After State
- WebSocket connection established
- Status updates received in real-time
- UI updates automatically

### Testing Steps

1. Connect WebSocket client
2. Verify connection confirmation
3. Trigger device status change
4. Verify status update received
5. Test multiple clients
6. Test disconnection handling

## Definition of Done

- [ ] Code written and follows standards
- [ ] WebSocket endpoint implemented
- [ ] Authentication works
- [ ] Status updates broadcast correctly
- [ ] School-level scoping verified
- [ ] Disconnection handling tested
- [ ] Unit tests written and passing
- [ ] Code reviewed

## Time Estimate

4-5 hours

## Notes

- Use FastAPI WebSocket support
- WebSocket authentication via query params or headers
- Store connections in memory (consider Redis for multi-instance)
- Broadcast only to relevant school's connections
- Handle connection cleanup on disconnect
- Consider heartbeat/ping-pong for connection keepalive

