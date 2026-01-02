# Task 035: Device List UI

## Story/Phase
- **Story**: Story 03: Device Management
- **Phase**: Phase 1: Device Registration

## Description

Create the device list page component with search, filtering, status indicators, and device management actions.

## Type
- [ ] Backend
- [x] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Acceptance Criteria

1. [x] Device list page route exists at `/dashboard/devices`
2. [x] Page is protected (requires authentication via layout)
3. [x] `DeviceList` component created
4. [x] Displays list of devices in table format
5. [x] Shows device status indicators (online/offline/unknown)
6. [x] Search functionality works (by name, IP, or serial number)
7. [x] Filter by status works (dropdown)
8. [x] Filter by device group works (dropdown - Phase 2)
9. [x] Pagination controls work
10. [x] Loading states shown during data fetch
11. [x] Error states handled gracefully
12. [x] "Add Device" button navigates to create form
13. [x] Click on device navigates to detail page
14. [x] Connection test button for each device
15. [x] Responsive design (mobile-friendly)
16. [x] Empty state shown when no devices

## Technical Details

### Files to Create/Modify

```
frontend/app/(dashboard)/dashboard/devices/page.tsx
frontend/components/features/devices/DeviceList.tsx
frontend/components/features/devices/DeviceTableRow.tsx
frontend/components/features/devices/DeviceStatusBadge.tsx
frontend/components/features/devices/DeviceListFilters.tsx
frontend/lib/api/devices.ts (add listDevices, testConnection functions)
```

### Key Code Patterns

```typescript
// app/(dashboard)/dashboard/devices/page.tsx
"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { DeviceList } from "@/components/features/devices/DeviceList"
import { useAuthStore } from "@/lib/store/authStore"
import { listDevices, type DeviceResponse, DeviceStatus } from "@/lib/api/devices"

export default function DevicesPage() {
  const router = useRouter()
  const { token } = useAuthStore()
  const [devices, setDevices] = useState<DeviceResponse[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [pageSize] = useState(50)
  const [search, setSearch] = useState("")
  const [statusFilter, setStatusFilter] = useState<DeviceStatus | null>(null)
  const [groupFilter, setGroupFilter] = useState<number | null>(null)

  useEffect(() => {
    if (!token) return

    const fetchDevices = async () => {
      try {
        setIsLoading(true)
        const result = await listDevices(token, {
          page,
          page_size: pageSize,
          search: search || undefined,
          status: statusFilter || undefined,
          device_group_id: groupFilter || undefined,
        })
        setDevices(result.items)
      } catch (err) {
        setError("Failed to load devices")
      } finally {
        setIsLoading(false)
      }
    }

    fetchDevices()
  }, [token, page, search, statusFilter, groupFilter])

  return (
    <DeviceList
      devices={devices}
      isLoading={isLoading}
      error={error}
      search={search}
      onSearchChange={setSearch}
      statusFilter={statusFilter}
      onStatusFilterChange={setStatusFilter}
      groupFilter={groupFilter}
      onGroupFilterChange={setGroupFilter}
      onAddDevice={() => router.push("/dashboard/devices/new")}
      onDeviceClick={(id) => router.push(`/dashboard/devices/${id}`)}
      onTestConnection={async (id) => {
        // Handle connection test
      }}
    />
  )
}
```

### Dependencies

- Task 030 (List devices API must exist)
- Task 034 (Connection test API must exist)
- Task 006 (Dashboard layout must exist)

## Visual Testing

### Before State
- No device list page exists
- Cannot view devices from frontend

### After State
- Can navigate to `/dashboard/devices`
- See list of devices with status indicators
- Can search and filter
- Can test device connections
- Can navigate to device detail or create form

### Testing Steps

1. Navigate to devices page
2. Verify list displays correctly
3. Test search functionality
4. Test filtering by status
5. Test pagination
6. Test connection test button
7. Test navigation to detail/create pages

## Definition of Done

- [x] Code written and follows standards
- [x] Component tests written and passing
- [x] Search functionality works
- [x] Filtering works
- [x] Pagination works
- [x] Status indicators display correctly
- [x] Connection test works
- [x] Responsive design verified
- [x] Loading states implemented
- [x] Error states handled
- [x] Empty state implemented
- [x] Code reviewed
- [x] Tested in browser

## Time Estimate

6-8 hours

## Notes

- Use table layout for desktop, card layout for mobile
- Debounce search input (300ms delay)
- Show loading skeleton during fetch
- Status indicators: Green for online, Red for offline, Gray for unknown
- Connection test should show loading state and update status
- Consider WebSocket for real-time status updates (Phase 3)

