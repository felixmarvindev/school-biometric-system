"use client"

import { motion } from "framer-motion"
import { fadeInUp } from "@/lib/animations/framer-motion"
import { ClassManagement } from "@/components/features/classes/ClassManagement"

export default function ClassesPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Animated background shapes */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-400/20 rounded-full blur-3xl animate-pulse" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-400/20 rounded-full blur-3xl animate-pulse delay-1000" />
      </div>

      {/* Content */}
      <div className="relative z-10 container mx-auto px-4 py-8">
        <motion.header
          initial="hidden"
          animate="visible"
          variants={fadeInUp}
          className="mb-8"
        >
          <h1 className="text-3xl md:text-4xl font-bold mb-2 text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">
            Class Management
          </h1>
          <p className="text-muted-foreground">
            Create and manage classes and streams for organizing students.
          </p>
        </motion.header>

        <motion.main
          initial="hidden"
          animate="visible"
          variants={fadeInUp}
          transition={{ delay: 0.2 }}
        >
          <ClassManagement />
        </motion.main>
      </div>
    </div>
  )
}

