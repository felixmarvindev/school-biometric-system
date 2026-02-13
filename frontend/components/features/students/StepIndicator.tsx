"use client"

import { motion } from "framer-motion"
import { Check } from "lucide-react"
import { cn } from "@/lib/utils"
import type { LucideIcon } from "lucide-react"

export interface StepDef {
  id: number
  name: string
  icon: LucideIcon
  description: string
  optional?: boolean
}

interface StepIndicatorProps {
  steps: StepDef[]
  currentStep: number
}

export function StepIndicator({ steps, currentStep }: StepIndicatorProps) {
  return (
    <nav aria-label="Progress" className="w-full">
      <ol className="flex items-center">
        {steps.map((step, idx) => {
          const status =
            step.id < currentStep
              ? "completed"
              : step.id === currentStep
                ? "active"
                : "pending"
          const isLast = idx === steps.length - 1

          return (
            <li key={step.id} className="flex items-center flex-1 last:flex-none">
              <div className="flex flex-col items-center gap-1.5 relative">
                <motion.div
                  initial={false}
                  animate={{
                    scale: status === "active" ? 1.1 : 1,
                  }}
                  className={cn(
                    "flex items-center justify-center size-10 rounded-full border-2 transition-colors duration-300 relative z-10",
                    status === "completed" &&
                      "bg-blue-600 border-blue-600 text-white",
                    status === "active" &&
                      "border-blue-600 bg-blue-50 text-blue-600 shadow-md shadow-blue-500/20 dark:bg-blue-900/30 dark:text-blue-400",
                    status === "pending" &&
                      "border-gray-300 bg-gray-100 text-gray-400 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-500"
                  )}
                >
                  {status === "completed" ? (
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ type: "spring", stiffness: 300, damping: 20 }}
                    >
                      <Check className="size-4 stroke-[3]" />
                    </motion.div>
                  ) : (
                    <step.icon className="size-4" />
                  )}
                </motion.div>
                <span
                  className={cn(
                    "text-[11px] font-medium text-center leading-tight max-w-[70px]",
                    status === "active" && "text-blue-600 dark:text-blue-400 font-semibold",
                    status === "completed" && "text-foreground",
                    status === "pending" && "text-muted-foreground"
                  )}
                >
                  {step.name}
                </span>
              </div>

              {!isLast && (
                <div className="flex-1 h-0.5 mx-2 mb-5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-blue-600 rounded-full"
                    initial={false}
                    animate={{
                      width: status === "completed" ? "100%" : "0%",
                    }}
                    transition={{ duration: 0.4, ease: "easeInOut" }}
                  />
                </div>
              )}
            </li>
          )
        })}
      </ol>
    </nav>
  )
}
