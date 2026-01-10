# Task 049: Fetch Device Serial Number

## Story
Story 03: Device Management - Phase 3: Real Device Integration

## Task Type
Backend - Device Communication

## Duration Estimate
0.5 day

## Description

Implement functionality to fetch the device serial number directly from a real ZKTeco device using the device communication protocol.

## Prerequisites

- ✅ Task 048 complete (device connection service working)
- ✅ Real device available for testing

## Acceptance Criteria

- [x] Can fetch device serial number from real device ✅
- [x] Serial number is returned in API response ✅
- [x] Serial number is stored in database (via fetch_all_device_info with update_serial=True) ✅
- [x] Error handling for devices that don't support serial number retrieval ✅
- [x] Serial number format is validated ✅
- [x] API endpoint returns serial number (`GET /api/v1/devices/{device_id}/serial`) ✅

## Implementation Details

### Files to Modify

1. **backend/device_service/services/device_info_service.py** (create if doesn't exist)
   - `fetch_device_serial()` method
   - Serial number parsing/validation

2. **backend/device_service/api/routes/devices.py**
   - Add endpoint: `GET /api/v1/devices/{device_id}/serial`
   - Add to device registration: auto-fetch serial during registration

3. **backend/device_service/schemas/device.py** (if separate schemas file)
   - Add serial number to device response schema

### Key Code Patterns

```python
# backend/device_service/services/device_info_service.py
from typing import Optional
from device_service.services.device_connection_service import DeviceConnectionService
from device_service.models.device import Device
from sqlalchemy.ext.asyncio import AsyncSession
import logging

logger = logging.getLogger(__name__)

class DeviceInfoService:
    """Service for fetching device information from real devices."""
    
    def __init__(self, db: AsyncSession, connection_service: DeviceConnectionService):
        self.db = db
        self.connection_service = connection_service
    
    async def fetch_device_serial(self, device: Device) -> Optional[str]:
        """
        Fetch device serial number from real device.
        
        Args:
            device: Device model instance
            
        Returns:
            Serial number string or None if unavailable
        """
        conn = await self.connection_service.get_connection(device)
        if not conn:
            logger.error(f"Cannot connect to device {device.id} to fetch serial")
            return None
        
        try:
            # ZKTeco library method to get serial number
            # This may vary based on library version
            serial = await asyncio.to_thread(conn.get_serial_number)
            
            if serial:
                logger.info(f"Fetched serial number {serial} from device {device.id}")
                # Update device in database
                device.serial_number = serial
                await self.db.commit()
                await self.db.refresh(device)
            
            return serial
        except Exception as e:
            logger.error(f"Error fetching serial from device {device.id}: {e}")
            return None
```

### API Endpoint

```python
# backend/device_service/api/routes/devices.py
@router.get(
    "/{device_id}/serial",
    summary="Get device serial number",
    description="Fetch device serial number directly from the device",
    responses={
        200: {"description": "Serial number retrieved"},
        404: {"description": "Device not found"},
        503: {"description": "Device connection failed"},
    },
)
async def get_device_serial(
    device_id: int = Path(...),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fetch serial number from real device."""
    # Implementation
```

## Testing

### Manual Testing Steps

1. **Fetch Serial During Registration**
   - Register new device with IP/port
   - Click "Fetch Device Info" button
   - Verify serial number is fetched and displayed
   - Verify serial number is saved to database

2. **Fetch Serial for Existing Device**
   - Navigate to device detail page
   - Click "Refresh Device Info"
   - Verify serial number is fetched and updated

3. **Test Error Cases**
   - Try fetching from offline device
   - Verify appropriate error message
   - Try fetching from device with invalid connection

### Expected Results

- Serial number is fetched successfully from online device
- Serial number is stored in database
- Serial number is displayed in UI
- Error messages are clear when device is unavailable
- Serial number format is correct (alphanumeric, proper length)

## Definition of Done

- [x] Device serial number can be fetched from real device
- [x] Serial number is returned in API response
- [x] Serial number is stored in database
- [x] Error handling implemented
- [x] API endpoint created and tested
- [x] Serial number validation added
- [x] Logging added for debugging
- [x] Documentation updated

## Notes

- **Library Method**: Verify exact method name for getting serial number in ZKTeco library
- **Serial Format**: ZKTeco devices may return serial in different formats (hex, string, etc.)
- **Validation**: Ensure serial number format matches expected pattern
- **Caching**: Consider caching serial number to avoid repeated device queries

## Dependencies

- Depends on: Task 048
- Part of: Device info fetching suite (along with tasks 050, 051, 052)
