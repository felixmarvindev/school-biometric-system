/**
 * Registration Success Screen Component
 * 
 * Displays a success message after successful registration.
 */

"use client"

import { motion } from "framer-motion"
import { Card, CardContent } from "@/components/ui/card"
import { School, User, CheckCircle2 } from "lucide-react"

interface RegistrationSuccessScreenProps {
  /** Registered school data */
  school: {
    id: number
    name: string
    code: string
  }
  /** Registered admin data */
  admin: {
    email: string
    first_name: string
    last_name: string
  }
  /** Redirect message */
  redirectMessage?: string
}

/**
 * Registration Success Screen Component
 */
export function RegistrationSuccessScreen({
  school,
  admin,
  redirectMessage = "Redirecting to dashboard in a few seconds...",
}: RegistrationSuccessScreenProps) {
  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
      >
        <Card className="w-full max-w-lg border-none shadow-2xl bg-white/80 backdrop-blur-sm">
          <CardContent className="pt-12 pb-12 text-center">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
              className="mb-6 flex justify-center"
            >
              <div className="w-20 h-20 rounded-full bg-emerald-100 flex items-center justify-center">
                <CheckCircle2 className="w-12 h-12 text-emerald-600" />
              </div>
            </motion.div>

            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="text-3xl font-bold mb-3 text-gray-900"
            >
              Registration Complete!
            </motion.h2>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="text-gray-600 mb-6 text-lg"
            >
              Your school and admin account have been successfully created.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="space-y-3 bg-blue-50 rounded-lg p-6 text-left"
            >
              <div className="flex items-start gap-3">
                <School className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="text-sm font-medium text-gray-700">School Name</p>
                  <p className="text-base font-semibold text-gray-900">{school.name}</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <User className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="text-sm font-medium text-gray-700">Admin Email</p>
                  <p className="text-base font-semibold text-gray-900">{admin.email}</p>
                </div>
              </div>
            </motion.div>

            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.6 }}
              className="text-sm text-gray-500 mt-6"
            >
              {redirectMessage}
            </motion.p>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}

