"use client"

import { motion } from "framer-motion"
import { LucideIcon } from "lucide-react"

export interface ActivityItemProps {
  message: string
  time: string
  icon: LucideIcon
  type?: "success" | "info" | "warning" | "error"
  index?: number
}

export function ActivityItem({ message, time, icon: Icon, type = "info", index = 0 }: ActivityItemProps) {
  const colorClasses = {
    success: "bg-emerald-100 text-emerald-600",
    info: "bg-blue-100 text-blue-600",
    warning: "bg-yellow-100 text-yellow-600",
    error: "bg-red-100 text-red-600",
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.1, duration: 0.3 }}
      className="flex items-start gap-3 rounded-lg p-3 transition-colors hover:bg-muted/50"
    >
      <div className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-full ${colorClasses[type]}`}>
        <Icon className="h-4 w-4" />
      </div>
      <div className="min-w-0 flex-1">
        <p className="text-sm font-medium leading-tight text-foreground">{message}</p>
        <p className="mt-1 text-xs text-muted-foreground">{time}</p>
      </div>
    </motion.div>
  )
}

