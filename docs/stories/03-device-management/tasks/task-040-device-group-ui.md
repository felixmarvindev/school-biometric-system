# Task 040: Device Group Management UI

## Story/Phase
- **Story**: Story 03: Device Management
- **Phase**: Phase 2: Device Groups

## Description

Create UI components for device group management, including group creation, editing, and assignment to devices.

## Type
- [ ] Backend
- [x] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Acceptance Criteria

1. [ ] Device group list page exists
2. [ ] Device group form component exists (create/edit)
3. [ ] Group selector added to device form
4. [ ] Group filter added to device list
5. [ ] Group management actions (edit, delete)
6. [ ] Group assignment to devices works
7. [ ] Device count displayed per group
8. [ ] Loading states implemented
9. [ ] Error handling comprehensive
10. [ ] Responsive design verified

## Technical Details

### Files to Create/Modify

```
frontend/app/(dashboard)/dashboard/device-groups/page.tsx
frontend/app/(dashboard)/dashboard/device-groups/new/page.tsx
frontend/app/(dashboard)/dashboard/device-groups/[id]/edit/page.tsx
frontend/components/features/devices/DeviceGroupList.tsx
frontend/components/features/devices/DeviceGroupForm.tsx
frontend/components/features/devices/DeviceGroupSelector.tsx
frontend/lib/api/device_groups.ts
frontend/components/features/devices/DeviceForm.tsx (add group selector)
frontend/components/features/devices/DeviceList.tsx (add group filter)
```

### Key Code Patterns

```typescript
// components/features/devices/DeviceGroupSelector.tsx
"use client"

import { useEffect, useState } from "react"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { listDeviceGroups, type DeviceGroupResponse } from "@/lib/api/device_groups"
import { useAuthStore } from "@/lib/store/authStore"

interface DeviceGroupSelectorProps {
  value?: number | null
  onValueChange: (value: number | null) => void
  placeholder?: string
}

export function DeviceGroupSelector({ value, onValueChange, placeholder = "Select group..." }: DeviceGroupSelectorProps) {
  const { token } = useAuthStore()
  const [groups, setGroups] = useState<DeviceGroupResponse[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    if (!token) return

    const fetchGroups = async () => {
      try {
        const result = await listDeviceGroups(token, { page: 1, page_size: 100 })
        setGroups(result.items)
      } catch (err) {
        console.error("Failed to load device groups", err)
      } finally {
        setIsLoading(false)
      }
    }

    fetchGroups()
  }, [token])

  return (
    <Select
      value={value?.toString() || ""}
      onValueChange={(val) => onValueChange(val ? parseInt(val) : null)}
      disabled={isLoading}
    >
      <SelectTrigger>
        <SelectValue placeholder={placeholder} />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="">None</SelectItem>
        {groups.map((group) => (
          <SelectItem key={group.id} value={group.id.toString()}>
            {group.name} ({group.device_count} devices)
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
}
```

### Dependencies

- Task 039 (Device group management API must exist)
- Task 036 (Device form UI must exist - to add group selector)
- Task 035 (Device list UI must exist - to add group filter)

## Visual Testing

### Before State
- No device group UI exists
- Cannot manage groups from frontend

### After State
- Can create and manage device groups
- Can assign devices to groups
- Can filter devices by group
- Groups displayed in device list

### Testing Steps

1. Navigate to device groups page
2. Create a new device group
3. Edit device group
4. Assign device to group from device form
5. Filter devices by group in device list
6. Verify group count updates
7. Delete device group

## Definition of Done

- [ ] Code written and follows standards
- [ ] Group management UI complete
- [ ] Group selector added to device form
- [ ] Group filter added to device list
- [ ] Loading states implemented
- [ ] Error handling comprehensive
- [ ] Responsive design verified
- [ ] Code reviewed
- [ ] Tested in browser

## Time Estimate

5-6 hours

## Notes

- Group selector should show device count per group
- Group filter in device list should include "No Group" option
- Group management can be modal or separate page
- Consider showing devices within a group on group detail page (future enhancement)

