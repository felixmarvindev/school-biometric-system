/**
 * School Registration Form Component (Simple Version)
 * 
 * A reusable school registration form component with controlled inputs.
 * 
 * Features:
 * - Controlled inputs (no React Hook Form dependency)
 * - Required and optional field sections
 * - Field-level error handling
 * - Fully accessible
 */

"use client"

import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"

export interface SchoolRegistrationFormData {
  schoolName: string
  schoolCode: string
  address: string
  phone: string
  schoolEmail: string
}

export interface SchoolRegistrationFormErrors {
  schoolName?: string
  schoolCode?: string
  address?: string
  phone?: string
  schoolEmail?: string
}

interface SchoolRegistrationFormProps {
  /** Form data values */
  data: SchoolRegistrationFormData
  /** Callback when any field changes */
  onChange: (field: keyof SchoolRegistrationFormData, value: string) => void
  /** Field-level errors */
  errors?: SchoolRegistrationFormErrors
  /** Whether form is in loading state */
  isLoading?: boolean
  /** Custom class name */
  className?: string
}

/**
 * School Registration Form Component
 */
export function SchoolRegistrationFormSimple({
  data,
  onChange,
  errors = {},
  isLoading = false,
  className = "",
}: SchoolRegistrationFormProps) {
  return (
    <div className={`space-y-6 ${className}`}>
      {/* Required Fields */}
      <div className="space-y-4">
        <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">
          Required Information
        </h3>

        <div className="space-y-2">
          <Label htmlFor="schoolName" className="text-gray-700">
            School Name <span className="text-red-500">*</span>
          </Label>
          <Input
            id="schoolName"
            value={data.schoolName}
            onChange={(e) => onChange("schoolName", e.target.value)}
            placeholder="e.g., Greenfield Academy"
            className={errors.schoolName ? "border-red-500" : ""}
            disabled={isLoading}
            aria-required="true"
            aria-invalid={!!errors.schoolName}
          />
          {errors.schoolName && <p className="text-sm text-red-500">{errors.schoolName}</p>}
        </div>

        <div className="space-y-2">
          <Label htmlFor="schoolCode" className="text-gray-700">
            School Code <span className="text-red-500">*</span>
          </Label>
          <Input
            id="schoolCode"
            value={data.schoolCode}
            onChange={(e) => onChange("schoolCode", e.target.value.toUpperCase())}
            placeholder="e.g., GFA-001"
            className={errors.schoolCode ? "border-red-500" : ""}
            disabled={isLoading}
            aria-required="true"
            aria-invalid={!!errors.schoolCode}
          />
          {errors.schoolCode && <p className="text-sm text-red-500">{errors.schoolCode}</p>}
        </div>
      </div>

      {/* Optional Fields */}
      <div className="space-y-4 pt-4 border-t">
        <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">
          Optional Information
        </h3>

        <div className="space-y-2">
          <Label htmlFor="address" className="text-gray-700">
            Address
          </Label>
          <Textarea
            id="address"
            value={data.address}
            onChange={(e) => onChange("address", e.target.value)}
            placeholder="e.g., 123 Main Street, Nairobi, Kenya"
            rows={3}
            disabled={isLoading}
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="phone" className="text-gray-700">
              Phone Number
            </Label>
            <Input
              id="phone"
              type="tel"
              value={data.phone}
              onChange={(e) => onChange("phone", e.target.value)}
              placeholder="e.g., +254712345678"
              disabled={isLoading}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="schoolEmail" className="text-gray-700">
              Email Address
            </Label>
            <Input
              id="schoolEmail"
              type="email"
              value={data.schoolEmail}
              onChange={(e) => onChange("schoolEmail", e.target.value)}
              placeholder="e.g., admin@school.ac.ke"
              disabled={isLoading}
            />
          </div>
        </div>
      </div>
    </div>
  )
}

