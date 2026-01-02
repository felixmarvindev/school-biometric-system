"use client"

import { useRouter } from "next/navigation"
import { motion } from "framer-motion"
import { fadeInUp } from "@/lib/animations/framer-motion"
import { DeviceForm } from "@/components/features/devices/DeviceForm"
import { useAuthStore } from "@/lib/store/authStore"
import { createDevice, DeviceApiError } from "@/lib/api/devices"
import { type DeviceFormData } from "@/lib/validations/device"

export default function NewDevicePage() {
  const router = useRouter()
  const { token } = useAuthStore()

  const handleSubmit = async (data: DeviceFormData) => {
    if (!token) {
      throw new Error("Authentication required")
    }

    await createDevice(token, data)
    router.push("/dashboard/devices")
  }

  const handleCancel = () => {
    router.push("/dashboard/devices")
  }

  if (!token) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
        <div className="relative z-10 container mx-auto px-4 py-8">
          <p className="text-muted-foreground">Please log in to continue.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Animated background shapes */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-400/20 rounded-full blur-3xl animate-pulse" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-400/20 rounded-full blur-3xl animate-pulse delay-1000" />
      </div>

      {/* Content */}
      <div className="relative z-10 container mx-auto px-4 py-8 max-w-3xl">
        <motion.header
          initial="hidden"
          animate="visible"
          variants={fadeInUp}
          className="mb-8"
        >
          <h1 className="text-3xl md:text-4xl font-bold mb-2 text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">
            Register New Device
          </h1>
          <p className="text-muted-foreground">
            Add a new biometric device to your school.
          </p>
        </motion.header>

        <motion.main
          initial="hidden"
          animate="visible"
          variants={fadeInUp}
          transition={{ delay: 0.2 }}
        >
          <DeviceForm
            onSubmit={handleSubmit}
            onCancel={handleCancel}
            token={token}
          />
        </motion.main>
      </div>
    </div>
  )
}

