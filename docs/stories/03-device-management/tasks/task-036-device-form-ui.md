# Task 036: Device Form UI

## Story/Phase
- **Story**: Story 03: Device Management
- **Phase**: Phase 1: Device Registration

## Description

Create the device registration and edit form component with validation, connection testing, and error handling.

## Type
- [ ] Backend
- [x] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Acceptance Criteria

1. [ ] Device form page route exists at `/dashboard/devices/new` and `/dashboard/devices/{id}/edit`
2. [ ] Page is protected (requires authentication)
3. [ ] `DeviceForm` component created
4. [ ] Form fields: name, IP address, port, serial number, location, description
5. [ ] Device group selector (dropdown - Phase 2)
6. [ ] IP address format validation (client-side)
7. [ ] Port range validation (1-65535)
8. [ ] Form submission works (create/update)
9. [ ] Connection test button works
10. [ ] Loading states during submission
11. [ ] Success/error messages displayed
12. [ ] Form validation messages clear
13. [ ] Redirects to device list on success
14. [ ] Responsive design (mobile-friendly)

## Technical Details

### Files to Create/Modify

```
frontend/app/(dashboard)/dashboard/devices/new/page.tsx
frontend/app/(dashboard)/dashboard/devices/[id]/edit/page.tsx
frontend/components/features/devices/DeviceForm.tsx
frontend/lib/validations/device.ts
frontend/lib/api/devices.ts (add createDevice, updateDevice, testConnection functions)
```

### Key Code Patterns

```typescript
// components/features/devices/DeviceForm.tsx
"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { deviceSchema, type DeviceFormData } from "@/lib/validations/device"
import { createDevice, updateDevice, testConnection } from "@/lib/api/devices"
import { useAuthStore } from "@/lib/store/authStore"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

interface DeviceFormProps {
  deviceId?: number
  initialData?: Partial<DeviceFormData>
}

export function DeviceForm({ deviceId, initialData }: DeviceFormProps) {
  const router = useRouter()
  const { token } = useAuthStore()
  const [isTesting, setIsTesting] = useState(false)
  const [testResult, setTestResult] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    watch,
  } = useForm<DeviceFormData>({
    resolver: zodResolver(deviceSchema),
    defaultValues: initialData,
  })

  const ipAddress = watch("ip_address")
  const port = watch("port")

  const handleTestConnection = async () => {
    if (!ipAddress || !port) {
      setTestResult("Please enter IP address and port first")
      return
    }

    setIsTesting(true)
    setTestResult(null)

    try {
      // For new devices, test connection without saving
      // For existing devices, use device_id
      const result = deviceId
        ? await testConnection(token!, deviceId)
        : await testConnectionByAddress(token!, ipAddress, port)

      if (result.success) {
        setTestResult(`✅ Connection successful (${result.response_time_ms}ms)`)
      } else {
        setTestResult(`❌ Connection failed: ${result.message}`)
      }
    } catch (err) {
      setTestResult("❌ Connection test failed")
    } finally {
      setIsTesting(false)
    }
  }

  const onSubmit = async (data: DeviceFormData) => {
    try {
      if (deviceId) {
        await updateDevice(token!, deviceId, data)
      } else {
        await createDevice(token!, data)
      }
      router.push("/dashboard/devices")
    } catch (err) {
      // Error handling
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* Form fields */}
      <div>
        <Label htmlFor="name">Device Name *</Label>
        <Input id="name" {...register("name")} />
        {errors.name && <p className="text-red-600">{errors.name.message}</p>}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label htmlFor="ip_address">IP Address *</Label>
          <Input id="ip_address" {...register("ip_address")} />
          {errors.ip_address && <p className="text-red-600">{errors.ip_address.message}</p>}
        </div>
        <div>
          <Label htmlFor="port">Port *</Label>
          <Input id="port" type="number" {...register("port", { valueAsNumber: true })} />
          {errors.port && <p className="text-red-600">{errors.port.message}</p>}
        </div>
      </div>

      {/* Connection test button */}
      <Button
        type="button"
        variant="outline"
        onClick={handleTestConnection}
        disabled={isTesting || !ipAddress || !port}
      >
        {isTesting ? "Testing..." : "Test Connection"}
      </Button>
      {testResult && <p className="text-sm">{testResult}</p>}

      {/* Other fields */}
      {/* ... */}

      <div className="flex gap-4">
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Saving..." : deviceId ? "Update Device" : "Create Device"}
        </Button>
        <Button type="button" variant="outline" onClick={() => router.back()}>
          Cancel
        </Button>
      </div>
    </form>
  )
}
```

### Dependencies

- Task 029 (Create device API must exist)
- Task 032 (Update device API must exist)
- Task 034 (Connection test API must exist)
- Task 028 (Device schemas must exist)

## Visual Testing

### Before State
- No device form exists
- Cannot register devices from frontend

### After State
- Can navigate to `/dashboard/devices/new`
- Can fill device form
- Can test connection before saving
- Can create/update devices
- Form validation works

### Testing Steps

1. Navigate to create device page
2. Fill form and test validation
3. Test connection button
4. Submit form and verify redirect
5. Navigate to edit device page
6. Update device and verify changes

## Definition of Done

- [ ] Code written and follows standards
- [ ] Form validation works
- [ ] Connection test works
- [ ] Create device works
- [ ] Update device works
- [ ] Error handling comprehensive
- [ ] Loading states implemented
- [ ] Responsive design verified
- [ ] Code reviewed
- [ ] Tested in browser

## Time Estimate

6-8 hours

## Notes

- Use React Hook Form + Zod for validation
- IP address validation should match backend (IPv4/IPv6)
- Port validation: 1-65535
- Connection test can be done before saving (for new devices)
- Serial number is optional (can be updated after connection)
- Device group selector can be placeholder for Phase 2

