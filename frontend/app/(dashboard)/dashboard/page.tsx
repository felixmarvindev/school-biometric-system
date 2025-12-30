"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { motion } from "framer-motion"
import { Users, Smartphone, UserPlus } from "lucide-react"
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
import { CheckCircle2, Mail, Settings } from "lucide-react"
import type { UserResponse } from "@/lib/api/auth"

// Mock activity data (will be replaced with real data later)
const mockRecentActivity = [
  { type: "success" as const, message: "School registration completed successfully", time: "Just now", icon: CheckCircle2 },
  { type: "success" as const, message: "Admin account created and verified", time: "Just now", icon: CheckCircle2 },
  { type: "info" as const, message: "Welcome email sent to admin", time: "2 min ago", icon: Mail },
  { type: "info" as const, message: "System configuration initialized", time: "5 min ago", icon: Settings },
]

// Mock stats (will be replaced with real data later)
const mockStats = [
  { label: "Total Students", value: 0, icon: Users, colorClass: "bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400" },
  { label: "Registered Devices", value: 0, icon: Smartphone, colorClass: "bg-indigo-100 text-indigo-600 dark:bg-indigo-900/30 dark:text-indigo-400" },
  { label: "Enrollments", value: 0, icon: UserPlus, colorClass: "bg-violet-100 text-violet-600 dark:bg-violet-900/30 dark:text-violet-400" },
  { label: "Today's Attendance", value: 0, icon: Users, colorClass: "bg-emerald-100 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400" },
]

export default function DashboardPage() {
  const router = useRouter()
  const { token, setUser } = useAuthStore()
  const [isLoading, setIsLoading] = useState(true)
  const [school, setSchool] = useState<SchoolResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Fetch school data
  useEffect(() => {
    if (!token) return

    const fetchSchool = async () => {
      try {
        setIsLoading(true)
        const schoolData = await getMySchool(token)
        setSchool(schoolData)
        
        // Update user info from API response if available (user comes from token via API)
        if (schoolData.user) {
          setUser(schoolData.user as UserResponse)
        }
      } catch (err) {
        console.error("Failed to fetch school data:", err)
        setError("Failed to load school information")
      } finally {
        setIsLoading(false)
      }
    }

    fetchSchool()
  }, [token, setUser])

  const handleManageSchoolSettings = () => {
    router.push("/dashboard/settings")
  }

  // Get user info from store (layout handles authentication)
  const { user } = useAuthStore()
  const adminFirstName = user?.first_name || user?.email.split("@")[0] || ""

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
                  {mockStats.map((stat, index) => (
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
                <RecentActivityCard activities={mockRecentActivity} />
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

