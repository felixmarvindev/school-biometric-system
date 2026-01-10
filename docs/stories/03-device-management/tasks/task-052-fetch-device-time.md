# Task 052: Fetch Device Time (CMD_GET_TIME)

## Story
Story 03: Device Management - Phase 3: Real Device Integration

## Task Type
Backend - Device Communication

## Duration Estimate
0.5 day

## Description

Implement functionality to fetch device time directly from a real ZKTeco device using the `CMD_GET_TIME` command. This is useful for verifying device clock synchronization and debugging attendance time issues.

## Prerequisites

- ✅ Task 048 complete (device connection service working)
- ✅ Real device available for testing

## Acceptance Criteria

- [x] Can fetch device time from real device using CMD_GET_TIME
- [x] Device time is returned in API response
- [x] Device time is displayed in UI (device detail page)
- [x] Time format is correct (ISO 8601 or datetime)
- [x] Error handling for devices that don't support time queries
- [x] Time comparison with server time is possible (optional)

## Implementation Details

### Files to Modify

1. **backend/device_service/services/device_info_service.py**
   - Add `fetch_device_time()` method
   - Use CMD_GET_TIME command

2. **backend/device_service/api/routes/devices.py**
   - Add endpoint: `GET /api/v1/devices/{device_id}/time`
   - Add to device info endpoint

3. **backend/device_service/schemas/device.py**
   - Add device_time to device info response schema

### Key Code Patterns

```python
# backend/device_service/services/device_info_service.py
from datetime import datetime
from device_service.zk.const import CMD_GET_TIME
import asyncio

async def fetch_device_time(self, device: Device) -> Optional[datetime]:
    """
    Fetch current device time from real device using CMD_GET_TIME.
    
    Args:
        device: Device model instance
        
    Returns:
        Device datetime or None if unavailable
    """
    conn = await self.connection_service.get_connection(device)
    if not conn:
        logger.error(f"Cannot connect to device {device.id} to fetch time")
        return None
    
    try:
        # ZKTeco library method - may have helper or need to send command
        # Option 1: If library provides helper
        device_time = await asyncio.to_thread(conn.get_time)
        
        # Option 2: If need to send command manually
        # response = await asyncio.to_thread(conn.send_command, CMD_GET_TIME)
        # device_time = self._parse_time_response(response)
        
        if device_time:
            logger.info(f"Fetched time {device_time} from device {device.id}")
            return device_time
        else:
            return None
            
    except Exception as e:
        logger.error(f"Error fetching time from device {device.id}: {e}")
        return None

def _parse_time_response(self, response: bytes) -> Optional[datetime]:
    """
    Parse time response from device.
    
    Args:
        response: Raw response bytes from device
        
    Returns:
        Parsed datetime or None
    """
    # Parse based on ZKTeco protocol response format
    # ZKTeco devices typically return time in specific format
    # Adjust based on actual library/response format
    try:
        # Example parsing (adjust based on actual format)
        pass
    except Exception as e:
        logger.error(f"Error parsing time response: {e}")
        return None
```

### API Endpoint

```python
@router.get(
    "/{device_id}/time",
    summary="Get device time",
    description="Fetch current device time directly from the device",
    responses={
        200: {"description": "Device time retrieved"},
        404: {"description": "Device not found"},
        503: {"description": "Device connection failed"},
    },
)
async def get_device_time(
    device_id: int = Path(...),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fetch device time from real device."""
    # Implementation
    device_service = DeviceService(db)
    device = await device_service.get_device_by_id(device_id, current_user.school_id)
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    info_service = DeviceInfoService(db, connection_service)
    device_time = await info_service.fetch_device_time(device)
    
    if device_time is None:
        raise HTTPException(
            status_code=503,
            detail="Could not fetch time from device. Device may be offline."
        )
    
    return {
        "device_time": device_time.isoformat(),
        "server_time": datetime.utcnow().isoformat(),
        "time_difference_seconds": (datetime.utcnow() - device_time).total_seconds(),
    }
```

## Testing

### Manual Testing Steps

1. **Fetch Device Time**
   - Navigate to device detail page
   - Click "Get Device Time" or view in device info
   - Verify device time is displayed
   - Verify time format is readable

2. **Test Time Comparison**
   - Fetch device time
   - Compare with server time
   - Verify time difference is displayed (if implemented)
   - Check if time zones are handled correctly

3. **Test Error Cases**
   - Try fetching time from offline device
   - Verify appropriate error messages

### Expected Results

- Device time is fetched successfully from online device
- Time is displayed in readable format
- Time comparison works (if implemented)
- Error handling works for unavailable devices
- Time format is consistent (ISO 8601)

## Definition of Done

- [x] Device time can be fetched from real device using CMD_GET_TIME
- [x] Device time is returned in API response
- [x] Device time is displayed in UI
- [x] Time format is correct
- [x] Error handling implemented
- [x] API endpoint created and tested
- [x] Logging added
- [x] Documentation updated

## Notes

- **Time Format**: ZKTeco devices may return time in different formats - ensure proper parsing
- **Time Zone**: Consider timezone handling - devices may use local time or UTC
- **Library Support**: Check if ZKTeco library provides helper method for time, or if manual command is needed
- **Use Case**: Device time is mainly for debugging/synchronization - may not need to be stored persistently
- **Future**: Consider implementing CMD_SET_TIME to sync device time with server

## Dependencies

- Depends on: Task 048
- Part of: Device info fetching suite
- Optional enhancement: Can add time sync functionality later
