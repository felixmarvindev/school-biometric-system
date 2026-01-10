# Task 050: Fetch Device Model and Firmware Version

## Story
Story 03: Device Management - Phase 3: Real Device Integration

## Task Type
Backend - Device Communication

## Duration Estimate
0.5 day

## Description

Implement functionality to fetch device model name and firmware version directly from a real ZKTeco device. This information helps identify device capabilities and compatibility.

## Prerequisites

- ✅ Task 048 complete (device connection service working)
- ✅ Real device available for testing

## Acceptance Criteria

- [ ] Can fetch device model from real device
- [ ] Can fetch firmware version from real device
- [ ] Model and firmware are returned in API response
- [ ] Model and firmware are displayed in UI
- [ ] Error handling for devices that don't support these queries
- [ ] Device model and firmware stored (optional - may add fields to Device model)

## Implementation Details

### Files to Modify

1. **backend/device_service/services/device_info_service.py**
   - `fetch_device_model()` method
   - `fetch_device_firmware()` method
   - `fetch_device_info()` method (combined fetch)

2. **backend/device_service/api/routes/devices.py**
   - Add endpoint: `GET /api/v1/devices/{device_id}/info`
   - Returns model, firmware, serial, capacity, etc.

3. **backend/device_service/models/device.py** (optional - if storing)
   - Add `model_name` field (optional)
   - Add `firmware_version` field (optional)

4. **backend/device_service/schemas/device.py**
   - Add model and firmware to device response schema

### Key Code Patterns

```python
# backend/device_service/services/device_info_service.py
from typing import Optional, Dict, Any
import asyncio

async def fetch_device_model(self, device: Device) -> Optional[str]:
    """
    Fetch device model name from real device.
    
    Args:
        device: Device model instance
        
    Returns:
        Model name string or None if unavailable
    """
    conn = await self.connection_service.get_connection(device)
    if not conn:
        return None
    
    try:
        # ZKTeco library method - verify exact method name
        model = await asyncio.to_thread(conn.get_firmware_version)
        # Or may need to parse from device info
        # model = await asyncio.to_thread(conn.get_device_name)
        return model
    except Exception as e:
        logger.error(f"Error fetching model from device {device.id}: {e}")
        return None

async def fetch_device_firmware(self, device: Device) -> Optional[str]:
    """
    Fetch firmware version from real device.
    
    Args:
        device: Device model instance
        
    Returns:
        Firmware version string or None if unavailable
    """
    conn = await self.connection_service.get_connection(device)
    if not conn:
        return None
    
    try:
        # ZKTeco library method - verify exact method name
        firmware = await asyncio.to_thread(conn.get_firmware_version)
        return firmware
    except Exception as e:
        logger.error(f"Error fetching firmware from device {device.id}: {e}")
        return None

async def fetch_device_info(self, device: Device) -> Dict[str, Any]:
    """
    Fetch all device information at once.
    
    Returns:
        Dictionary with device information
    """
    info = {}
    
    # Fetch all info in parallel if possible
    serial = await self.fetch_device_serial(device)
    model = await self.fetch_device_model(device)
    firmware = await self.fetch_device_firmware(device)
    
    info.update({
        "serial_number": serial,
        "model_name": model,
        "firmware_version": firmware,
    })
    
    return info
```

### API Endpoint

```python
@router.get(
    "/{device_id}/info",
    summary="Get device information",
    description="Fetch device information (model, firmware, serial, etc.) directly from the device",
    responses={
        200: {"description": "Device information retrieved"},
        404: {"description": "Device not found"},
        503: {"description": "Device connection failed"},
    },
)
async def get_device_info(
    device_id: int = Path(...),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fetch device information from real device."""
    # Implementation
```

## Testing

### Manual Testing Steps

1. **Fetch Device Info**
   - Navigate to device detail page
   - Click "Fetch Device Info" or "Refresh Info"
   - Verify model name is displayed
   - Verify firmware version is displayed

2. **Test During Registration**
   - Register new device
   - Click "Fetch Device Info" during registration
   - Verify model and firmware are fetched and displayed

3. **Test Error Cases**
   - Try fetching from offline device
   - Verify appropriate error messages
   - Verify partial info is handled (if some fields fail)

### Expected Results

- Model name is fetched and displayed correctly
- Firmware version is fetched and displayed correctly
- Both fields are shown in device detail UI
- Error handling works for unavailable devices
- Info can be refreshed on demand

## Definition of Done

- [x] Device model can be fetched from real device
- [x] Firmware version can be fetched from real device
- [x] Model and firmware returned in API response
- [x] Model and firmware displayed in UI
- [x] Error handling implemented
- [x] API endpoint created and tested
- [x] Logging added
- [x] Documentation updated

## Notes

- **Library Methods**: Verify exact method names in ZKTeco library for model/firmware
- **Device Support**: Not all ZKTeco devices may support these queries - handle gracefully
- **Field Storage**: Consider if model/firmware should be stored in database or fetched on-demand
- **Caching**: Model/firmware rarely change, consider caching to reduce device queries

## Dependencies

- Depends on: Task 048
- Part of: Device info fetching suite (along with tasks 049, 051, 052)
