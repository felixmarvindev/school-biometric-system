"use client"

import { Button } from "@/components/ui/button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { X } from "lucide-react"
import { type DeviceStatus } from "@/lib/api/devices"

export interface DeviceListFiltersProps {
  statusFilter: DeviceStatus | null
  onStatusFilterChange: (value: DeviceStatus | null) => void
  deviceGroupFilter: number | null
  onDeviceGroupFilterChange: (value: number | null) => void
  deviceGroups?: Array<{ id: number; name: string }>
}

export function DeviceListFilters({
  statusFilter,
  onStatusFilterChange,
  deviceGroupFilter,
  onDeviceGroupFilterChange,
  deviceGroups = [],
}: DeviceListFiltersProps) {
  const hasFilters = statusFilter || deviceGroupFilter

  return (
    <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
      <div className="flex-1 grid grid-cols-1 gap-3 sm:grid-cols-2">
        {/* Status Filter */}
        <Select
          value={statusFilter || "all"}
          onValueChange={(value) =>
            onStatusFilterChange(value === "all" ? null : (value as DeviceStatus))
          }
        >
          <SelectTrigger className="border-gray-300 focus:border-blue-500 focus:ring-blue-500">
            <SelectValue placeholder="All Statuses" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Statuses</SelectItem>
            <SelectItem value="online">Online</SelectItem>
            <SelectItem value="offline">Offline</SelectItem>
            <SelectItem value="unknown">Unknown</SelectItem>
          </SelectContent>
        </Select>

        {/* Device Group Filter */}
        <Select
          value={deviceGroupFilter?.toString() || "all"}
          onValueChange={(value) =>
            onDeviceGroupFilterChange(value === "all" ? null : parseInt(value))
          }
          disabled={deviceGroups.length === 0}
        >
          <SelectTrigger className="border-gray-300 focus:border-purple-500 focus:ring-purple-500">
            <SelectValue placeholder="All Groups" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Groups</SelectItem>
            {deviceGroups.map((group) => (
              <SelectItem key={group.id} value={group.id.toString()}>
                {group.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Clear Filters Button */}
      {hasFilters && (
        <Button
          variant="outline"
          size="sm"
          onClick={() => {
            onStatusFilterChange(null)
            onDeviceGroupFilterChange(null)
          }}
          className="sm:w-auto"
        >
          <X className="mr-2 h-4 w-4" />
          Clear Filters
        </Button>
      )}
    </div>
  )
}

