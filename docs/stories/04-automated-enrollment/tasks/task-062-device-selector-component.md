# Task 062: Device Selector Component

## Story/Phase
- **Story**: Story 04: Automated Enrollment
- **Phase**: Phase 1: Enrollment UI

## Description

Create a device selector component that displays available devices with online/offline status indicators and allows selection of a device for enrollment.

## Type
- [ ] Backend
- [x] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Duration Estimate
1 day

## Prerequisites

- ✅ Task 060 complete (enrollment page exists)
- ✅ Devices API endpoint working (`GET /api/v1/devices`)
- ✅ Device status tracking working

## Acceptance Criteria

1. [ ] Device selector component created
2. [ ] Device list displays with status indicators (online/offline)
3. [ ] Can select a device from list
4. [ ] Selected device is highlighted
5. [ ] Device details shown (name, location, status)
6. [ ] Offline devices are clearly marked (or disabled)
7. [ ] Loading state shown while fetching
8. [ ] Empty state shown when no devices
9. [ ] Component is reusable

## Implementation Details

### Frontend Changes

1. **frontend/components/features/enrollment/DeviceSelector.tsx**
   - Create device selector component
   - Add device list display
   - Add status indicators (online/offline badges)
   - Add selection handling
   - Add loading/empty states

2. **frontend/lib/api/devices.ts** (if not exists)
   - Add `getAllDevices()` function
   - Add `getOnlineDevices()` function

3. **frontend/app/(dashboard)/dashboard/enrollment/page.tsx**
   - Integrate DeviceSelector component
   - Handle selected device state

### Key Code Patterns

```typescript
// frontend/components/features/enrollment/DeviceSelector.tsx
'use client';

import { useState, useEffect } from 'react';
import { Wifi, WifiOff, CheckCircle2 } from 'lucide-react';
import { getAllDevices, type Device } from '@/lib/api/devices';
import { Badge } from '@/components/ui/badge';

interface DeviceSelectorProps {
  onSelect: (device: Device) => void;
  selectedDevice?: Device | null;
}

export function DeviceSelector({ onSelect, selectedDevice }: DeviceSelectorProps) {
  const [devices, setDevices] = useState<Device[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    getAllDevices()
      .then(setDevices)
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <div className="space-y-2">
      <label className="text-sm font-medium text-blue-700 dark:text-blue-400">
        Select Device
      </label>
      
      {isLoading && <div>Loading devices...</div>}
      
      {!isLoading && devices.length === 0 && (
        <div className="text-sm text-gray-500">No devices available</div>
      )}
      
      {devices.length > 0 && (
        <div className="border rounded-lg max-h-60 overflow-y-auto">
          {devices.map((device) => {
            const isOnline = device.status === 'online';
            const isSelected = selectedDevice?.id === device.id;
            
            return (
              <div
                key={device.id}
                onClick={() => isOnline && onSelect(device)}
                className={`p-3 cursor-pointer hover:bg-blue-50 dark:hover:bg-gray-700 ${
                  isSelected ? 'bg-blue-100 dark:bg-blue-900' : ''
                } ${!isOnline ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="font-medium">{device.name}</div>
                    <div className="text-sm text-gray-500">
                      {device.location || device.ip_address}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {isOnline ? (
                      <Badge variant="default" className="bg-green-500">
                        <Wifi className="w-3 h-3 mr-1" />
                        Online
                      </Badge>
                    ) : (
                      <Badge variant="secondary">
                        <WifiOff className="w-3 h-3 mr-1" />
                        Offline
                      </Badge>
                    )}
                    {isSelected && (
                      <CheckCircle2 className="w-5 h-5 text-blue-600" />
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
      
      {selectedDevice && (
        <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
          <div className="font-medium">{selectedDevice.name}</div>
          <div className="text-sm text-gray-600 dark:text-gray-400">
            {selectedDevice.location || selectedDevice.ip_address}
          </div>
        </div>
      )}
    </div>
  );
}
```

## Testing

### Manual Testing

1. **Device List**
   - Load enrollment page
   - ✅ Verify devices are displayed
   - ✅ Verify status indicators show correctly
   - ✅ Verify online/offline badges

2. **Selection**
   - Click an online device
   - ✅ Verify device is selected
   - ✅ Verify selected device is highlighted
   - ✅ Verify onSelect callback called

3. **Offline Devices**
   - Try to select offline device
   - ✅ Verify offline devices are disabled or show warning
   - ✅ Verify cannot select offline device

## Definition of Done

- [ ] Device selector component created
- [ ] Status indicators work correctly
- [ ] Selection works correctly
- [ ] Offline devices handled properly
- [ ] Loading/empty states handled
- [ ] Component is reusable
- [ ] No console errors
- [ ] Follows design system

## Next Task

**Task 063: Finger Selector Component** - Add finger selection dropdown.
