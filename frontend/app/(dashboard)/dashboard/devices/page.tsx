"use client"

import { useState, useEffect, useCallback } from "react"
import { useRouter } from "next/navigation"
import { motion } from "framer-motion"
import { fadeInUp } from "@/lib/animations/framer-motion"
import { DeviceList } from "@/components/features/devices/DeviceList"
import { useAuthStore } from "@/lib/store/authStore"
import {
  listDevices,
  testDeviceConnection,
  type DeviceStatus,
  DeviceApiError,
} from "@/lib/api/devices"
import { useDebounce } from "@/lib/hooks/useDebounce"

export default function DevicesPage() {
  const router = useRouter()
  const { token } = useAuthStore()
  const [devices, setDevices] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [pageSize] = useState(50)
  const [totalPages, setTotalPages] = useState(1)
  const [total, setTotal] = useState(0)
  const [search, setSearch] = useState("")
  const [statusFilter, setStatusFilter] = useState<DeviceStatus | null>(null)
  const [deviceGroupFilter, setDeviceGroupFilter] = useState<number | null>(null)
  const [isTestingConnection, setIsTestingConnection] = useState(false)

  // Debounce search to avoid too many API calls
  const debouncedSearch = useDebounce(search, 300)

  const fetchDevices = useCallback(async () => {
    if (!token) {
      setIsLoading(false)
      return
    }

    try {
      setIsLoading(true)
      setError(null)

      const result = await listDevices(token, {
        page,
        page_size: pageSize,
        search: debouncedSearch || undefined,
        status: statusFilter || undefined,
        device_group_id: deviceGroupFilter || undefined,
      })

      setDevices(result.items)
      setTotal(result.total)
      setTotalPages(result.pages)
    } catch (err) {
      if (err instanceof DeviceApiError) {
        setError(err.message)
      } else {
        setError("Failed to load devices. Please try again.")
      }
    } finally {
      setIsLoading(false)
    }
  }, [token, page, pageSize, debouncedSearch, statusFilter, deviceGroupFilter])

  useEffect(() => {
    fetchDevices()
  }, [fetchDevices])

  const handleTestConnection = async (deviceId: number) => {
    if (!token) return

    setIsTestingConnection(true)
    try {
      await testDeviceConnection(token, deviceId)
      // Refresh devices to show updated status
      await fetchDevices()
    } catch (err) {
      if (err instanceof DeviceApiError) {
        setError(err.message)
      } else {
        setError("Connection test failed. Please try again.")
      }
    } finally {
      setIsTestingConnection(false)
    }
  }

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
            Device Management
          </h1>
          <p className="text-muted-foreground">
            Register and monitor biometric devices for student attendance tracking.
          </p>
        </motion.header>

        <motion.main
          initial="hidden"
          animate="visible"
          variants={fadeInUp}
          transition={{ delay: 0.2 }}
        >
          <DeviceList
            devices={devices}
            isLoading={isLoading}
            error={error}
            search={search}
            onSearchChange={setSearch}
            statusFilter={statusFilter}
            onStatusFilterChange={setStatusFilter}
            deviceGroupFilter={deviceGroupFilter}
            onDeviceGroupFilterChange={setDeviceGroupFilter}
            page={page}
            totalPages={totalPages}
            total={total}
            onPageChange={setPage}
            onAddDevice={() => router.push("/dashboard/devices/new")}
            onDeviceClick={(id) => router.push(`/dashboard/devices/${id}/edit`)}
            onTestConnection={handleTestConnection}
            isTestingConnection={isTestingConnection}
            deviceGroups={[]} // TODO: Load device groups when Phase 2 is implemented
          />
        </motion.main>
      </div>
    </div>
  )
}

