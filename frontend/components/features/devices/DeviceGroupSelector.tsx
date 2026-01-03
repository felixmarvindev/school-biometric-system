"use client"

import { useEffect, useState } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Button } from "@/components/ui/button"
import { listDeviceGroups, type DeviceGroupResponse } from "@/lib/api/device_groups"
import { useAuthStore } from "@/lib/store/authStore"
import { Plus } from "lucide-react"

export interface DeviceGroupSelectorProps {
  value?: number | null
  onValueChange: (value: number | null) => void
  placeholder?: string
  onNewGroupCreated?: (groupId: number) => void
}

/**
 * Device group selector component for use in forms.
 */
export function DeviceGroupSelector({
  value,
  onValueChange,
  placeholder = "Select group...",
  onNewGroupCreated,
}: DeviceGroupSelectorProps) {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { token } = useAuthStore()
  const [groups, setGroups] = useState<DeviceGroupResponse[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const fetchGroups = async () => {
    if (!token) {
      setIsLoading(false)
      return
    }

    try {
      const result = await listDeviceGroups(token, { page: 1, page_size: 100 })
      setGroups(result.items)
    } catch (err) {
      console.error("Failed to load device groups", err)
      // Continue with empty list on error
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchGroups()
  }, [token])

  // Handle return from creating a new group
  useEffect(() => {
    const newGroupId = searchParams?.get("newGroupId")
    if (newGroupId) {
      // Refresh groups list to include the new group
      fetchGroups().then(() => {
        // Select the new group
        const groupId = parseInt(newGroupId, 10)
        onValueChange(groupId)
        if (onNewGroupCreated) {
          onNewGroupCreated(groupId)
        }
        // Clean up URL - remove the newGroupId param
        const currentUrl = new URL(window.location.href)
        currentUrl.searchParams.delete("newGroupId")
        router.replace(currentUrl.pathname + currentUrl.search, { scroll: false })
      })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams])

  const handleAddNewGroup = () => {
    // Navigate to create group page with return URL
    const currentUrl = window.location.pathname + window.location.search
    router.push(`/dashboard/device-groups/new?returnTo=${encodeURIComponent(currentUrl)}`)
  }

  return (
    <div className="space-y-2">
      <Select
        value={value?.toString() || "none"}
        onValueChange={(val) => onValueChange(val === "none" ? null : parseInt(val, 10))}
        disabled={isLoading}
      >
        <SelectTrigger className="border-gray-300 focus:border-purple-500 focus:ring-purple-500">
          <SelectValue placeholder={isLoading ? "Loading groups..." : placeholder} />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="none">None</SelectItem>
          {groups.map((group) => (
            <SelectItem key={group.id} value={group.id.toString()}>
              {group.name} ({group.device_count} {group.device_count === 1 ? "device" : "devices"})
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      <Button
        type="button"
        variant="ghost"
        size="sm"
        onClick={handleAddNewGroup}
        className="text-purple-600 hover:text-purple-700 hover:bg-purple-50 dark:hover:bg-purple-900/20 h-auto py-1 px-2 text-xs"
      >
        <Plus className="mr-1 h-3 w-3" />
        Add New Group
      </Button>
    </div>
  )
}

