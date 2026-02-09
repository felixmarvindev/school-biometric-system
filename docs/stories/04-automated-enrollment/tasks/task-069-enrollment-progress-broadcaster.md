# Task 069: Enrollment Progress Broadcaster

## Story/Phase
- **Story**: Story 04: Automated Enrollment
- **Phase**: Phase 3: Real-time Progress

## Description

Create a WebSocket broadcaster service to emit enrollment progress events (0%, 33%, 66%, 100%) to connected clients.

## Type
- [x] Backend
- [ ] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Duration Estimate
1 day

## Prerequisites

- ✅ WebSocket infrastructure exists (from device status)
- ✅ Task 066 complete (enrollment command handler)

## Acceptance Criteria

1. [x] Enrollment progress broadcaster service created
2. [x] Can emit progress events (0%, 33%, 66%, 100%)
3. [x] Events include: session_id, progress, status, message
4. [x] Events filtered by school_id
5. [x] Completion event emitted on success
6. [x] Error event emitted on failure

## Implementation Details

### Backend Changes

1. **backend/device_service/services/enrollment_progress_broadcaster.py**
   - Create EnrollmentProgressBroadcaster class
   - Add `broadcast_progress()` method
   - Add `broadcast_completion()` method
   - Add `broadcast_error()` method

2. **backend/device_service/api/routes/websocket.py** (extend existing)
   - Add enrollment progress event handling
   - Register enrollment WebSocket connections

### Key Code Patterns

```python
# backend/device_service/services/enrollment_progress_broadcaster.py
from typing import Dict, Set
from fastapi import WebSocket
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class EnrollmentProgressBroadcaster:
    """Manages WebSocket connections and broadcasts enrollment progress."""
    
    def __init__(self):
        self._connections: Dict[int, Set[WebSocket]] = defaultdict(set)
    
    def register(self, websocket: WebSocket, school_id: int):
        """Register WebSocket connection for enrollment updates."""
        self._connections[school_id].add(websocket)
    
    async def broadcast_progress(
        self,
        school_id: int,
        session_id: str,
        progress: int,  # 0, 33, 66, 100
        status: str,  # "ready", "placing", "capturing", "complete"
        message: str,
    ):
        """Broadcast enrollment progress update."""
        if school_id not in self._connections:
            return
        
        event = {
            "type": "enrollment_progress",
            "session_id": session_id,
            "progress": progress,
            "status": status,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        disconnected = set()
        for ws in self._connections[school_id]:
            try:
                await ws.send_json(event)
            except Exception as e:
                logger.warning(f"Error sending progress update: {e}")
                disconnected.add(ws)
        
        for ws in disconnected:
            self._connections[school_id].discard(ws)
```

## Testing

### Manual Testing

1. **Progress Broadcasting**
   - Start enrollment
   - ✅ Verify progress events emitted
   - ✅ Verify events received by WebSocket clients

## Definition of Done

- [x] Progress broadcaster created
- [x] Can emit progress events
- [x] Events filtered by school
- [x] Error handling works

## Next Task

**Task 070: Enrollment Progress UI Component** - Create frontend component to display progress.
