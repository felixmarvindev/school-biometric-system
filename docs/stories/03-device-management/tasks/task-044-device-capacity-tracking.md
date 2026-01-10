# Task 044: Device Capacity Tracking

## Story/Phase
- **Story**: Story 03: Device Management
- **Phase**: Phase 3: Device Monitoring

## Description

Track and display device capacity (enrolled users vs. max capacity) for enrollment planning.

## Type
- [x] Backend
- [x] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Acceptance Criteria

1. [x] Device capacity retrieved from device (max_users)
2. [x] Enrolled users count tracked in database
3. [x] Capacity information displayed in device list
4. [ ] Capacity information displayed in device detail (DeviceDetail component not yet created)
5. [x] Capacity percentage calculated and displayed
6. [x] Warning when capacity approaching limit (80%+)
7. [ ] Capacity updated during enrollment (Story 04 - will be implemented in enrollment story)
8. [x] Capacity displayed in UI with progress bar

## Technical Details

### Files to Create/Modify

```
backend/device_service/services/device_capacity.py
backend/device_service/api/routes/devices.py (add capacity endpoint)
frontend/components/features/devices/DeviceCapacityIndicator.tsx
frontend/components/features/devices/DeviceList.tsx (display capacity)
frontend/components/features/devices/DeviceDetail.tsx (display capacity)
```

### Key Code Patterns

```python
# services/device_capacity.py
from sqlalchemy.ext.asyncio import AsyncSession
from device_service.models.device import Device
from device_service.repositories.device_repository import DeviceRepository
from device_service.services.device_connection import DeviceConnectionService

class DeviceCapacityService:
    """Service for tracking and managing device capacity."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = DeviceRepository(db)
        self.connection_service = DeviceConnectionService()
    
    async def get_device_capacity(self, device_id: int) -> dict:
        """Get device capacity information."""
        device = await self.repo.get_by_id(device_id)
        
        if not device:
            return None
        
        max_users = device.max_users or 0
        enrolled_users = device.enrolled_users or 0
        available = max_users - enrolled_users if max_users > 0 else None
        percentage = (enrolled_users / max_users * 100) if max_users > 0 else None
        
        return {
            "device_id": device_id,
            "max_users": max_users,
            "enrolled_users": enrolled_users,
            "available": available,
            "percentage": percentage,
            "is_full": max_users > 0 and enrolled_users >= max_users,
            "is_warning": percentage is not None and percentage >= 80,
        }
    
    async def refresh_device_capacity(self, device_id: int) -> dict:
        """Refresh capacity from device and update database."""
        device = await self.repo.get_by_id(device_id)
        
        if not device:
            return None
        
        # Get capacity from device (using ZKTeco protocol)
        if settings.SIMULATION_MODE:
            # Simulate device capacity
            max_users = 1000  # Simulated max
        else:
            max_users = await self.connection_service.get_device_capacity(
                ip_address=device.ip_address,
                port=device.port
            )
        
        # Update device max_users
        await self.repo.update_device(
            device_id=device_id,
            max_users=max_users
        )
        
        await self.db.commit()
        
        return await self.get_device_capacity(device_id)
```

### Frontend Component

```typescript
// components/features/devices/DeviceCapacityIndicator.tsx
interface DeviceCapacityIndicatorProps {
  maxUsers: number | null
  enrolledUsers: number
}

export function DeviceCapacityIndicator({ maxUsers, enrolledUsers }: DeviceCapacityIndicatorProps) {
  if (!maxUsers || maxUsers === 0) {
    return <span className="text-muted-foreground">Unknown capacity</span>
  }

  const percentage = (enrolledUsers / maxUsers) * 100
  const isWarning = percentage >= 80
  const isFull = percentage >= 100

  return (
    <div className="flex items-center gap-2">
      <div className="flex-1">
        <Progress value={percentage} className={isWarning ? "bg-yellow-500" : ""} />
      </div>
      <span className={`text-sm ${isFull ? "text-red-600" : isWarning ? "text-yellow-600" : "text-muted-foreground"}`}>
        {enrolledUsers} / {maxUsers}
      </span>
    </div>
  )
}
```

### Dependencies

- Task 034 (Connection test API - connection service exists)
- Task 027 (Device model must exist - has max_users, enrolled_users fields)

## Visual Testing

### Before State
- No capacity information displayed
- Cannot see device enrollment limits

### After State
- Capacity displayed in device list and detail
- Progress bar shows usage
- Warning when approaching limit

### Testing Steps

1. View device list - verify capacity displayed
2. View device detail - verify capacity information
3. Test with full device - verify warning
4. Test with device at 80%+ - verify warning
5. Verify capacity percentage calculated correctly

## Definition of Done

- [x] Code written and follows standards
- [x] Capacity tracking implemented
- [x] Capacity displayed in UI
- [x] Progress bar works
- [x] Warning states implemented
- [x] Capacity refresh works
- [x] Code reviewed
- [x] Tested in browser

## Time Estimate

3-4 hours

## Notes

- Max users retrieved from device (ZKTeco protocol command)
- Enrolled users tracked in database (updated during enrollment)
- Display percentage with progress bar
- Warning at 80% capacity
- Error state at 100% capacity
- Capacity refresh button in device detail (optional)

