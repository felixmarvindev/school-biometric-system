/**
 * Admin Account Form Component (Simple Version)
 * 
 * A reusable, independent admin account form component that can be used
 * in registration flows or standalone admin creation.
 * 
 * Features:
 * - Controlled inputs (no React Hook Form dependency)
 * - Password strength indicator
 * - Password visibility toggle
 * - Field-level error handling
 * - Fully accessible
 */

"use client"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { Eye, EyeOff } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Alert, AlertDescription } from "@/components/ui/alert"

export interface AdminAccountFormData {
  firstName: string
  lastName: string
  email: string
  password: string
  confirmPassword: string
}

export interface AdminAccountFormErrors {
  firstName?: string
  lastName?: string
  email?: string
  password?: string
  confirmPassword?: string
}

interface AdminAccountFormProps {
  /** Form data values */
  data: AdminAccountFormData
  /** Callback when any field changes */
  onChange: (field: keyof AdminAccountFormData, value: string) => void
  /** Field-level errors */
  errors?: AdminAccountFormErrors
  /** General error message */
  generalError?: string | null
  /** Whether form is in loading state */
  isLoading?: boolean
  /** Show password strength indicator */
  showPasswordStrength?: boolean
  /** Custom class name */
  className?: string
}

/**
 * Calculate password strength (0-100)
 */
function getPasswordStrength(password: string) {
  if (!password) return { strength: 0, label: "", color: "bg-gray-300" }
  
  let strength = 0
  if (password.length >= 8) strength++
  if (password.length >= 12) strength++
  if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++
  if (/\d/.test(password)) strength++
  if (/[^a-zA-Z0-9]/.test(password)) strength++

  const labels = ["Weak", "Fair", "Good", "Strong", "Very Strong"]
  const colors = ["bg-red-500", "bg-orange-500", "bg-yellow-500", "bg-lime-500", "bg-emerald-500"]

  return {
    strength: (strength / 5) * 100,
    label: labels[strength - 1] || "",
    color: colors[strength - 1] || "bg-gray-300",
  }
}

/**
 * Admin Account Form Component
 */
export function AdminAccountFormSimple({
  data,
  onChange,
  errors = {},
  generalError = null,
  isLoading = false,
  showPasswordStrength = true,
  className = "",
}: AdminAccountFormProps) {
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)

  const passwordStrength = getPasswordStrength(data.password)

  return (
    <div className={`space-y-6 ${className}`}>

      {/* First Name and Last Name */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="firstName" className="text-gray-700">
            First Name <span className="text-red-500">*</span>
          </Label>
          <Input
            id="firstName"
            value={data.firstName}
            onChange={(e) => onChange("firstName", e.target.value)}
            placeholder="e.g., John"
            className={errors.firstName ? "border-red-500" : ""}
            disabled={isLoading}
            aria-required="true"
            aria-invalid={!!errors.firstName}
          />
          {errors.firstName && <p className="text-sm text-red-500">{errors.firstName}</p>}
        </div>

        <div className="space-y-2">
          <Label htmlFor="lastName" className="text-gray-700">
            Last Name <span className="text-red-500">*</span>
          </Label>
          <Input
            id="lastName"
            value={data.lastName}
            onChange={(e) => onChange("lastName", e.target.value)}
            placeholder="e.g., Doe"
            className={errors.lastName ? "border-red-500" : ""}
            disabled={isLoading}
            aria-required="true"
            aria-invalid={!!errors.lastName}
          />
          {errors.lastName && <p className="text-sm text-red-500">{errors.lastName}</p>}
        </div>
      </div>

      {/* Email */}
      <div className="space-y-2">
        <Label htmlFor="email" className="text-gray-700">
          Email Address <span className="text-red-500">*</span>
        </Label>
        <Input
          id="email"
          type="email"
          value={data.email}
          onChange={(e) => onChange("email", e.target.value)}
          placeholder="e.g., admin@school.ac.ke"
          className={errors.email ? "border-red-500" : ""}
          disabled={isLoading}
          aria-required="true"
          aria-invalid={!!errors.email}
        />
        {errors.email && <p className="text-sm text-red-500">{errors.email}</p>}
      </div>

      {/* Password */}
      <div className="space-y-2">
        <Label htmlFor="password" className="text-gray-700">
          Password <span className="text-red-500">*</span>
        </Label>
        <div className="relative">
          <Input
            id="password"
            type={showPassword ? "text" : "password"}
            value={data.password}
            onChange={(e) => onChange("password", e.target.value)}
            placeholder="Enter a strong password (min. 8 characters)"
            className={errors.password ? "border-red-500 pr-10" : "pr-10"}
            disabled={isLoading}
            aria-required="true"
            aria-invalid={!!errors.password}
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
            aria-label={showPassword ? "Hide password" : "Show password"}
            disabled={isLoading}
          >
            {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </button>
        </div>
        {errors.password && <p className="text-sm text-red-500">{errors.password}</p>}

        {/* Password Strength Indicator */}
        {showPasswordStrength && data.password && (
          <div className="space-y-2 mt-3">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Password strength</span>
              <span
                className={`font-medium ${
                  passwordStrength.strength >= 80
                    ? "text-emerald-600"
                    : passwordStrength.strength >= 60
                      ? "text-lime-600"
                      : passwordStrength.strength >= 40
                        ? "text-yellow-600"
                        : "text-orange-600"
                }`}
              >
                {passwordStrength.label}
              </span>
            </div>
            <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${passwordStrength.strength}%` }}
                transition={{ duration: 0.3 }}
                className={`h-full ${passwordStrength.color}`}
              />
            </div>
          </div>
        )}
      </div>

      {/* Confirm Password */}
      <div className="space-y-2">
        <Label htmlFor="confirmPassword" className="text-gray-700">
          Confirm Password <span className="text-red-500">*</span>
        </Label>
        <div className="relative">
          <Input
            id="confirmPassword"
            type={showConfirmPassword ? "text" : "password"}
            value={data.confirmPassword}
            onChange={(e) => onChange("confirmPassword", e.target.value)}
            placeholder="Re-enter your password to confirm"
            className={errors.confirmPassword ? "border-red-500 pr-10" : "pr-10"}
            disabled={isLoading}
            aria-required="true"
            aria-invalid={!!errors.confirmPassword}
          />
          <button
            type="button"
            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
            aria-label={showConfirmPassword ? "Hide password" : "Show password"}
            disabled={isLoading}
          >
            {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </button>
        </div>
        {errors.confirmPassword && <p className="text-sm text-red-500">{errors.confirmPassword}</p>}
      </div>
    </div>
  )
}

