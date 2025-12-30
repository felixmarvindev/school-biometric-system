# Task 034: Device Connection Test API

## Story/Phase
- **Story**: Story 03: Device Management
- **Phase**: Phase 1: Device Registration

## Description

Create the API endpoint for testing device connectivity and updating device status.

## Type
- [x] Backend
- [ ] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Acceptance Criteria

1. [ ] POST `/api/v1/devices/{device_id}/test` endpoint exists
2. [ ] Endpoint requires authentication (JWT token)
3. [ ] Only tests devices from user's school
4. [ ] Attempts TCP connection to device IP/port
5. [ ] Returns connection test results (success/failure)
6. [ ] Updates device status (online/offline) based on test
7. [ ] Updates last_seen timestamp on success
8. [ ] Returns device information if connection successful
9. [ ] Supports timeout configuration
10. [ ] Returns 401 if not authenticated
11. [ ] API endpoint is documented

## Technical Details

### Files to Create/Modify

```
backend/device_service/api/routes/devices.py
backend/device_service/services/device_service.py
backend/device_service/services/device_connection.py
```

### Key Code Patterns

```python
# routes/devices.py
from fastapi import APIRouter, HTTPException, status, Depends, Path
from device_service.api.dependencies import get_current_user, get_db
from shared.schemas.device import DeviceConnectionTest, DeviceConnectionTestResponse
from shared.schemas.auth import UserResponse
from sqlalchemy.ext.asyncio import AsyncSession

@router.post(
    "/{device_id}/test",
    response_model=DeviceConnectionTestResponse,
    summary="Test device connection",
    description="""
    Test connectivity to a biometric device.
    
    Attempts to establish a TCP connection to the device's IP and port.
    Updates device status based on test results.
    """,
    responses={
        200: {"description": "Connection test completed"},
        404: {"description": "Device not found"},
    },
)
async def test_device_connection(
    device_id: int = Path(..., description="Device ID"),
    test_config: DeviceConnectionTest = DeviceConnectionTest(),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Test device connection.
    
    - **Authentication**: Required (JWT token)
    - **Authorization**: Only tests devices from user's school
    """
    from device_service.services.device_service import DeviceService
    from device_service.services.device_connection import DeviceConnectionService
    
    device_service = DeviceService(db)
    connection_service = DeviceConnectionService()
    
    # Get device and verify authorization
    device = await device_service.get_device_by_id(
        device_id=device_id,
        school_id=current_user.school_id
    )
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found",
        )
    
    # Test connection
    import asyncio
    import socket
    from datetime import datetime
    
    start_time = datetime.utcnow()
    
    try:
        # Attempt TCP connection (basic connectivity test)
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(device.ip_address, device.port),
            timeout=test_config.timeout
        )
        writer.close()
        await writer.wait_closed()
        
        # Connection successful
        end_time = datetime.utcnow()
        response_time_ms = int((end_time - start_time).total_seconds() * 1000)
        
        # Update device status
        await device_service.update_device_status(
            device_id=device_id,
            status=DeviceStatus.ONLINE,
            last_seen=datetime.utcnow()
        )
        
        return DeviceConnectionTestResponse(
            success=True,
            message="Connection successful",
            response_time_ms=response_time_ms,
        )
    except (asyncio.TimeoutError, ConnectionRefusedError, OSError) as e:
        # Connection failed
        await device_service.update_device_status(
            device_id=device_id,
            status=DeviceStatus.OFFLINE,
        )
        
        return DeviceConnectionTestResponse(
            success=False,
            message=f"Connection failed: {str(e)}",
        )
```

### Dependencies

- Task 033 (Delete device API - service layer exists)
- Task 028 (Device schemas must exist)

## Visual Testing

### Before State
- Cannot test device connections
- Device status remains unknown

### After State
- Can POST `/api/v1/devices/{id}/test` to test connection
- Device status updated based on test result
- Connection test results returned

### Testing Steps

1. Test without token - verify 401 error
2. Test with valid device (online) - verify success response
3. Test with invalid IP - verify failure response
4. Test with offline device - verify failure response
5. Verify device status updated after test
6. Verify last_seen timestamp updated on success

## Definition of Done

- [ ] Code written and follows standards
- [ ] Unit tests written and passing
- [ ] Connection test logic tested
- [ ] Status update tested
- [ ] Timeout handling tested
- [ ] Authorization verified
- [ ] API documented
- [ ] Code reviewed
- [ ] Tested with real device (if available) or simulated

## Time Estimate

4-5 hours

## Notes

- Basic TCP connection test (not full ZKTeco protocol handshake yet)
- Full protocol connection will be implemented in later tasks
- Timeout should be configurable (default 5 seconds)
- Consider async connection testing to avoid blocking
- Status updates should be atomic (transaction)
- Future: Test can return device information (model, firmware, etc.)

