# Task 043: Device Status UI Updates

## Story/Phase
- **Story**: Story 03: Device Management
- **Phase**: Phase 3: Device Monitoring

## Description

Integrate WebSocket client in frontend to receive and display real-time device status updates.

## Type
- [ ] Backend
- [x] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Acceptance Criteria

1. [ ] WebSocket client hook created
2. [ ] Device list subscribes to status updates
3. [ ] Status indicators update in real-time
4. [ ] Last_seen timestamps update in real-time
5. [ ] Connection status indicator (connected/disconnected)
6. [ ] Automatic reconnection on disconnect
7. [ ] Loading states during initial connection
8. [ ] Error handling for connection failures

## Technical Details

### Files to Create/Modify

```
frontend/lib/hooks/useDeviceStatusWebSocket.ts
frontend/lib/websocket/client.ts
frontend/components/features/devices/DeviceList.tsx (integrate WebSocket)
frontend/components/features/devices/DeviceStatusBadge.tsx (real-time updates)
```

### Key Code Patterns

```typescript
// hooks/useDeviceStatusWebSocket.ts
import { useEffect, useState, useCallback } from "react"
import { useAuthStore } from "@/lib/store/authStore"
import { DeviceStatus } from "@/lib/api/devices"

interface DeviceStatusUpdate {
  type: "device_status_update"
  device_id: number
  status: DeviceStatus
  last_seen: string | null
  timestamp: string
}

export function useDeviceStatusWebSocket(
  onStatusUpdate: (update: DeviceStatusUpdate) => void
) {
  const { token } = useAuthStore()
  const [isConnected, setIsConnected] = useState(false)
  const [ws, setWs] = useState<WebSocket | null>(null)

  useEffect(() => {
    if (!token) return

    const connect = () => {
      const wsUrl = `${process.env.NEXT_PUBLIC_WS_URL}/ws/device-status?token=${token}`
      const websocket = new WebSocket(wsUrl)

      websocket.onopen = () => {
        console.log("WebSocket connected")
        setIsConnected(true)
      }

      websocket.onmessage = (event) => {
        const data = JSON.parse(event.data)

        if (data.type === "device_status_update") {
          onStatusUpdate(data as DeviceStatusUpdate)
        }
      }

      websocket.onerror = (error) => {
        console.error("WebSocket error:", error)
        setIsConnected(false)
      }

      websocket.onclose = () => {
        console.log("WebSocket disconnected")
        setIsConnected(false)
        // Reconnect after 3 seconds
        setTimeout(connect, 3000)
      }

      setWs(websocket)
    }

    connect()

    return () => {
      if (ws) {
        ws.close()
      }
    }
  }, [token, onStatusUpdate])

  return { isConnected }
}

// components/features/devices/DeviceList.tsx
import { useDeviceStatusWebSocket } from "@/lib/hooks/useDeviceStatusWebSocket"
import { DeviceStatus } from "@/lib/api/devices"

export function DeviceList({ devices, ... }) {
  const [deviceStatuses, setDeviceStatuses] = useState<Map<number, DeviceStatus>>(
    new Map(devices.map(d => [d.id, d.status]))
  )

  const handleStatusUpdate = useCallback((update: DeviceStatusUpdate) => {
    setDeviceStatuses(prev => {
      const newMap = new Map(prev)
      newMap.set(update.device_id, update.status)
      return newMap
    })
  }, [])

  const { isConnected } = useDeviceStatusWebSocket(handleStatusUpdate)

  return (
    <div>
      <div className="flex items-center gap-2 mb-4">
        <span className="text-sm text-muted-foreground">Status:</span>
        {isConnected ? (
          <span className="text-green-600">🟢 Real-time</span>
        ) : (
          <span className="text-yellow-600">🟡 Connecting...</span>
        )}
      </div>
      
      {/* Device list with real-time status */}
      {devices.map(device => (
        <DeviceTableRow
          key={device.id}
          device={device}
          status={deviceStatuses.get(device.id) || device.status}
        />
      ))}
    </div>
  )
}
```

### Dependencies

- Task 042 (Device status WebSocket events must exist)
- Task 035 (Device list UI must exist)

## Visual Testing

### Before State
- Status updates require page refresh
- No real-time feedback

### After State
- Status updates in real-time
- Connection indicator shows status
- Last_seen timestamps update automatically

### Testing Steps

1. Open device list page
2. Verify WebSocket connection indicator
3. Trigger device status change (health check or manual test)
4. Verify status updates in real-time
5. Test disconnection and reconnection
6. Verify multiple devices updating

## Definition of Done

- [ ] Code written and follows standards
- [ ] WebSocket hook implemented
- [ ] Real-time updates work
- [ ] Connection indicator displays
- [ ] Auto-reconnection works
- [ ] Error handling comprehensive
- [ ] Loading states implemented
- [ ] Code reviewed
- [ ] Tested in browser

## Time Estimate

4-5 hours

## Notes

- Use React hooks for WebSocket connection management
- Automatic reconnection on disconnect
- Connection status indicator for transparency
- Optimize updates (only update changed devices)
- Consider connection pooling for multiple components
- Handle token refresh gracefully

