# Task 053: Auto-populate Device Info During Registration

## Story
Story 03: Device Management - Phase 3: Real Device Integration

## Task Type
Backend + Frontend - Integration

## Duration Estimate
1 day

## Description

Enhance device registration flow to automatically fetch and populate device information (serial, model, firmware, capacity) from the real device when IP address and port are provided. This improves user experience by reducing manual data entry.

## Prerequisites

- ✅ Tasks 049, 050, 051, 052 complete (all device info fetching working)
- ✅ Real device available for testing

## Acceptance Criteria

- [ ] "Fetch Device Info" button available during device registration
- [ ] Clicking button fetches all device info from real device
- [ ] Device info auto-populates form fields (serial, model, firmware, capacity)
- [ ] Loading state shown during fetch
- [ ] Error handling for offline/unreachable devices
- [ ] User can still manually enter info if fetch fails
- [ ] Fetched info can be edited before submission
- [ ] Device registration uses fetched info if available

## Implementation Details

### Backend Changes

1. **backend/device_service/api/routes/devices.py**
   - Add endpoint: `POST /api/v1/devices/fetch-info` (by IP/port)
   - Returns device info before device is created

2. **backend/device_service/services/device_info_service.py**
   - Add `fetch_device_info_by_address()` method
   - Fetches info using IP/port without requiring device record

### Frontend Changes

1. **frontend/components/devices/DeviceRegistrationForm.tsx**
   - Add "Fetch Device Info" button
   - Add loading state
   - Auto-populate form fields with fetched data
   - Handle errors gracefully

2. **frontend/lib/api/devices.ts**
   - Add `fetchDeviceInfoByAddress()` function

### Key Code Patterns

#### Backend

```python
# backend/device_service/api/routes/devices.py
@router.post(
    "/fetch-info",
    summary="Fetch device info by IP address",
    description="Fetch device information (serial, model, firmware, capacity) from device before registration",
    responses={
        200: {"description": "Device info retrieved"},
        503: {"description": "Device connection failed"},
    },
)
async def fetch_device_info_by_address(
    info_request: DeviceInfoRequest,  # {ip_address, port, com_password}
    db: AsyncSession = Depends(get_db),
):
    """Fetch device info from device at specified address."""
    # Create temporary connection
    conn = RealDeviceConnection(
        ip=info_request.ip_address,
        port=info_request.port,
        password=int(info_request.com_password) if info_request.com_password else None
    )
    
    if not await conn.connect():
        raise HTTPException(
            status_code=503,
            detail="Could not connect to device. Please check IP address and port."
        )
    
    try:
        info_service = DeviceInfoService(db, connection_service)
        
        # Fetch all info
        device_info = {
            "serial_number": await info_service.fetch_device_serial_from_connection(conn),
            "model_name": await info_service.fetch_device_model_from_connection(conn),
            "firmware_version": await info_service.fetch_device_firmware_from_connection(conn),
            "max_users": await info_service.fetch_device_capacity_from_connection(conn),
            "device_time": await info_service.fetch_device_time_from_connection(conn),
        }
        
        return device_info
    finally:
        await conn.disconnect()
```

#### Frontend

```typescript
// frontend/components/devices/DeviceRegistrationForm.tsx
const [isFetchingInfo, setIsFetchingInfo] = useState(false);
const [fetchError, setFetchError] = useState<string | null>(null);

const handleFetchDeviceInfo = async () => {
  if (!form.watch('ip_address') || !form.watch('port')) {
    setFetchError('Please enter IP address and port first');
    return;
  }
  
  setIsFetchingInfo(true);
  setFetchError(null);
  
  try {
    const info = await fetchDeviceInfoByAddress(token, {
      ip_address: form.watch('ip_address'),
      port: form.watch('port'),
      com_password: form.watch('com_password') || undefined,
    });
    
    // Auto-populate form
    form.setValue('serial_number', info.serial_number || '');
    form.setValue('model_name', info.model_name || '');
    form.setValue('firmware_version', info.firmware_version || '');
    form.setValue('max_users', info.max_users?.toString() || '');
    
    toast.success('Device info fetched successfully');
  } catch (error) {
    setFetchError(error instanceof Error ? error.message : 'Failed to fetch device info');
    toast.error('Could not fetch device info. You can enter details manually.');
  } finally {
    setIsFetchingInfo(false);
  }
};
```

## Testing

### Manual Testing Steps

1. **Fetch Info During Registration**
   - Navigate to device registration form
   - Enter IP address and port
   - Click "Fetch Device Info" button
   - Verify loading indicator appears
   - Verify form fields are auto-populated
   - Verify user can edit fetched values
   - Submit form and verify device is created with fetched info

2. **Test Error Cases**
   - Enter invalid IP address
   - Click "Fetch Device Info"
   - Verify error message is shown
   - Verify user can still manually enter info
   - Submit form with manual info

3. **Test Partial Info**
   - Connect to device that doesn't support all queries
   - Verify partial info is populated
   - Verify missing fields can be entered manually

### Expected Results

- Device info is fetched successfully when device is online
- Form fields are auto-populated correctly
- User can edit fetched values before submission
- Error messages are clear when device is unavailable
- Manual entry still works if fetch fails
- Registration works with both fetched and manual info

## Definition of Done

- [x] "Fetch Device Info" button implemented in registration form
- [x] Backend endpoint for fetching info by IP/port created
- [x] Form fields auto-populate with fetched data
- [x] Loading state shown during fetch
- [x] Error handling implemented
- [x] User can edit fetched values
- [x] Manual entry still works
- [x] Device registration uses fetched info
- [x] UI/UX is intuitive
- [x] Tests passing

## Notes

- **User Experience**: Make it clear that fetching info is optional but recommended
- **Error Messages**: Provide helpful guidance when device is unreachable
- **Validation**: Still validate all fields even if auto-populated
- **Performance**: Fetching may take a few seconds - ensure good loading UX
- **Optional Fields**: Some info may not be available - handle gracefully

## Dependencies

- Depends on: Tasks 049, 050, 051, 052 (all device info fetching)
- Enhances: Device registration flow
- Blocks: None (enhancement, not blocker)
