# Task 048: Device Connection Service (Real Device)

## Story
Story 03: Device Management - Phase 3: Real Device Integration

## Task Type
Backend - Service Layer

## Duration Estimate
1 day

## Description

Create a comprehensive device connection service that manages real ZKTeco device connections, handles connection pooling, retries, and provides a clean interface for device operations.

## Prerequisites

- ✅ Task 047 complete (ZKTeco library integrated)
- ✅ Real device available for testing

## Acceptance Criteria

- [x] Device connection service manages connections properly ✅
- [x] Connection pooling/reuse implemented ✅
- [x] Connection timeout handling ✅
- [x] Service can be used by other services (dependency injection) ✅
- [x] Connection status can be checked ✅
- [x] Multiple concurrent connections supported ✅
- [x] Real ZKTeco protocol connection testing implemented ✅

## Implementation Details

### Files to Create/Modify

1. **backend/device_service/services/device_connection_service.py**
   - DeviceConnectionService class
   - Connection management
   - Connection pool/registry
   - Retry logic

2. **backend/device_service/api/dependencies.py** (update)
   - Add dependency for device connection service
   - Connection service injection

### Key Code Patterns

```python
# backend/device_service/services/device_connection_service.py
from typing import Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from device_service.models.device import Device
from device_service.services.device_connection import RealDeviceConnection
import logging

logger = logging.getLogger(__name__)

class DeviceConnectionService:
    """Service for managing device connections."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._connections: Dict[int, RealDeviceConnection] = {}
    
    async def get_connection(self, device: Device) -> Optional[RealDeviceConnection]:
        """
        Get or create a connection to a device.
        
        Args:
            device: Device model instance
            
        Returns:
            RealDeviceConnection instance or None if connection fails
        """
        # Check if connection exists and is still valid
        if device.id in self._connections:
            conn = self._connections[device.id]
            # Test if connection is still alive
            if await self._test_connection(conn):
                return conn
            else:
                # Remove stale connection
                del self._connections[device.id]
        
        # Create new connection
        conn = RealDeviceConnection(
            ip=device.ip_address,
            port=device.port,
            password=int(device.com_password) if device.com_password else None
        )
        
        if await conn.connect():
            self._connections[device.id] = conn
            return conn
        else:
            return None
    
    async def _test_connection(self, conn: RealDeviceConnection) -> bool:
        """Test if connection is still active."""
        # Try a simple command to test connection
        try:
            # This will be implemented when we have device commands
            return True
        except Exception:
            return False
    
    async def disconnect_device(self, device_id: int):
        """Disconnect from a device."""
        if device_id in self._connections:
            conn = self._connections[device_id]
            await conn.disconnect()
            del self._connections[device_id]
    
    async def disconnect_all(self):
        """Disconnect from all devices."""
        for device_id, conn in list(self._connections.items()):
            await conn.disconnect()
        self._connections.clear()
```

## Testing

### Manual Testing Steps

1. **Test Connection Retrieval**
   - Get connection for existing device
   - Verify connection is established
   - Check connection reuse on subsequent calls

2. **Test Connection Pooling**
   - Connect to multiple devices
   - Verify each has its own connection
   - Verify connections are reused

3. **Test Disconnection**
   - Disconnect from device
   - Verify connection is removed from pool
   - Verify reconnection works

### Expected Results

- Connections are established successfully
- Connections are reused when appropriate
- Failed connections are handled gracefully
- Connection pool is managed correctly

## Definition of Done

- [x] Device connection service implemented
- [x] Connection pooling/reuse working
- [x] Connection retry logic implemented
- [x] Service can be injected as dependency
- [x] Connection status checking works
- [x] Multiple concurrent connections supported
- [x] Error handling and logging added
- [x] Unit tests created (if applicable)

## Notes

- **Connection Lifecycle**: Consider when to close connections (on API request end, after timeout, etc.)
- **Error Handling**: Ensure failed connections don't block other operations
- **Resource Management**: Clean up connections properly to avoid resource leaks
- **Thread Safety**: If using connection pool, ensure thread-safe operations

## Dependencies

- Depends on: Task 047
- Blocks: Task 049, 050, 051, 052 (all device info fetching tasks)
