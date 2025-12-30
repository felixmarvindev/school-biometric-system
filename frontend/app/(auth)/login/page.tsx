"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Mail, Lock, Eye, EyeOff, School, ArrowLeft, AlertCircle } from "lucide-react"
import Link from "next/link"
import { login, LoginError, type UserResponse } from "@/lib/api/auth"
import { useAuthStore } from "@/lib/store/authStore"
import { decodeJwtPayload } from "@/lib/utils/jwt"

export default function LoginPage() {
  const router = useRouter()
  const { login: setAuth } = useAuthStore()
  
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")

    // Basic validation
    if (!email || !password) {
      setError("Please fill in all fields")
      return
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setError("Please enter a valid email address")
      return
    }

    setIsLoading(true)

    try {
      // Call login API
      const tokenResponse = await login({ email, password })
      
      // Decode token to get user info (token is source of truth)
      const tokenPayload = decodeJwtPayload<{
        sub?: string;
        email?: string;
        first_name?: string;
        last_name?: string;
        school_id?: number;
        role?: string;
      }>(tokenResponse.access_token)
      
      // Create user object from token payload (token is source of truth)
      const user: UserResponse = {
        id: tokenPayload?.sub ? parseInt(tokenPayload.sub, 10) : 0,
        email: tokenPayload?.email || email,
        first_name: tokenPayload?.first_name || "",
        last_name: tokenPayload?.last_name || "",
        role: tokenPayload?.role || "school_admin",
        school_id: tokenPayload?.school_id || 0,
        is_active: true,
        is_deleted: false,
        created_at: new Date().toISOString(),
        updated_at: null,
      }
      
      // Store token and user info
      setAuth(tokenResponse.access_token, user)
      
      // Redirect to dashboard
      router.push("/dashboard")
    } catch (err: unknown) {
      setIsLoading(false)
      
      if (err instanceof LoginError) {
        setError(err.message)
      } else if (err instanceof Error) {
        setError(err.message)
      } else {
        setError("An unexpected error occurred. Please try again.")
      }
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 relative overflow-hidden">
      {/* Decorative gradient blobs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 0.6, scale: 1 }}
          transition={{ duration: 1, delay: 0.2 }}
          className="absolute top-1/4 -left-24 w-96 h-96 bg-gradient-to-br from-blue-300 to-indigo-400 rounded-full blur-3xl"
        />
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 0.5, scale: 1 }}
          transition={{ duration: 1, delay: 0.4 }}
          className="absolute bottom-1/4 -right-24 w-96 h-96 bg-gradient-to-br from-purple-300 to-pink-400 rounded-full blur-3xl"
        />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="w-full max-w-md relative z-10"
      >
        <Card className="shadow-2xl border-0 backdrop-blur-sm bg-white/95 dark:bg-gray-800/95">
          <CardHeader className="space-y-4 pb-6">
            {/* Logo/Icon */}
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", stiffness: 200, damping: 15, delay: 0.2 }}
              className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center mx-auto shadow-lg shadow-blue-500/30"
            >
              <School className="w-8 h-8 text-white" />
            </motion.div>

            {/* Header Text */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="text-center"
            >
              <CardTitle className="text-2xl text-gray-900 dark:text-gray-100">Sign in to your school</CardTitle>
              <CardDescription className="text-base mt-2">
                Access your dashboard to manage students and attendance
              </CardDescription>
            </motion.div>
          </CardHeader>

          <CardContent className="pb-8">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Error Alert */}
              {error && (
                <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
                  <Alert variant="destructive" className="border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-950/50">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                </motion.div>
              )}

              {/* Form Fields with Staggered Animation */}
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="space-y-2"
              >
                <Label htmlFor="email" className="text-gray-700 dark:text-gray-300">
                  Email Address
                </Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <Input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => {
                      setEmail(e.target.value)
                      setError("")
                    }}
                    placeholder="admin@school.edu"
                    className="pl-10"
                    aria-label="Email Address"
                    autoComplete="email"
                    disabled={isLoading}
                    required
                  />
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                className="space-y-2"
              >
                <Label htmlFor="password" className="text-gray-700 dark:text-gray-300">
                  Password
                </Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => {
                      setPassword(e.target.value)
                      setError("")
                    }}
                    placeholder="Enter your password"
                    className="pl-10 pr-10"
                    aria-label="Password"
                    autoComplete="current-password"
                    disabled={isLoading}
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
                    aria-label={showPassword ? "Hide password" : "Show password"}
                    disabled={isLoading}
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </motion.div>

              {/* Submit Button */}
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
                <Button
                  type="submit"
                  disabled={isLoading}
                  className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-lg shadow-blue-500/30 transition-all duration-300"
                  size="lg"
                >
                  {isLoading ? (
                    <div className="flex items-center justify-center">
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Number.POSITIVE_INFINITY, ease: "linear" }}
                        className="w-4 h-4 border-2 border-white border-t-transparent rounded-full mr-2"
                      />
                      Signing in...
                    </div>
                  ) : (
                    "Sign In"
                  )}
                </Button>
              </motion.div>

              {/* Secondary Links */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.7 }}
                className="space-y-3"
              >
                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-gray-200 dark:border-gray-700" />
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className="px-2 bg-white dark:bg-gray-800 text-gray-500">New to the system?</span>
                  </div>
                </div>

                <div className="flex flex-col gap-2">
                  <Link href="/register" className="w-full">
                    <Button
                      type="button"
                      variant="outline"
                      className="w-full border-blue-200 dark:border-blue-800 text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-950/50 hover:text-blue-700 dark:hover:text-blue-300 transition-colors bg-transparent"
                    >
                      Register your school
                    </Button>
                  </Link>
                  <Link href="/" className="w-full">
                    <Button
                      type="button"
                      variant="ghost"
                      className="w-full text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-800"
                    >
                      <ArrowLeft className="w-4 h-4 mr-2" />
                      Back to home
                    </Button>
                  </Link>
                </div>
              </motion.div>
            </form>
          </CardContent>
        </Card>

        {/* Footer Text */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="text-center text-sm text-gray-600 dark:text-gray-400 mt-6"
        >
          Secure biometric attendance system
        </motion.p>
      </motion.div>
    </div>
  )
}

