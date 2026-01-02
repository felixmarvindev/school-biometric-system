"use client"

import { Badge } from "@/components/ui/badge"
import { type DeviceStatus } from "@/lib/api/devices"

export interface DeviceStatusBadgeProps {
  status: DeviceStatus
}

/**
 * Status badge component for devices.
 * 
 * Shows status with appropriate colors:
 * - Green for online
 * - Red for offline
 * - Gray for unknown
 */
export function DeviceStatusBadge({ status }: DeviceStatusBadgeProps) {
  const statusConfig = {
    online: {
      label: "Online",
      className: "bg-green-500 text-white border-green-600",
    },
    offline: {
      label: "Offline",
      className: "bg-red-500 text-white border-red-600",
    },
    unknown: {
      label: "Unknown",
      className: "bg-gray-500 text-white border-gray-600",
    },
  }

  const config = statusConfig[status]

  return (
    <Badge className={config.className} variant="outline">
      {config.label}
    </Badge>
  )
}

