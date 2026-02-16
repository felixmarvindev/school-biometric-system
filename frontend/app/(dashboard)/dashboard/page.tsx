"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { motion } from "framer-motion"
import { Users, Smartphone, UserPlus, Clock3 } from "lucide-react"
import { staggerContainer } from "@/lib/animations/framer-motion"
import {
  StatCard,
  ActionCard,
  StatsSkeleton,
  WelcomeBanner,
  SchoolInfoCard,
  RecentActivityCard,
} from "@/components/features/dashboard"
import { useAuthStore } from "@/lib/store/authStore"
import { getMySchool, type SchoolResponse } from "@/lib/api/schools"
import { listStudents } from "@/lib/api/students"
import { listDevices } from "@/lib/api/devices"
import { getAttendanceStats } from "@/lib/api/attendance"
import { getSuccessfulEnrollmentCount } from "@/lib/api/enrollment"
import type { UserResponse } from "@/lib/api/auth"

// Placeholder activity data (to be replaced with live logs later)
const placeholderRecentActivity = [
  { type: "info" as const, message: "No attendance activity yet", time: "Pending implementation", icon: Clock3 },
  { type: "info" as const, message: "No enrollment activity yet", time: "Pending implementation", icon: Clock3 },
  { type: "info" as const, message: "Recent activity feed will appear here", time: "Pending implementation", icon: Clock3 },
]

interface DashboardStats {
  totalStudents: number
  registeredDevices: number
  enrollments: number
  todaysAttendance: number
}

const DEFAULT_STATS: DashboardStats = {
  totalStudents: 0,
  registeredDevices: 0,
  enrollments: 0,
  todaysAttendance: 0,
}

export default function DashboardPage() {
  const router = useRouter()
  const { token, setUser } = useAuthStore()
  const [isLoading, setIsLoading] = useState(true)
  const [school, setSchool] = useState<SchoolResponse | null>(null)
  const [stats, setStats] = useState<DashboardStats>(DEFAULT_STATS)
  const [error, setError] = useState<string | null>(null)

  // Fetch school data
  useEffect(() => {
    if (!token) return

    const fetchDashboardStats = async (): Promise<DashboardStats> => {
      const [studentsResponse, devicesFirstPage, attendanceResponse, successfulEnrollments] = await Promise.all([
        listStudents(token, { page: 1, page_size: 1 }),
        listDevices(token, { page: 1, page_size: 1 }),
        getAttendanceStats(token),
        getSuccessfulEnrollmentCount(token),
      ])

      return {
        totalStudents: studentsResponse.total,
        registeredDevices: devicesFirstPage.total,
        enrollments: successfulEnrollments,
        todaysAttendance: attendanceResponse.total_events,
      }
    }

    const fetchDashboardData = async () => {
      try {
        setIsLoading(true)
        setError(null)

        const [schoolResult, statsResult] = await Promise.allSettled([
          getMySchool(token),
          fetchDashboardStats(),
        ])

        if (schoolResult.status === "fulfilled") {
          setSchool(schoolResult.value)

          // Update user info from API response if available (user comes from token via API)
          if (schoolResult.value.user) {
            setUser(schoolResult.value.user as UserResponse)
          }
        } else {
          console.error("Failed to fetch school data:", schoolResult.reason)
          setError("Failed to load school information")
        }

        if (statsResult.status === "fulfilled") {
          setStats(statsResult.value)
        } else {
          console.error("Failed to fetch dashboard stats:", statsResult.reason)
        }
      } catch (err) {
        console.error("Failed to fetch dashboard data:", err)
        setError("Failed to load dashboard")
      } finally {
        setIsLoading(false)
      }
    }

    fetchDashboardData()
  }, [token, setUser])

  const handleManageSchoolSettings = () => {
    router.push("/dashboard/settings")
  }

  // Get user info from store (layout handles authentication)
  const { user } = useAuthStore()
  const adminFirstName = user?.first_name || user?.email.split("@")[0] || ""
  const dashboardStats = [
    {
      label: "Total Students",
      value: stats.totalStudents,
      icon: Users,
      colorClass: "bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400",
    },
    {
      label: "Registered Devices",
      value: stats.registeredDevices,
      icon: Smartphone,
      colorClass: "bg-indigo-100 text-indigo-600 dark:bg-indigo-900/30 dark:text-indigo-400",
    },
    {
      label: "Enrollments",
      value: stats.enrollments,
      icon: UserPlus,
      colorClass: "bg-purple-100 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400",
    },
    {
      label: "Today's Attendance",
      value: stats.todaysAttendance,
      icon: Users,
      colorClass: "bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400",
    },
  ]

  return (
    <motion.main
              initial={{ opacity: 0, scale: 0.98 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.4, ease: "easeOut" }}
              className="flex-1 space-y-6 p-4 sm:p-6 lg:p-8"
            >
              {/* Welcome Banner */}
              <WelcomeBanner
                schoolCode={school?.code || "N/A"}
                adminFirstName={adminFirstName}
                isSetupComplete={!!school}
              />

              {/* Stats Grid */}
              {isLoading ? (
                <StatsSkeleton />
              ) : (
                <motion.div
                  variants={staggerContainer}
                  initial="hidden"
                  animate="visible"
                  className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4"
                >
                  {dashboardStats.map((stat, index) => (
                    <StatCard key={stat.label} {...stat} index={index} />
                  ))}
                </motion.div>
              )}

              {/* Two Column Layout */}
              <motion.div
                variants={staggerContainer}
                initial="hidden"
                animate="visible"
                className="grid grid-cols-1 gap-6 lg:grid-cols-2"
              >
                {/* School Overview */}
                {school && (
                  <SchoolInfoCard
                    name={school.name}
                    code={school.code}
                    address={school.address || undefined}
                    phone={school.phone || undefined}
                    email={school.email || undefined}
                    onManageSettings={handleManageSchoolSettings}
                  />
                )}

                {/* Recent Activity */}
                <RecentActivityCard activities={placeholderRecentActivity} />
              </motion.div>

              {/* Action Cards */}
              <motion.div
                variants={staggerContainer}
                initial="hidden"
                animate="visible"
                className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3"
              >
                <ActionCard
                  icon={Users}
                  title="Add Your First Student"
                  description="Start building your student directory by adding student profiles with their information."
                  buttonText="Add Student"
                  colorClass="bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400"
                  onAction={() => router.push("/dashboard/students")}
                  index={0}
                />
                <ActionCard
                  icon={Smartphone}
                  title="Register a Device"
                  description="Connect biometric devices to enable seamless attendance tracking across your school."
                  buttonText="Register Device"
                  colorClass="bg-indigo-100 text-indigo-600 dark:bg-indigo-900/30 dark:text-indigo-400"
                  onAction={() => router.push("/dashboard/devices")}
                  index={1}
                />
                <ActionCard
                  icon={UserPlus}
                  title="Begin Enrollment"
                  description="Enroll students with biometric data for quick and accurate attendance recording."
                  buttonText="Start Enrollment"
                  colorClass="bg-violet-100 text-violet-600 dark:bg-violet-900/30 dark:text-violet-400"
                  onAction={() => router.push("/dashboard/enrollment")}
                  index={2}
                />
              </motion.div>
            </motion.main>
  )
}

