"use client"

import { useState, useEffect } from "react"
import { useRouter, useParams } from "next/navigation"
import { motion } from "framer-motion"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { Alert, AlertDescription } from "@/components/ui/alert"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import {
  ArrowLeft,
  Edit,
  Trash2,
  Calendar,
  User,
  Phone,
  Mail,
  School,
  Loader2,
  AlertCircle,
} from "lucide-react"
import { fadeInUp, pageTransition } from "@/lib/animations/framer-motion"
import { useAuthStore } from "@/lib/store/authStore"
import {
  getStudent,
  deleteStudent,
  type StudentResponse,
  StudentApiError,
} from "@/lib/api/students"
import { formatDate, formatDateTime } from "@/lib/utils"

export default function StudentDetailPage() {
  const router = useRouter()
  const params = useParams()
  const studentId = params.id ? parseInt(params.id as string) : undefined
  const { token } = useAuthStore()
  const [student, setStudent] = useState<StudentResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)

  useEffect(() => {
    if (!token || !studentId) return

    const fetchStudent = async () => {
      try {
        setIsLoading(true)
        setError(null)
        const data = await getStudent(token, studentId)
        setStudent(data)
      } catch (err) {
        if (err instanceof StudentApiError) {
          setError(err.message)
        } else {
          setError("Failed to load student")
        }
      } finally {
        setIsLoading(false)
      }
    }

    fetchStudent()
  }, [token, studentId])

  const handleEdit = () => {
    router.push(`/dashboard/students/${studentId}/edit`)
  }

  const handleDelete = async () => {
    if (!token || !studentId) return

    try {
      setIsDeleting(true)
      await deleteStudent(token, studentId)
      router.push("/dashboard/students")
    } catch (err) {
      if (err instanceof StudentApiError) {
        setError(err.message)
      } else {
        setError("Failed to delete student")
      }
      setIsDeleting(false)
      setShowDeleteDialog(false)
    }
  }

  if (isLoading) {
    return (
      <motion.main
        variants={pageTransition}
        initial="initial"
        animate="animate"
        className="flex-1 space-y-6 p-4 sm:p-6 lg:p-8"
      >
        <div className="space-y-6">
          <Skeleton className="h-10 w-32" />
          <Card>
            <CardContent className="p-6 space-y-4">
              <Skeleton className="h-8 w-48" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
            </CardContent>
          </Card>
        </div>
      </motion.main>
    )
  }

  if (error || !student) {
    return (
      <motion.main
        variants={pageTransition}
        initial="initial"
        animate="animate"
        className="flex-1 space-y-6 p-4 sm:p-6 lg:p-8"
      >
        <div className="space-y-4">
          <Button
            variant="ghost"
            onClick={() => router.push("/dashboard/students")}
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Students
          </Button>
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              {error || "Student not found"}
            </AlertDescription>
          </Alert>
        </div>
      </motion.main>
    )
  }

  return (
    <motion.main
      variants={pageTransition}
      initial="initial"
      animate="animate"
      className="flex-1 space-y-6 p-4 sm:p-6 lg:p-8"
    >
      <div className="space-y-6">
        {/* Header with Actions */}
        <motion.div
          variants={fadeInUp}
          initial="hidden"
          animate="visible"
          className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between"
        >
          <Button
            variant="ghost"
            onClick={() => router.push("/dashboard/students")}
            className="text-muted-foreground hover:text-foreground"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Students
          </Button>
          <div className="flex gap-3">
            <Button
              variant="outline"
              onClick={handleEdit}
              className="border-blue-300 text-blue-700 hover:bg-blue-50 dark:hover:bg-blue-900/20"
            >
              <Edit className="mr-2 h-4 w-4" />
              Edit
            </Button>
            <Button
              variant="destructive"
              onClick={() => setShowDeleteDialog(true)}
              className="bg-red-600 hover:bg-red-700"
            >
              <Trash2 className="mr-2 h-4 w-4" />
              Delete
            </Button>
          </div>
        </motion.div>

        {/* Student Info Card */}
        <motion.div
          variants={fadeInUp}
          initial="hidden"
          animate="visible"
          transition={{ delay: 0.1 }}
        >
          <Card className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border border-gray-200/50 dark:border-gray-700/50">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <div className="flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-purple-500 text-white text-2xl font-bold">
                      {student.first_name[0]}{student.last_name[0]}
                    </div>
                    <div>
                      <CardTitle className="text-2xl font-bold">
                        {student.first_name} {student.last_name}
                      </CardTitle>
                      <Badge variant="outline" className="mt-2 font-mono">
                        {student.admission_number}
                      </Badge>
                    </div>
                  </div>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Personal Information */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-blue-700 dark:text-blue-400 flex items-center gap-2">
                  <User className="h-5 w-5" />
                  Personal Information
                </h3>
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">Full Name</p>
                    <p className="font-medium">
                      {student.first_name} {student.last_name}
                    </p>
                  </div>
                  {student.date_of_birth && (
                    <div>
                      <p className="text-sm text-muted-foreground mb-1 flex items-center gap-1">
                        <Calendar className="h-4 w-4" />
                        Date of Birth
                      </p>
                      <p className="font-medium">{formatDate(student.date_of_birth)}</p>
                    </div>
                  )}
                  {student.gender && (
                    <div>
                      <p className="text-sm text-muted-foreground mb-1">Gender</p>
                      <Badge variant="secondary" className="capitalize">
                        {student.gender}
                      </Badge>
                    </div>
                  )}
                </div>
              </div>

              {/* Academic Information */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-indigo-700 dark:text-indigo-400 flex items-center gap-2">
                  <School className="h-5 w-5" />
                  Academic Information
                </h3>
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  {student.class_id ? (
                    <div>
                      <p className="text-sm text-muted-foreground mb-1">Class</p>
                      <p className="font-medium">Form {student.class_id}</p>
                    </div>
                  ) : (
                    <div>
                      <p className="text-sm text-muted-foreground mb-1">Class</p>
                      <p className="text-muted-foreground">Not assigned</p>
                    </div>
                  )}
                  {student.stream_id ? (
                    <div>
                      <p className="text-sm text-muted-foreground mb-1">Stream</p>
                      <p className="font-medium">Stream {student.stream_id}</p>
                    </div>
                  ) : (
                    <div>
                      <p className="text-sm text-muted-foreground mb-1">Stream</p>
                      <p className="text-muted-foreground">Not assigned</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Parent/Guardian Contact */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-purple-700 dark:text-purple-400 flex items-center gap-2">
                  <Phone className="h-5 w-5" />
                  Parent/Guardian Contact
                </h3>
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  {student.parent_phone ? (
                    <div>
                      <p className="text-sm text-muted-foreground mb-1 flex items-center gap-1">
                        <Phone className="h-4 w-4" />
                        Phone Number
                      </p>
                      <a
                        href={`tel:${student.parent_phone}`}
                        className="font-medium text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
                      >
                        {student.parent_phone}
                      </a>
                    </div>
                  ) : (
                    <div>
                      <p className="text-sm text-muted-foreground mb-1">Phone Number</p>
                      <p className="text-muted-foreground">Not provided</p>
                    </div>
                  )}
                  {student.parent_email ? (
                    <div>
                      <p className="text-sm text-muted-foreground mb-1 flex items-center gap-1">
                        <Mail className="h-4 w-4" />
                        Email Address
                      </p>
                      <a
                        href={`mailto:${student.parent_email}`}
                        className="font-medium text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
                      >
                        {student.parent_email}
                      </a>
                    </div>
                  ) : (
                    <div>
                      <p className="text-sm text-muted-foreground mb-1">Email Address</p>
                      <p className="text-muted-foreground">Not provided</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Metadata */}
              <div className="pt-4 border-t border-gray-200/50 dark:border-gray-700/50">
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 text-sm text-muted-foreground">
                  <div>
                    <p>Created: {formatDateTime(student.created_at)}</p>
                  </div>
                  {student.updated_at && (
                    <div>
                      <p>Last Updated: {formatDateTime(student.updated_at)}</p>
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Delete Confirmation Dialog */}
      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Student</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete {student.first_name} {student.last_name}? This
              action will soft-delete the student (data will be preserved but marked as deleted).
              This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setShowDeleteDialog(false)}
              disabled={isDeleting}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDelete}
              disabled={isDeleting}
              className="bg-red-600 hover:bg-red-700"
            >
              {isDeleting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Deleting...
                </>
              ) : (
                "Delete Student"
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </motion.main>
  )
}

