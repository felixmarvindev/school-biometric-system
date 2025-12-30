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

export interface StudentListFiltersProps {
  classFilter: number | null
  onClassFilterChange: (value: number | null) => void
  streamFilter: number | null
  onStreamFilterChange: (value: number | null) => void
  classes?: Array<{ id: number; name: string }>
  streams?: Array<{ id: number; name: string; class_id: number }>
}

export function StudentListFilters({
  classFilter,
  onClassFilterChange,
  streamFilter,
  onStreamFilterChange,
  classes = [],
  streams = [],
}: StudentListFiltersProps) {
  // Filter streams by selected class
  const availableStreams = classFilter
    ? streams.filter((s) => s.class_id === classFilter)
    : streams

  const hasFilters = classFilter || streamFilter

  return (
    <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
      <div className="flex-1 grid grid-cols-1 gap-3 sm:grid-cols-2">
        {/* Class Filter */}
        <Select
          value={classFilter?.toString() || "all"}
          onValueChange={(value) =>
            onClassFilterChange(value === "all" ? null : parseInt(value))
          }
        >
          <SelectTrigger className="border-gray-300 focus:border-blue-500 focus:ring-blue-500">
            <SelectValue placeholder="All Classes" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Classes</SelectItem>
            {classes.map((cls) => (
              <SelectItem key={cls.id} value={cls.id.toString()}>
                {cls.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        {/* Stream Filter */}
        <Select
          value={streamFilter?.toString() || "all"}
          onValueChange={(value) =>
            onStreamFilterChange(value === "all" ? null : parseInt(value))
          }
          disabled={!classFilter && streams.length > 0}
        >
          <SelectTrigger className="border-gray-300 focus:border-purple-500 focus:ring-purple-500">
            <SelectValue placeholder="All Streams" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Streams</SelectItem>
            {availableStreams.map((stream) => (
              <SelectItem key={stream.id} value={stream.id.toString()}>
                {stream.name}
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
            onClassFilterChange(null)
            onStreamFilterChange(null)
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

