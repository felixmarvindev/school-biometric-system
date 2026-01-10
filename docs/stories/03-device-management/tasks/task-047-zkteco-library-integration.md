# Task 047: ZKTeco Library Integration Setup

## Story
Story 03: Device Management - Phase 3: Real Device Integration

## Task Type
Backend - Infrastructure

## Duration Estimate
1 day

## Description

Set up the ZKTeco Python library integration and create the foundational device communication infrastructure. This task establishes the connection between our system and real ZKTeco devices.

## Prerequisites

- ✅ Phase 2 complete (device groups working)
- ✅ ZKTeco Python library available (or needs to be installed)
- ✅ Device IP address and port known for testing

## Acceptance Criteria

- [ ] ZKTeco Python library installed and accessible
- [ ] Device communication service structure created
- [ ] Basic device connection can be established
- [ ] Connection errors are handled gracefully
- [ ] Library integration follows async/await patterns
- [ ] Connection can be tested with real device

## Implementation Details

### Files to Create

1. **backend/device_service/zk/base.py** (if library needs wrapper)
   - Device connection class
   - Async wrapper for ZKTeco library calls
   - Connection management

2. **backend/device_service/services/device_connection.py** (update existing or create)
   - Real device connection service
   - Connection pooling/management
   - Error handling

### Files to Modify

1. **backend/device_service/core/config.py**
   - Add device connection timeout settings
   - Add device password configuration
   - Add device connection retry settings

2. **requirements.txt** (backend)
   - Add ZKTeco library dependency (e.g., `zkteco-python` or appropriate package)

### Key Code Patterns

```python
# backend/device_service/services/device_connection.py
from typing import Optional
from zk import ZK
import asyncio
import logging

logger = logging.getLogger(__name__)

class RealDeviceConnection:
    """Service for connecting to real ZKTeco devices."""
    
    def __init__(self, ip: str, port: int = 4370, password: Optional[int] = None):
        self.ip = ip
        self.port = port
        self.password = password or 0
        self.zk = ZK(ip, port, timeout=5, password=self.password, ommit_ping=False)
        self.conn = None
    
    async def connect(self) -> bool:
        """Establish connection to device (async wrapper)."""
        try:
            self.conn = await asyncio.to_thread(self.zk.connect)
            logger.info(f"Connected to device {self.ip}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Connection failed to {self.ip}:{self.port}: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from device."""
        if self.conn:
            await asyncio.to_thread(self.conn.disconnect)
            self.conn = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
```

## Testing

### Manual Testing Steps

1. **Install Library**
   ```bash
   # Install ZKTeco library (example - adjust based on actual library)
   pip install zkteco-python
   # OR install from source if needed
   ```

2. **Test Connection**
   ```python
   # Test script
   async def test_connection():
       device = RealDeviceConnection("192.168.1.100", 4370)
       if await device.connect():
           print("Connection successful!")
           await device.disconnect()
       else:
           print("Connection failed")
   ```

3. **Expected Results**
   - Connection succeeds when device is online
   - Connection fails gracefully when device is offline
   - Connection timeout works correctly
   - Error messages are clear

### Edge Cases to Test

- Device offline
- Wrong IP address
- Wrong port
- Device password incorrect
- Network timeout
- Device already connected from another session

## Definition of Done

- [x] ZKTeco library installed and tested
- [x] Device connection service created
- [x] Can connect to real device successfully
- [x] Connection errors handled with clear messages
- [x] Code follows async/await patterns
- [x] Logging added for connection attempts
- [x] Basic error handling implemented
- [x] Documentation added for library setup

## Notes

- **Library Selection**: Confirm which ZKTeco Python library to use (may need to research or use existing one)
- **Connection Pattern**: Use async/await to avoid blocking the event loop
- **Error Handling**: Make error messages user-friendly and actionable
- **Testing**: Ensure real device is available for testing during this task

## Dependencies

- Blocks: Task 048, 049, 050, 051, 052 (all device info fetching tasks)
- Required by: All real device integration features
