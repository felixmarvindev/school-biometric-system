"use client"

import { motion } from "framer-motion"
import { TableCell, TableRow } from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { staggerItem } from "@/lib/animations/framer-motion"
import { type DeviceGroupResponse } from "@/lib/api/device_groups"
import { Edit, Trash2, Users } from "lucide-react"

export interface DeviceGroupTableRowProps {
  group: DeviceGroupResponse
  onGroupClick: (id: number) => void
  onEdit: (id: number) => void
  onDelete: (id: number) => void
}

/**
 * Device group table row component.
 */
export function DeviceGroupTableRow({
  group,
  onGroupClick,
  onEdit,
  onDelete,
}: DeviceGroupTableRowProps) {
  return (
    <motion.tr
      variants={staggerItem}
      initial="hidden"
      animate="visible"
      className="border-gray-200/50 dark:border-gray-700/50 hover:bg-gray-50/50 dark:hover:bg-gray-800/50 transition-colors"
    >
      <TableCell className="font-medium cursor-pointer" onClick={() => onGroupClick(group.id)}>
        {group.name}
      </TableCell>
      <TableCell className="text-muted-foreground cursor-pointer" onClick={() => onGroupClick(group.id)}>
        {group.description || "—"}
      </TableCell>
      <TableCell className="cursor-pointer" onClick={() => onGroupClick(group.id)}>
        <Badge variant="secondary" className="bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400">
          <Users className="mr-1 h-3 w-3" />
          {group.device_count} {group.device_count === 1 ? "device" : "devices"}
        </Badge>
      </TableCell>
      <TableCell>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={(e) => {
              e.stopPropagation()
              onEdit(group.id)
            }}
            className="border-blue-300 text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-950/20"
          >
            <Edit className="mr-2 h-3 w-3" />
            Edit
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={(e) => {
              e.stopPropagation()
              onDelete(group.id)
            }}
            className="border-red-300 text-red-600 hover:bg-red-50 dark:hover:bg-red-950/20"
          >
            <Trash2 className="mr-2 h-3 w-3" />
            Delete
          </Button>
        </div>
      </TableCell>
    </motion.tr>
  )
}

