# Task 046: Simulation Mode UI

## Story/Phase
- **Story**: Story 03: Device Management
- **Phase**: Phase 4: Simulation Mode

## Description

Add UI indicators and controls for simulation mode, making it clear when the system is in demo/test mode.

## Type
- [ ] Backend
- [x] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Acceptance Criteria

1. [ ] Simulation mode indicator displayed in UI
2. [ ] Indicator shows when simulation mode is active
3. [ ] Device list shows simulation mode badge
4. [ ] Device form shows simulation mode indicator
5. [ ] Warning banner when in simulation mode
6. [ ] Simulation mode status fetched from API
7. [ ] Visual distinction for simulated devices (optional)
8. [ ] Help text explains simulation mode

## Technical Details

### Files to Create/Modify

```
frontend/app/(dashboard)/dashboard/devices/page.tsx (add simulation indicator)
frontend/components/features/devices/SimulationModeBanner.tsx
frontend/components/features/devices/DeviceList.tsx (add simulation badge)
frontend/lib/api/devices.ts (add getSimulationMode function)
```

### Key Code Patterns

```typescript
// components/features/devices/SimulationModeBanner.tsx
"use client"

interface SimulationModeBannerProps {
  isSimulationMode: boolean
}

export function SimulationModeBanner({ isSimulationMode }: SimulationModeBannerProps) {
  if (!isSimulationMode) return null

  return (
    <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4 mb-4">
      <div className="flex items-center gap-2">
        <span className="text-yellow-600 dark:text-yellow-400">⚠️</span>
        <div>
          <h3 className="font-semibold text-yellow-900 dark:text-yellow-100">
            Simulation Mode Active
          </h3>
          <p className="text-sm text-yellow-700 dark:text-yellow-300">
            The system is running in simulation mode. All device operations are simulated and no physical devices are connected.
          </p>
        </div>
      </div>
    </div>
  )
}

// app/(dashboard)/dashboard/devices/page.tsx
import { SimulationModeBanner } from "@/components/features/devices/SimulationModeBanner"
import { useEffect, useState } from "react"
import { getSimulationMode } from "@/lib/api/devices"

export default function DevicesPage() {
  const [isSimulationMode, setIsSimulationMode] = useState(false)

  useEffect(() => {
    const checkSimulationMode = async () => {
      try {
        const mode = await getSimulationMode()
        setIsSimulationMode(mode.is_simulation_mode)
      } catch (err) {
        console.error("Failed to check simulation mode", err)
      }
    }

    checkSimulationMode()
  }, [])

  return (
    <div>
      <SimulationModeBanner isSimulationMode={isSimulationMode} />
      
      {/* Rest of device list */}
      <DeviceList isSimulationMode={isSimulationMode} />
    </div>
  )
}

// components/features/devices/DeviceList.tsx
interface DeviceListProps {
  isSimulationMode?: boolean
  // ... other props
}

export function DeviceList({ isSimulationMode, ... }: DeviceListProps) {
  return (
    <div>
      {isSimulationMode && (
        <div className="mb-4">
          <span className="inline-flex items-center gap-1 px-2 py-1 bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 text-xs font-medium rounded">
            🧪 Simulation Mode
          </span>
        </div>
      )}
      
      {/* Device list */}
    </div>
  )
}
```

### Dependencies

- Task 045 (Simulation mode backend must exist)
- Task 035 (Device list UI must exist)

## Visual Testing

### Before State
- No indication of simulation mode
- Unclear if real or simulated devices

### After State
- Clear simulation mode indicator
- Warning banner displayed
- Devices clearly marked when simulated

### Testing Steps

1. Enable simulation mode in backend
2. View device list - verify simulation banner
3. Verify simulation badge displays
4. Test device operations - verify they work
5. Verify help text/explanation available

## Definition of Done

- [ ] Code written and follows standards
- [ ] Simulation mode indicator displays
- [ ] Warning banner shows when active
- [ ] Device list shows simulation badge
- [ ] Help text explains simulation mode
- [ ] Visual distinction clear
- [ ] Code reviewed
- [ ] Tested in browser

## Time Estimate

2-3 hours

## Notes

- Simulation mode status fetched from backend API endpoint
- Banner should be non-intrusive but clear
- Yellow/warning colors for simulation mode
- Consider toggle to hide banner (user preference)
- Help tooltip explains what simulation mode means
- Clear visual distinction helps prevent confusion

