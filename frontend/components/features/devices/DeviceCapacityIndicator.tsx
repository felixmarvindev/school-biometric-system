"use client"

import { motion } from "framer-motion"
import { AlertTriangle, CheckCircle2 } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { fadeInUp } from "@/lib/animations"

export interface DeviceCapacityIndicatorProps {
  /** Maximum number of users the device can hold (null if unknown) */
  maxUsers: number | null
  /** Current number of enrolled users */
  enrolledUsers: number
  /** Optional: show compact version */
  compact?: boolean
}

/**
 * Component to display device capacity with progress bar and warnings.
 */
export function DeviceCapacityIndicator({
  maxUsers,
  enrolledUsers,
  compact = false,
}: DeviceCapacityIndicatorProps) {
  // If max users is not set or zero, show unknown state
  if (!maxUsers || maxUsers === 0) {
    return (
      <motion.div
        variants={fadeInUp}
        initial="hidden"
        animate="visible"
        className="flex items-center gap-2"
      >
        <Badge variant="outline" className="text-xs text-muted-foreground">
          Unknown capacity
        </Badge>
      </motion.div>
    )
  }

  const percentage = Math.min(100, (enrolledUsers / maxUsers) * 100)
  const available = maxUsers - enrolledUsers
  const isWarning = percentage >= 80 && percentage < 95
  const isCritical = percentage >= 95 && percentage < 100
  const isFull = percentage >= 100

  // Color classes based on capacity
  const progressBarClass = isFull
    ? "bg-red-500"
    : isCritical
    ? "bg-red-400"
    : isWarning
    ? "bg-yellow-500"
    : "bg-green-500"

  const textColorClass = isFull
    ? "text-red-600 dark:text-red-400"
    : isCritical
    ? "text-red-600 dark:text-red-400"
    : isWarning
    ? "text-yellow-600 dark:text-yellow-400"
    : "text-muted-foreground"

  if (compact) {
    return (
      <motion.div
        variants={fadeInUp}
        initial="hidden"
        animate="visible"
        className="flex items-center gap-2 min-w-[120px]"
      >
        <div className="flex-1 relative h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
          <motion.div
            className={`h-full ${progressBarClass} transition-colors duration-300`}
            initial={{ width: 0 }}
            animate={{ width: `${percentage}%` }}
            transition={{ duration: 0.5, ease: "easeOut" }}
          />
        </div>
        <span className={`text-xs font-medium whitespace-nowrap ${textColorClass}`}>
          {enrolledUsers}/{maxUsers}
        </span>
        {isFull && (
          <Badge variant="destructive" className="text-xs px-1.5 py-0">
            Full
          </Badge>
        )}
        {isCritical && !isFull && (
          <Badge variant="destructive" className="text-xs px-1.5 py-0">
            Critical
          </Badge>
        )}
        {isWarning && !isCritical && !isFull && (
          <Badge className="text-xs px-1.5 py-0 bg-yellow-500 text-yellow-900 border-yellow-600">
            Warning
          </Badge>
        )}
      </motion.div>
    )
  }

  return (
    <motion.div
      variants={fadeInUp}
      initial="hidden"
      animate="visible"
      className="space-y-2"
    >
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-foreground">Capacity</span>
          {isFull && (
            <Badge variant="destructive" className="text-xs">
              <AlertTriangle className="mr-1 h-3 w-3" />
              Full
            </Badge>
          )}
          {isCritical && !isFull && (
            <Badge variant="destructive" className="text-xs">
              <AlertTriangle className="mr-1 h-3 w-3" />
              Critical
            </Badge>
          )}
          {isWarning && !isCritical && !isFull && (
            <Badge className="text-xs bg-yellow-500 text-yellow-900 border-yellow-600">
              <AlertTriangle className="mr-1 h-3 w-3" />
              Warning
            </Badge>
          )}
        </div>
        <span className={`text-sm font-semibold ${textColorClass}`}>
          {enrolledUsers} / {maxUsers}
        </span>
      </div>

      <div className="relative h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
        <motion.div
          className={`h-full ${progressBarClass} transition-colors duration-300`}
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.5, ease: "easeOut" }}
        />
      </div>

      <div className="flex items-center justify-between text-xs text-muted-foreground">
        <span>{percentage.toFixed(1)}% used</span>
        {available >= 0 && (
          <span className="flex items-center gap-1">
            {available > 0 ? (
              <>
                <CheckCircle2 className="h-3 w-3 text-green-500" />
                {available} available
              </>
            ) : (
              <>
                <AlertTriangle className="h-3 w-3 text-red-500" />
                No slots available
              </>
            )}
          </span>
        )}
      </div>
    </motion.div>
  )
}

