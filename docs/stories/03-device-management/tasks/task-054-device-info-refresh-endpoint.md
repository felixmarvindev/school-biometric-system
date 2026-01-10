# Task 054: Device Info Refresh Endpoint

## Story
Story 03: Device Management - Phase 3: Real Device Integration

## Task Type
Backend + Frontend - API & UI

## Duration Estimate
0.5 day

## Description

Create a comprehensive endpoint and UI feature to refresh all device information from a real device. This allows administrators to update device details (serial, model, firmware, capacity, time) by fetching directly from the device.

## Prerequisites

- ✅ Tasks 049, 050, 051, 052 complete (all device info fetching working)
- ✅ Real device available for testing

## Acceptance Criteria

- [ ] Endpoint to refresh all device info: `POST /api/v1/devices/{device_id}/refresh-info`
- [ ] Endpoint fetches all device information from real device
- [ ] Endpoint updates device record in database with fetched info
- [ ] "Refresh Device Info" button in device detail page
- [ ] Loading state during refresh
- [ ] Success/error feedback to user
- [ ] Updated info displayed in UI after refresh
- [ ] Partial updates handled (if some info unavailable)

## Implementation Details

### Backend Changes

1. **backend/device_service/api/routes/devices.py**
   - Add endpoint: `POST /api/v1/devices/{device_id}/refresh-info`

2. **backend/device_service/services/device_info_service.py**
   - Add `refresh_all_device_info()` method
   - Updates device record with all fetched info

### Frontend Changes

1. **frontend/app/devices/[id]/page.tsx** (or device detail component)
   - Add "Refresh Device Info" button
   - Add loading state
   - Show success/error messages
   - Refresh displayed info after successful update

2. **frontend/lib/api/devices.ts**
   - Add `refreshDeviceInfo()` function

### Key Code Patterns

#### Backend

```python
# backend/device_service/api/routes/devices.py
@router.post(
    "/{device_id}/refresh-info",
    summary="Refresh all device information",
    description="Fetch all device information (serial, model, firmware, capacity, time) from real device and update database",
    response_model=DeviceResponse,
    responses={
        200: {"description": "Device info refreshed successfully"},
        404: {"description": "Device not found"},
        503: {"description": "Device connection failed"},
    },
)
async def refresh_device_info(
    device_id: int = Path(...),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Refresh all device information from real device."""
    device_service = DeviceService(db)
    
    device = await device_service.get_device_by_id(
        device_id=device_id,
        school_id=current_user.school_id
    )
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found"
        )
    
    connection_service = DeviceConnectionService(db)
    info_service = DeviceInfoService(db, connection_service)
    
    # Fetch all device info
    try:
        updated_info = await info_service.refresh_all_device_info(device)
        
        # Update device record
        if updated_info.get('serial_number'):
            device.serial_number = updated_info['serial_number']
        if updated_info.get('model_name'):
            # Store in description or add field to model if needed
            pass
        if updated_info.get('max_users'):
            device.max_users = updated_info['max_users']
        
        await db.commit()
        await db.refresh(device)
        
        return DeviceResponse.model_validate(device)
        
    except Exception as e:
        logger.error(f"Error refreshing device info for device {device_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Could not refresh device info: {str(e)}"
        )
```

#### Frontend

```typescript
// frontend/components/devices/DeviceDetail.tsx
const [isRefreshing, setIsRefreshing] = useState(false);

const handleRefreshInfo = async () => {
  setIsRefreshing(true);
  try {
    const updatedDevice = await refreshDeviceInfo(token, deviceId);
    // Update device state
    setDevice(updatedDevice);
    toast.success('Device info refreshed successfully');
  } catch (error) {
    toast.error(
      error instanceof Error 
        ? error.message 
        : 'Failed to refresh device info. Device may be offline.'
    );
  } finally {
    setIsRefreshing(false);
  }
};

// In JSX
<Button
  onClick={handleRefreshInfo}
  disabled={isRefreshing}
  variant="outline"
>
  {isRefreshing ? (
    <>
      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
      Refreshing...
    </>
  ) : (
    <>
      <RefreshCw className="mr-2 h-4 w-4" />
      Refresh Device Info
    </>
  )}
</Button>
```

## Testing

### Manual Testing Steps

1. **Refresh Device Info**
   - Navigate to device detail page
   - Click "Refresh Device Info" button
   - Verify loading state appears
   - Verify device info is updated in database
   - Verify updated info is displayed in UI
   - Verify success message is shown

2. **Test Error Cases**
   - Disconnect device from network
   - Click "Refresh Device Info"
   - Verify error message is shown
   - Verify existing device info is preserved

3. **Test Partial Updates**
   - Connect to device that doesn't support all queries
   - Click "Refresh Device Info"
   - Verify available info is updated
   - Verify unavailable info is not changed

### Expected Results

- All device info is refreshed when device is online
- Device record in database is updated
- UI displays updated information
- Success message confirms refresh
- Error handling works for offline devices
- Partial updates handled gracefully

## Definition of Done

- [x] Refresh endpoint created and working
- [x] Endpoint updates all device info in database
- [x] "Refresh Device Info" button in UI
- [x] Loading state implemented
- [x] Success/error feedback shown
- [x] Updated info displayed after refresh
- [x] Partial updates handled
- [x] Error handling implemented
- [x] Tests passing

## Notes

- **Performance**: Refreshing may take a few seconds - ensure good UX
- **Partial Updates**: Some info may not be available - only update what's fetched
- **Error Handling**: Don't clear existing info if refresh fails
- **Use Case**: Useful when device info changes or was entered incorrectly
- **Frequency**: Users may refresh frequently - ensure it's not too slow

## Dependencies

- Depends on: Tasks 049, 050, 051, 052 (all device info fetching)
- Enhances: Device detail page
- Blocks: None (enhancement)
