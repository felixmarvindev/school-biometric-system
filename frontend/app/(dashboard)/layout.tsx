"use client"

import { useEffect, useState } from "react"
import { useRouter, usePathname } from "next/navigation"
import { motion } from "framer-motion"
import { SidebarProvider, SidebarInset } from "@/components/ui/sidebar"
import { TooltipProvider } from "@/components/ui/tooltip"
import { DashboardSidebar, DashboardHeader } from "@/components/features/dashboard"
import { useAuthStore } from "@/lib/store/authStore"

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const router = useRouter()
  const pathname = usePathname()
  const { token, user, logout, hasHydrated, setHasHydrated } = useAuthStore()
  const [title, setTitle] = useState("Dashboard")

  // Update page title based on route
  useEffect(() => {
    if (pathname === "/dashboard/settings") {
      setTitle("Settings")
    } else if (pathname === "/dashboard") {
      setTitle("Dashboard")
    } else if (pathname.startsWith("/dashboard/")) {
      // Extract title from pathname (e.g., "/dashboard/students" -> "Students")
      const segments = pathname.split("/").filter(Boolean)
      if (segments.length > 1) {
        const pageName = segments[segments.length - 1]
        setTitle(pageName.charAt(0).toUpperCase() + pageName.slice(1))
      }
    }
  }, [pathname])

  // Ensure hydration is marked as complete on client side
  useEffect(() => {
    if (typeof window !== 'undefined' && !hasHydrated) {
      const timer = setTimeout(() => {
        setHasHydrated(true)
      }, 100)
      return () => clearTimeout(timer)
    }
  }, [hasHydrated, setHasHydrated])

  // Wait for hydration before checking authentication
  useEffect(() => {
    if (!hasHydrated) {
      return
    }

    if (!token || !user) {
      router.push("/login")
      return
    }
  }, [hasHydrated, token, user, router])

  const handleLogout = () => {
    logout()
    router.push("/login")
  }

  const handleSettings = () => {
    router.push("/dashboard/settings")
  }

  // Show loading state while hydrating
  if (!hasHydrated) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-50 via-blue-50/50 to-indigo-50/30 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex flex-col items-center gap-4"
        >
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
            className="h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full"
          />
          <p className="text-sm text-muted-foreground">Loading...</p>
        </motion.div>
      </div>
    )
  }

  // Redirect if not authenticated (after hydration)
  if (!token || !user) {
    return null // Will redirect
  }

  // Get user info
  const adminFirstName = user.first_name || user.email.split("@")[0]
  const adminFullName = `${user.first_name} ${user.last_name}`.trim() || user.email

  return (
    <TooltipProvider>
      <SidebarProvider defaultOpen={true}>
        <div className="flex min-h-screen w-full bg-gradient-to-br from-slate-50 via-blue-50/50 to-indigo-50/30 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
          <DashboardSidebar
            adminName={adminFullName}
            adminEmail={user.email}
            adminAvatar={null}
            currentPath={pathname}
            onLogout={handleLogout}
            onSettings={handleSettings}
          />

          <SidebarInset>
            <DashboardHeader
              title={title}
              adminName={adminFullName}
              notificationCount={3}
              onLogout={handleLogout}
              onSettings={handleSettings}
            />

            {children}
          </SidebarInset>
        </div>
      </SidebarProvider>
    </TooltipProvider>
  )
}

