"use client"

import { Badge } from "@/components/ui/badge"
import { Wifi, WifiOff, Loader2 } from "lucide-react"
import { motion } from "framer-motion"

export interface DeviceStatusIndicatorProps {
  isConnected: boolean
  isConnecting: boolean
  error?: string | null
}

/**
 * WebSocket connection status indicator.
 * 
 * Shows the real-time connection status to device status updates.
 */
export function DeviceStatusIndicator({
  isConnected,
  isConnecting,
  error,
}: DeviceStatusIndicatorProps) {
  if (error) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="flex items-center gap-2"
      >
        <Badge variant="outline" className="bg-red-50 dark:bg-red-950/20 border-red-300 text-red-700 dark:text-red-400">
          <WifiOff className="mr-1 h-3 w-3" />
          Connection Error
        </Badge>
      </motion.div>
    )
  }

  if (isConnecting) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="flex items-center gap-2"
      >
        <Badge variant="outline" className="bg-yellow-50 dark:bg-yellow-950/20 border-yellow-300 text-yellow-700 dark:text-yellow-400">
          <Loader2 className="mr-1 h-3 w-3 animate-spin" />
          Connecting...
        </Badge>
      </motion.div>
    )
  }

  if (isConnected) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="flex items-center gap-2"
      >
        <Badge variant="outline" className="bg-green-50 dark:bg-green-950/20 border-green-300 text-green-700 dark:text-green-400">
          <Wifi className="mr-1 h-3 w-3" />
          Real-time
        </Badge>
      </motion.div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="flex items-center gap-2"
    >
      <Badge variant="outline" className="bg-gray-50 dark:bg-gray-950/20 border-gray-300 text-gray-700 dark:text-gray-400">
        <WifiOff className="mr-1 h-3 w-3" />
        Disconnected
      </Badge>
    </motion.div>
  )
}

