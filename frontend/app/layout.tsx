/**
 * Root layout - ensures axios interceptors are initialized.
 * This file must import the axios instance to set up global interceptors.
 */

import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { Toaster } from "@/components/ui/sonner"

// Import axios instance to initialize global interceptors
import "@/lib/api/axios-instance"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "School Biometric Management System",
  description: "Automated fingerprint-based attendance tracking for schools",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        {children}
        <Toaster />
      </body>
    </html>
  )
}
