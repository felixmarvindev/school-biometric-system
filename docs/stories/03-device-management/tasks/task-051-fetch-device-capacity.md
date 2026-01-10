# Task 051: Fetch Device Capacity (CMD_GET_FREE_SIZES)

## Story
Story 03: Device Management - Phase 3: Real Device Integration

## Task Type
Backend - Device Communication

## Duration Estimate
1 day

## Description

Implement functionality to fetch device capacity (max_users) directly from a real ZKTeco device using the `CMD_GET_FREE_SIZES` command. This replaces the simulated capacity with real device data.

## Prerequisites

- ✅ Task 048 complete (device connection service working)
- ✅ Real device available for testing

## Acceptance Criteria

- [ ] Can fetch device capacity (max_users) from real device using CMD_GET_FREE_SIZES
- [ ] Capacity is returned in API response
- [ ] Capacity is stored in device.max_users field in database
- [ ] Existing `refresh_device_capacity` endpoint uses real device data
- [ ] Error handling for devices that don't support capacity queries
- [ ] Capacity is displayed in UI
- [ ] Capacity refresh works from device detail page

## Implementation Details

### Files to Modify

1. **backend/device_service/services/device_capacity.py**
   - Update `refresh_device_capacity()` to fetch from real device
   - Implement `_fetch_capacity_from_device()` method

2. **backend/device_service/services/device_info_service.py**
   - Add `fetch_device_capacity()` method
   - Use CMD_GET_FREE_SIZES command

3. **backend/device_service/api/routes/devices.py**
   - Update `refresh_device_capacity` endpoint to use real device

### Key Code Patterns

```python
# backend/device_service/services/device_capacity.py
from device_service.services.device_connection_service import DeviceConnectionService
from device_service.zk.const import CMD_GET_FREE_SIZES
import asyncio
import logging

logger = logging.getLogger(__name__)

async def _fetch_capacity_from_device(self, device: Device) -> Optional[int]:
    """
    Fetch max_users capacity from real device using CMD_GET_FREE_SIZES.
    
    Args:
        device: Device model instance
        
    Returns:
        Max users capacity or None if unavailable
    """
    connection_service = DeviceConnectionService(self.db)
    conn = await connection_service.get_connection(device)
    
    if not conn:
        logger.error(f"Cannot connect to device {device.id} to fetch capacity")
        return None
    
    try:
        # Send CMD_GET_FREE_SIZES command
        # Response format may vary - parse accordingly
        response = await asyncio.to_thread(
            conn.send_command,
            CMD_GET_FREE_SIZES
        )
        
        # Parse response to extract max_users
        # Response format example: {"users": 1000, "fingerprints": 3000, ...}
        # Adjust parsing based on actual response format
        max_users = self._parse_capacity_response(response)
        
        if max_users:
            logger.info(f"Fetched capacity {max_users} from device {device.id}")
            return max_users
        else:
            logger.warning(f"Could not parse capacity from device {device.id} response")
            return None
            
    except Exception as e:
        logger.error(f"Error fetching capacity from device {device.id}: {e}")
        return None

def _parse_capacity_response(self, response: bytes) -> Optional[int]:
    """
    Parse capacity response from device.
    
    Args:
        response: Raw response bytes from device
        
    Returns:
        Max users capacity or None
    """
    # Parse based on ZKTeco protocol response format
    # This will need to be adjusted based on actual library/response format
    try:
        # Example parsing (adjust based on actual format)
        # If library provides parsed response, use that instead
        # If raw bytes, parse according to ZKTeco protocol
        pass
    except Exception as e:
        logger.error(f"Error parsing capacity response: {e}")
        return None

async def refresh_device_capacity(self, device_id: int) -> Optional[Dict[str, Any]]:
    """
    Refresh capacity from real device and update database.
    
    Now uses real device communication instead of simulation.
    """
    device = await self.repository.get_by_id(device_id)
    
    if not device:
        return None
    
    # Fetch from real device
    max_users = await self._fetch_capacity_from_device(device)
    
    if max_users is not None:
        device.max_users = max_users
        await self.db.commit()
        await self.db.refresh(device)
        logger.info(f"Updated device {device_id} capacity to {max_users}")
    else:
        logger.warning(f"Could not fetch capacity from device {device_id}, keeping existing value")
    
    return await self.get_device_capacity(device_id)
```

## Testing

### Manual Testing Steps

1. **Refresh Capacity**
   - Navigate to device detail page
   - Click "Refresh Capacity" button
   - Verify max_users is fetched from real device
   - Verify capacity is updated in database
   - Verify capacity is displayed in UI

2. **Test During Registration**
   - Register new device
   - Click "Fetch Device Info"
   - Verify capacity is fetched and displayed
   - Verify capacity is saved to database

3. **Test Error Cases**
   - Try refreshing from offline device
   - Verify appropriate error message
   - Verify existing capacity is preserved if fetch fails

4. **Verify Capacity Calculation**
   - Check device capacity on device itself (if accessible)
   - Verify fetched capacity matches device capacity
   - Verify enrolled_users vs max_users calculation is correct

### Expected Results

- Capacity is fetched successfully from online device
- Capacity matches device's actual max_users setting
- Capacity is stored in database (device.max_users)
- Capacity is displayed correctly in UI
- Capacity refresh works from multiple locations
- Error handling works for unavailable devices

## Definition of Done

- [x] Device capacity can be fetched from real device using CMD_GET_FREE_SIZES
- [x] Capacity is stored in device.max_users field
- [x] refresh_device_capacity endpoint uses real device
- [x] Capacity is displayed in UI
- [x] Error handling implemented
- [x] Response parsing works correctly
- [x] Logging added
- [x] Documentation updated
- [x] Removed simulation mode code from capacity service

## Notes

- **Command Format**: Verify exact format and response structure of CMD_GET_FREE_SIZES
- **Response Parsing**: ZKTeco devices may return capacity in different formats - ensure parsing handles all cases
- **Library Support**: Check if ZKTeco library provides helper method for capacity, or if manual command sending is needed
- **Capacity Types**: Some devices have separate capacities for users, fingerprints, etc. - focus on user capacity
- **Validation**: Ensure fetched capacity is reasonable (positive integer, not 0, etc.)

## Dependencies

- Depends on: Task 048
- Updates: Existing device_capacity service (removes simulation mode)
- Part of: Device info fetching suite
