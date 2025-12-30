"use client"

import { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { AlertCircle, CheckCircle2, Loader2, Lock, School } from "lucide-react"
import { useAuthStore } from "@/lib/store/authStore"
import { getMySchool, updateMySchool, type SchoolResponse, type SchoolUpdateData, SchoolRegistrationError } from "@/lib/api/schools"
import { fadeInUp, staggerContainer } from "@/lib/animations/framer-motion"

// Animation variants
const pageVariants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.4, ease: "easeOut" } },
}

const alertVariants = {
  initial: { opacity: 0, y: -10, scale: 0.95 },
  animate: { opacity: 1, y: 0, scale: 1, transition: { duration: 0.3, ease: "easeOut" } },
  exit: { opacity: 0, y: -10, scale: 0.95, transition: { duration: 0.2 } },
}

// Form field component with animation
function FormField({
  children,
  index,
}: {
  children: React.ReactNode
  index: number
}) {
  return (
    <motion.div variants={fadeInUp} initial="initial" animate="animate" transition={{ delay: index * 0.06 }}>
      {children}
    </motion.div>
  )
}

export default function SettingsPage() {
  const { token } = useAuthStore()
  const [isLoading, setIsLoading] = useState(true)
  const [school, setSchool] = useState<SchoolResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Form state
  const [formData, setFormData] = useState<SchoolUpdateData>({
    name: "",
    address: null,
    phone: null,
    email: null,
  })
  const [originalData, setOriginalData] = useState<SchoolUpdateData>(formData)
  const [isSaving, setIsSaving] = useState(false)
  const [showSuccess, setShowSuccess] = useState(false)
  const [showError, setShowError] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})

  // Fetch school data
  useEffect(() => {
    if (!token) return

    const fetchSchool = async () => {
      try {
        setIsLoading(true)
        const schoolData = await getMySchool(token)
        setSchool(schoolData)
        
        // Initialize form data
        const initialData: SchoolUpdateData = {
          name: schoolData.name,
          address: schoolData.address || null,
          phone: schoolData.phone || null,
          email: schoolData.email || null,
        }
        setFormData(initialData)
        setOriginalData(initialData)
      } catch (err) {
        console.error("Failed to fetch school data:", err)
        setError("Failed to load school information")
      } finally {
        setIsLoading(false)
      }
    }

    fetchSchool()
  }, [token])

  const handleInputChange = (field: keyof SchoolUpdateData, value: string | null) => {
    setFormData((prev) => ({ ...prev, [field]: value || null }))
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: "" }))
    }
    // Hide alerts when form changes
    setShowSuccess(false)
    setShowError(false)
  }

  const validateForm = () => {
    const newErrors: Record<string, string> = {}
    if (!formData.name?.trim()) {
      newErrors.name = "School name is required"
    }
    if (formData.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = "Please enter a valid email address"
    }
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSave = async () => {
    if (!validateForm() || !token || !school) return

    setIsSaving(true)
    setShowSuccess(false)
    setShowError(false)
    setErrors({})

    try {
      const updateData: SchoolUpdateData = {
        name: formData.name,
        address: formData.address || null,
        phone: formData.phone || null,
        email: formData.email || null,
      }

      const updatedSchool = await updateMySchool(token, updateData)
      setSchool(updatedSchool)
      
      // Update original data to reflect saved state
      setOriginalData({
        name: updatedSchool.name,
        address: updatedSchool.address || null,
        phone: updatedSchool.phone || null,
        email: updatedSchool.email || null,
      })
      
      setShowSuccess(true)
      
      // Hide success message after 5 seconds
      setTimeout(() => {
        setShowSuccess(false)
      }, 5000)
    } catch (err) {
      console.error("Failed to update school:", err)
      
      if (err instanceof SchoolRegistrationError) {
        if (err.fieldErrors) {
          setErrors(err.fieldErrors)
        }
        setShowError(true)
        setError(err.message)
      } else {
        setShowError(true)
        setError("Failed to update school information. Please try again.")
      }
    } finally {
      setIsSaving(false)
    }
  }

  const handleCancel = () => {
    setFormData(originalData)
    setErrors({})
    setShowSuccess(false)
    setShowError(false)
  }

  const hasChanges = JSON.stringify(formData) !== JSON.stringify(originalData)

  if (isLoading) {
    return (
      <div className="flex min-h-[400px] items-center justify-center">
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
          <p className="text-sm text-muted-foreground">Loading school information...</p>
        </motion.div>
      </div>
    )
  }

  return (
      <motion.main
        variants={pageVariants}
        initial="initial"
        animate="animate"
        className="flex-1 p-4 sm:p-6 lg:p-8"
      >
        <div className="mx-auto max-w-2xl space-y-6">
          {/* Page Header */}
          <motion.div variants={fadeInUp} className="space-y-1">
            <h2 className="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">School Settings</h2>
            <p className="text-muted-foreground">Manage your school's basic information and configuration</p>
          </motion.div>

          {/* Alerts */}
          <AnimatePresence mode="wait">
            {showSuccess && (
              <motion.div key="success" variants={alertVariants} initial="initial" animate="animate" exit="exit">
                <Alert className="border-emerald-200 bg-emerald-50 text-emerald-800 dark:border-emerald-800 dark:bg-emerald-950/50 dark:text-emerald-200">
                  <CheckCircle2 className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
                  <AlertTitle className="text-emerald-800 dark:text-emerald-200">Success</AlertTitle>
                  <AlertDescription className="text-emerald-700 dark:text-emerald-300">
                    School information updated successfully.
                  </AlertDescription>
                </Alert>
              </motion.div>
            )}

            {showError && (
              <motion.div key="error" variants={alertVariants} initial="initial" animate="animate" exit="exit">
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertTitle>Something went wrong</AlertTitle>
                  <AlertDescription>
                    {error || "We couldn't save your changes. Please try again."}
                  </AlertDescription>
                </Alert>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Settings Form Card */}
          {school && (
            <motion.div variants={staggerContainer} initial="initial" animate="animate">
              <Card className="border-none shadow-sm">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-lg">
                    <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10">
                      <School className="h-4 w-4 text-primary" />
                    </div>
                    School Information
                  </CardTitle>
                  <CardDescription>
                    Update your school's profile details. Some fields cannot be changed.
                  </CardDescription>
                </CardHeader>

                <CardContent className="space-y-6">
                  {/* School Name */}
                  <FormField index={0}>
                    <div className="space-y-2">
                      <Label htmlFor="school-name" className="text-sm font-medium">
                        School Name <span className="text-destructive">*</span>
                      </Label>
                      <Input
                        id="school-name"
                        value={formData.name || ""}
                        onChange={(e) => handleInputChange("name", e.target.value)}
                        disabled={isSaving}
                        placeholder="Enter school name"
                        className={errors.name ? "border-destructive focus-visible:ring-destructive" : ""}
                      />
                      {errors.name && <p className="text-sm text-destructive">{errors.name}</p>}
                    </div>
                  </FormField>

                  {/* School Code (Read-only) */}
                  <FormField index={1}>
                    <div className="space-y-2">
                      <Label htmlFor="school-code" className="flex items-center gap-2 text-sm font-medium">
                        School Code
                        <Badge variant="secondary" className="text-xs font-normal">
                          <Lock className="mr-1 h-3 w-3" />
                          Read-only
                        </Badge>
                      </Label>
                      <Input
                        id="school-code"
                        value={school.code}
                        disabled
                        className="bg-muted/50 text-muted-foreground"
                      />
                      <p className="text-xs text-muted-foreground">
                        School code is assigned during registration and cannot be changed.
                      </p>
                    </div>
                  </FormField>

                  <Separator />

                  {/* Two-column layout for contact info on larger screens */}
                  <div className="grid gap-6 sm:grid-cols-2">
                    {/* Phone */}
                    <FormField index={2}>
                      <div className="space-y-2">
                        <Label htmlFor="phone" className="text-sm font-medium">
                          Phone Number
                        </Label>
                        <Input
                          id="phone"
                          type="tel"
                          value={formData.phone || ""}
                          onChange={(e) => handleInputChange("phone", e.target.value || null)}
                          disabled={isSaving}
                          placeholder="+254712345678"
                        />
                      </div>
                    </FormField>

                    {/* Email */}
                    <FormField index={3}>
                      <div className="space-y-2">
                        <Label htmlFor="email" className="text-sm font-medium">
                          Email Address
                        </Label>
                        <Input
                          id="email"
                          type="email"
                          value={formData.email || ""}
                          onChange={(e) => handleInputChange("email", e.target.value || null)}
                          disabled={isSaving}
                          placeholder="contact@school.edu"
                          className={errors.email ? "border-destructive focus-visible:ring-destructive" : ""}
                        />
                        {errors.email && <p className="text-sm text-destructive">{errors.email}</p>}
                      </div>
                    </FormField>
                  </div>

                  {/* Address */}
                  <FormField index={4}>
                    <div className="space-y-2">
                      <Label htmlFor="address" className="text-sm font-medium">
                        Address
                      </Label>
                      <Textarea
                        id="address"
                        value={formData.address || ""}
                        onChange={(e) => handleInputChange("address", e.target.value || null)}
                        disabled={isSaving}
                        placeholder="Enter school address"
                        rows={3}
                        className="resize-none"
                      />
                    </div>
                  </FormField>
                </CardContent>

                <CardFooter className="flex flex-col-reverse gap-3 border-t bg-muted/20 px-6 py-4 sm:flex-row sm:justify-end">
                  <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                    <Button
                      variant="outline"
                      onClick={handleCancel}
                      disabled={isSaving || !hasChanges}
                      className="w-full sm:w-auto bg-transparent"
                    >
                      Cancel
                    </Button>
                  </motion.div>
                  <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                    <Button onClick={handleSave} disabled={isSaving || !hasChanges} className="w-full sm:w-auto">
                      {isSaving ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Saving...
                        </>
                      ) : (
                        "Save Changes"
                      )}
                    </Button>
                  </motion.div>
                </CardFooter>
              </Card>
            </motion.div>
          )}
        </div>
      </motion.main>
  )
}

