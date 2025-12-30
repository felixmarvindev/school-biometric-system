/**
 * Step Header Component
 * 
 * Displays an animated header for each step in a multi-step form.
 */

"use client"

import { motion, AnimatePresence } from "framer-motion"
import { CardTitle, CardDescription } from "@/components/ui/card"
import { LucideIcon } from "lucide-react"

interface StepHeaderProps {
  /** Current step number */
  step: number
  /** Step title */
  title: string
  /** Step description */
  description: string
  /** Icon component */
  icon: LucideIcon
  /** Icon background color class */
  iconBgColor?: string
  /** Icon color class */
  iconColor?: string
}

/**
 * Step Header Component
 */
export function StepHeader({
  step,
  title,
  description,
  icon: Icon,
  iconBgColor = "bg-blue-100",
  iconColor = "text-blue-600",
}: StepHeaderProps) {
  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={`step-${step}-header`}
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: 20 }}
        className="text-center"
      >
        <div className={`w-16 h-16 rounded-full ${iconBgColor} flex items-center justify-center mx-auto mb-4`}>
          <Icon className={`w-8 h-8 ${iconColor}`} />
        </div>
        <CardTitle className="text-2xl text-gray-900">{title}</CardTitle>
        <CardDescription className="text-base mt-2">{description}</CardDescription>
      </motion.div>
    </AnimatePresence>
  )
}

